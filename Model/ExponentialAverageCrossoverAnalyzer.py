from Model.Analyzer import Analyzer
from Model.Indicators.AverageCalculator import AverageCalculator
from Model.ExponentialAverageCrossoverSignalDetector import ExponentialAverageCrossoverSignalDetector
from Model.AnalysisResult import AnalysisResult
from Model.ExponentialAverageCrossoverVisualizer import ExponentialAverageCrossoverVisualizer

class ExponentialAverageCrossoverAnalyzer(Analyzer):
    
    def __init__(
        self,
        amountInvestedPerTrade: int,
        shortTermAverageCalculator: AverageCalculator,
        longTermAverageCalculator: AverageCalculator,
        signalDetector: ExponentialAverageCrossoverSignalDetector,
        visualizer: ExponentialAverageCrossoverVisualizer):
        
        super().__init__(amountInvestedPerTrade)
        
        self.shortTermAverageCalculator = shortTermAverageCalculator
        self.longTermAverageCalculator = longTermAverageCalculator
        self.signalDetector = signalDetector
        self.visualizer = visualizer
    
    def analyze(self, dates, sourceData) -> AnalysisResult:
        shortTermAverageData = self.shortTermAverageCalculator.calculate(sourceData).data
        longTermAverageData = self.longTermAverageCalculator.calculate(sourceData).data
        
        signals = self.signalDetector.detect(dates, sourceData, shortTermAverageData, longTermAverageData)
        
        result = self.simulate(signals)
        
        if self.visualizer:
            self.visualizer.visualize(dates, sourceData, shortTermAverageData, longTermAverageData, signals)
        
        return result