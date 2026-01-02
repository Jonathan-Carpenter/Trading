import datetime
import uuid
from Model.Analysis.CompositeVisualizer import CompositeVisualizer
from Model.Analysis.WeightedAnalyzerConfiguration import WeightedAnalyzerConfiguration
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
        threshold: float,
        analyzerConfigurations: list[WeightedAnalyzerConfiguration],
        visualizer: CompositeVisualizer | None):
        
        super().__init__(amountInvestedPerTrade)
        self.windowSize = windowSize
        self.threshold = threshold
        self.analyzerConfigurations = analyzerConfigurations
        self.visualizer = visualizer
        
        self.id = uuid.uuid4()
        self.smoothing = 2 / (self.windowSize + 1)
        self.totalAnalyzerWeights = sum([c.weighting for c in self.analyzerConfigurations])
      
    def analyze(self, tickerSymbol: str, dates: list[datetime.date], sourceData: list[float], rawSignals: bool = False) -> AnalysisResult | list[TradingSignal]:
        
        if self.totalAnalyzerWeights == 0:
            return AnalysisResult(0, [])
        
        length = len(dates)
        dateIndices: dict[datetime.date, int] = {}
        
        for i in range(length):
            dateIndices[dates[i]] = i
                
        allSignals = []
                
        buyScores = [1] * length
        sellScores = [1] * length
        
        for analyzerConfiguration in self.analyzerConfigurations:
            
            analyzerWeighting = analyzerConfiguration.weighting / self.totalAnalyzerWeights
            
            signals = analyzerConfiguration.analyzer.analyze(tickerSymbol, dates, sourceData, True)
            signalsOverDates: list[TradingSignal | None] = [None] * length
            
            allSignals += signals
            
            for signal in signals:
                index = dateIndices[signal.date]
                signalsOverDates[index] = signal
            
            windowStart = 0
            windowEnd = analyzerConfiguration.windowSize
                
            while windowEnd < length:
                
                windowSignals = [s for s in signalsOverDates[windowStart:windowEnd]]
                
                for signal in windowSignals:
                    
                    if signal is None:
                        continue
                    
                    daysAgo = dates[windowEnd] - signal.date
                    recencyWeighting = analyzerConfiguration.windowSize / (1 + daysAgo.days)
                    
                    signalEffect = (1 / (1 + recencyWeighting)) * analyzerWeighting
                    
                    if isinstance(signal, BuySignal):
                        buyScores[windowEnd] += signalEffect
                        
                    if isinstance(signal, SellSignal):
                        sellScores[windowEnd] += signalEffect
                        
                windowStart += 1
                windowEnd += 1
        
        compositeStrengthIndexData = [0] * length
        
        windowStart = 0
        windowEnd = self.windowSize
        
        while windowEnd < length:
            
            windowBuyScores = buyScores[windowStart:windowEnd]
            windowSellScores = sellScores[windowStart:windowEnd]
            
            avgBuyScore = 1 + (sum(windowBuyScores) / self.windowSize)
            avgSellScore = 1 + (sum(windowSellScores) / self.windowSize)
            
            # abs(Ratio) guaranteed to be > 1, so scale back this calculation by 1, otherwise the index jumps between -1 and +1
            windowCompositeStrengthIndex = (avgBuyScore / avgSellScore) - 1 if avgBuyScore > avgSellScore else (-avgSellScore / avgBuyScore) + 1
            windowSmoothedCompositeStrengthIndex = (self.smoothing * windowCompositeStrengthIndex) + ((1 - self.smoothing) * compositeStrengthIndexData[windowEnd - 1])
            
            compositeStrengthIndexData[windowEnd] = windowSmoothedCompositeStrengthIndex
            
            windowStart += 1
            windowEnd += 1
        
        compositeSignals: list[TradingSignal] = []
        
        previousAboveUpperThreshold = False
        previousBelowLowerThreshold = False
        
        for i in range(length):
            
            if (compositeStrengthIndexData[i] > self.threshold) and (not previousAboveUpperThreshold):
                buySignal = BuySignal(sourceData[i], dates[i], self.id)
                compositeSignals.append(buySignal)
                
                previousAboveUpperThreshold = True
                
            if (compositeStrengthIndexData[i] < -self.threshold) and (not previousBelowLowerThreshold):
                sellSignal = SellSignal(sourceData[i], dates[i], self.id)
                compositeSignals.append(sellSignal)
                
                previousBelowLowerThreshold = True
                
            if compositeStrengthIndexData[i] < self.threshold:
                previousAboveUpperThreshold = False
                
            if compositeStrengthIndexData[i] > -self.threshold:
                previousBelowLowerThreshold = False
        
        if rawSignals:
            return compositeSignals
        
        result = self.simulate(compositeSignals)
        
        if self.visualizer:
            self.visualizer.visualize(dates, sourceData, allSignals, result.actionedSignals, compositeStrengthIndexData)
        
        return result