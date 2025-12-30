import datetime
from Model.Analysis.Analyzer import Analyzer
from Model.Analysis.MovingAverageConvergenceDivergenceCrossoverVisualizer import MovingAverageConvergenceDivergenceCrossoverVisualizer
from Model.AnalysisResult import AnalysisResult
from Model.Indicators.AverageCalculator import AverageCalculator
from Model.Indicators.MovingAverageConvergenceDivergenceCalculator import MovingAverageConvergenceDivergenceCalculator
from Model.Signals.MovingAverageConvergenceDivergenceCrossoverSignalDetector import MovingAverageConvergenceDivergenceCrossoverSignalDetector
from Model.Signals.TradingSignal import TradingSignal


class MovingAverageConvergenceDivergenceCrossoverAnalyzer(Analyzer):
    
    def __init__(
        self,
        amountInvestedPerTrade: int,
        movingAverageConvergenceDivergenceCalculator: MovingAverageConvergenceDivergenceCalculator,
        signalDetector: MovingAverageConvergenceDivergenceCrossoverSignalDetector,
        visualizer: MovingAverageConvergenceDivergenceCrossoverVisualizer | None):
        
        super().__init__(amountInvestedPerTrade)
        
        self.movingAverageConvergenceDivergenceCalculator = movingAverageConvergenceDivergenceCalculator
        self.signalDetector = signalDetector
        self.visualizer = visualizer        
    
    def analyze(self, tickerSymbol: str, dates: list[datetime.date], sourceData: list[float], rawSignals: bool = False) -> AnalysisResult | list[TradingSignal]:
        
        movingAverageConvergenceDivergenceData = self.movingAverageConvergenceDivergenceCalculator.calculate(sourceData)
        
        signals = self.signalDetector.detect(dates, sourceData, movingAverageConvergenceDivergenceData)
        
        if rawSignals:
            return signals
        
        result = self.simulate(signals)
        
        if self.visualizer:
            self.visualizer.visualize(dates, sourceData, movingAverageConvergenceDivergenceData, result.actionedSignals)
        
        return result