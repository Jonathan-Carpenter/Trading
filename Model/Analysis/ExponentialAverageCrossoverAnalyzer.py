import datetime
from Model.Analysis.Analyzer import Analyzer
from Model.Indicators.AverageCalculator import AverageCalculator
from Model.Signals.ExponentialAverageCrossoverSignalDetector import ExponentialAverageCrossoverSignalDetector
from Model.AnalysisResult import AnalysisResult
from Model.Analysis.ExponentialAverageCrossoverVisualizer import ExponentialAverageCrossoverVisualizer
from Model.Signals.TradingSignal import TradingSignal

class ExponentialAverageCrossoverAnalyzer(Analyzer):
    
    def __init__(
        self,
        amountInvestedPerTrade: int,
        shortTermAverageCalculator: AverageCalculator,
        longTermAverageCalculator: AverageCalculator,
        signalDetector: ExponentialAverageCrossoverSignalDetector,
        visualizer: ExponentialAverageCrossoverVisualizer | None):
        
        super().__init__(amountInvestedPerTrade)
        
        self.shortTermAverageCalculator = shortTermAverageCalculator
        self.longTermAverageCalculator = longTermAverageCalculator
        self.signalDetector = signalDetector
        self.visualizer = visualizer        
    
    def analyze(self, dates: list[datetime.date], sourceData: list[float], rawSignals: bool = False) -> AnalysisResult | list[TradingSignal]:
        
        shortTermAverageData = self.shortTermAverageCalculator.calculate(sourceData).data
        longTermAverageData = self.longTermAverageCalculator.calculate(sourceData).data
        
        signals = self.signalDetector.detect(dates, sourceData, shortTermAverageData, longTermAverageData)
        
        if rawSignals:
            return signals
        
        result = self.simulate(signals)
        
        if self.visualizer:
            self.visualizer.visualize(dates, sourceData, shortTermAverageData, longTermAverageData, result.actionedSignals)
        
        return result