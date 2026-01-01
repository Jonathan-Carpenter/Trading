import datetime
import uuid
from Model.Analysis.CompositeVisualizer import CompositeVisualizer
from Model.AnalysisResult import AnalysisResult
from Model.Analysis.Analyzer import Analyzer
from Model.Signals.TradingSignal import TradingSignal
from Model.Signals.BuySignal import BuySignal
from Model.Signals.SellSignal import SellSignal

class CompositeAnalyzer(Analyzer):
    
    def __init__(
        self,
        amountInvestedPerTrade: int,
        windowSize: int,
        analyzersWithWeightings: list[(Analyzer, int)],
        visualizer: CompositeVisualizer | None):
        
        super().__init__(amountInvestedPerTrade)
        
        self.windowSize = windowSize
        self.analyzersWithWeightings = analyzersWithWeightings
        self.visualizer = visualizer
        
        self.id = uuid.uuid4()
        self.smoothing = 2 / (self.windowSize + 1)
        self.totalAnalyzerWeights = sum([weighting for (_, weighting) in self.analyzersWithWeightings])
      
    def analyze(self, tickerSymbol: str, dates: list[datetime.date], sourceData: list[float], rawSignals: bool = False) -> AnalysisResult | list[TradingSignal]:
        
        if self.totalAnalyzerWeights == 0:
            return AnalysisResult(0, [])
        
        length = len(dates)
        dateIndices: dict[datetime.date, int] = {}
        
        for i in range(length):
            dateIndices[dates[i]] = i
            
        signalsWithWeightings: list[list[(TradingSignal, int)]] = [None] * length
        
        for i in range(length):
            signalsWithWeightings[i] = []
        
        for (analyzer, weighting) in self.analyzersWithWeightings:
            newSignals: list[TradingSignal] = analyzer.analyze(tickerSymbol, dates, sourceData, True)
            
            for signal in newSignals:
                index = dateIndices[signal.date]                
                signalsWithWeightings[index].append((signal, weighting))
                
        compositeStrengthIndexData = [0] * length
        
        windowStart = 0
        windowEnd = self.windowSize
            
        while windowEnd < length:
            
            windowSignals = [s for signalsList in signalsWithWeightings[windowStart:windowEnd] for s in signalsList]
            
            buyScore = 1
            sellScore = 1
            
            for (signal, weighting) in windowSignals:
                
                daysAgo = dates[windowEnd] - signal.date
                recencyWeighting = 2 / (1 + daysAgo.days)
                analyzerWeighting = weighting / self.totalAnalyzerWeights
                
                signalEffect = (recencyWeighting * analyzerWeighting) / self.windowSize
                
                if isinstance(signal, BuySignal):
                    buyScore += signalEffect
                    
                if isinstance(signal, SellSignal):
                    sellScore += signalEffect
            
            windowCompositeStrengthIndex = buyScore / sellScore if buyScore > sellScore else -sellScore / buyScore
            windowSmoothedCompositeStrengthIndex = (self.smoothing * windowCompositeStrengthIndex) + ((1 - self.smoothing) * compositeStrengthIndexData[windowEnd - 1])
            
            compositeStrengthIndexData[windowEnd] = windowSmoothedCompositeStrengthIndex
            
            windowStart += 1
            windowEnd += 1
        
        compositeSignals: list[TradingSignal] = []
        
        previousAboveUpperThreshold = False
        previousBelowLowerThreshold = False
        threshold = 0.4
        
        for i in range(length):
            
            if (compositeStrengthIndexData[i] > threshold) and (not previousAboveUpperThreshold):
                buySignal = BuySignal(sourceData[i], dates[i], self.id)
                compositeSignals.append(buySignal)
                
                previousAboveUpperThreshold = True
                
            if (compositeStrengthIndexData[i] < -threshold) and (not previousBelowLowerThreshold):
                sellSignal = SellSignal(sourceData[i], dates[i], self.id)
                compositeSignals.append(sellSignal)
                
                previousBelowLowerThreshold = True
                
            if compositeStrengthIndexData[i] < threshold:
                previousAboveUpperThreshold = False
                
            if compositeStrengthIndexData[i] > -threshold:
                previousBelowLowerThreshold = False
        
        if rawSignals:
            return compositeSignals
        
        result = self.simulate(compositeSignals)
        
        if self.visualizer:
            self.visualizer.visualize(dates, sourceData, [s for ss in signalsWithWeightings for (s, _) in ss], result.actionedSignals, compositeStrengthIndexData)
        
        return result