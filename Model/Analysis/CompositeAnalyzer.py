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
        scoreThreshold: float,
        confidenceRatioThreshold: float,
        analyzersWithWeightings: list[(Analyzer, int)],
        visualizer: CompositeVisualizer | None):
        
        super().__init__(amountInvestedPerTrade)
        
        self.windowSize = windowSize
        self.scoreThreshold = scoreThreshold
        self.confidenceRatioThreshold = confidenceRatioThreshold
        self.analyzersWithWeightings = analyzersWithWeightings
        self.visualizer = visualizer
        
        self.id = uuid.uuid4()
        self.windowSizeWeighting = 1 / self.windowSize
        self.totalAnalyzerWeights = sum([weighting for (_, weighting) in self.analyzersWithWeightings])
      
    def analyze(self, tickerSymbol: str, dates: list[datetime.date], sourceData: list[float], rawSignals: bool = False) -> AnalysisResult | list[TradingSignal]:
        
        if self.totalAnalyzerWeights == 0:
            return AnalysisResult(0, [])
        
        signalsWithWeightings: list[(TradingSignal, int)] = []
        
        for (analyzer, weighting) in self.analyzersWithWeightings:
            newSignals = analyzer.analyze(tickerSymbol, dates, sourceData, True)
            signalsWithWeightings += [(s, weighting) for s in newSignals]
            
        compositeSignals: list[TradingSignal] = []
            
        for i in range(len(dates)):
            
            relevantSignals = [s for s in signalsWithWeightings if s[0].date < dates[i] and (dates[i] - s[0].date).days < self.windowSize]
            
            buyScore = 0
            sellScore = 0
            
            for (signal, weighting) in relevantSignals:
                
                daysAgo = dates[i] - signal.date
                recencyWeighting = 1 / (1 + daysAgo.days)
                analyzerWeighting = weighting / self.totalAnalyzerWeights
                
                signalEffect = self.windowSizeWeighting * recencyWeighting * analyzerWeighting * 100 # multiplying by 100 just makes scores easier to read when logging
                
                if isinstance(signal, BuySignal):
                    buyScore += signalEffect
                    
                if isinstance(signal, SellSignal):
                    sellScore += signalEffect
                    
            # print(f"Buy={buyScore:3f}; Sell={sellScore:3f}")
            
            if (buyScore > self.scoreThreshold) and (buyScore > sellScore * self.confidenceRatioThreshold):
                compositeSignals.append(BuySignal(sourceData[i], dates[i], self.id))
                
            if (sellScore > self.scoreThreshold) and (sellScore > buyScore * self.confidenceRatioThreshold):
                compositeSignals.append(SellSignal(sourceData[i], dates[i], self.id))
        
        if rawSignals:
            return compositeSignals
        
        result = self.simulate(compositeSignals)
        
        if self.visualizer:
            self.visualizer.visualize(dates, sourceData, [s for (s, _) in signalsWithWeightings], result.actionedSignals)
        
        return result