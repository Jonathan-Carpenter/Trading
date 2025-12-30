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
        analyzers: list[Analyzer],
        visualizer: CompositeVisualizer | None):
        
        super().__init__(amountInvestedPerTrade)
        
        self.windowSize = windowSize
        self.scoreThreshold = scoreThreshold
        self.confidenceRatioThreshold = confidenceRatioThreshold
        self.analyzers = analyzers
        self.visualizer = visualizer
        
        self.id = uuid.uuid4()
        self.signalCountWeighting = 1 / (self.windowSize + len(self.analyzers))
      
    def analyze(self, dates: list[datetime.date], sourceData: list[float], rawSignals: bool = False) -> AnalysisResult | list[TradingSignal]:
        
        signals: list[TradingSignal] = []
        
        for analyzer in self.analyzers:
            newSignals = analyzer.analyze(dates, sourceData, True)
            signals += newSignals
            
        compositeSignals: list[TradingSignal] = []
            
        for i in range(len(dates)):
            
            relevantSignals = [s for s in signals if s.date < dates[i] and (dates[i] - s.date).days < self.windowSize]
            
            buyScore = 0
            sellScore = 0
            
            for signal in relevantSignals:
                
                daysAgo = dates[i] - signal.date
                recencyWeighting = 1 / (1 + daysAgo.days)
                
                # TODO: Consider supporting a separate weighting for each signal source -> e.g. prefer more certain indicators? That would assume that they have different levels of "noise" in their signals.
                signalEffect = self.signalCountWeighting * recencyWeighting * 100 # multiplying by 100 just makes scores easier to read when logging
                
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
            self.visualizer.visualize(dates, sourceData, signals, result.actionedSignals)
        
        return result