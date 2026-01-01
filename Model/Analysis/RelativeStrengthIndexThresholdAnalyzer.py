import datetime
from Model.Analysis.BollingerBandCrossoverVisualizer import BollingerBandCrossoverVisualizer
from Model.Analysis.RelativeStrengthIndexThresholdVisualizer import RelativeStrengthIndexThresholdVisualizer
from Model.AnalysisResult import AnalysisResult
from Model.Analysis.Analyzer import Analyzer
from Model.Indicators.RelativeStrengthIndexCalculator import RelativeStrengthIndexCalculator
from Model.Signals.BollingerBandCrossoverSignalDetector import BollingerBandCrossoverSignalDetector
from Model.Signals.RelativeStrengthIndexThresholdSignalDetector import RelativeStrengthIndexThresholdSignalDetector
from Model.Signals.TradingSignal import TradingSignal


class RelativeStrengthIndexThresholdAnalyzer(Analyzer):
    
    def __init__(
        self,
        amountInvestedPerTrade: int,
        relativeStrengthIndexCalculator: RelativeStrengthIndexCalculator,
        relativeStrengthIndexThresholdSignalDetector: RelativeStrengthIndexThresholdSignalDetector,
        relativeStrengthIndexThresholdVisualizer: RelativeStrengthIndexThresholdVisualizer | None):
        
        super().__init__(amountInvestedPerTrade)
        
        self.relativeStrengthIndexCalculator = relativeStrengthIndexCalculator
        self.relativeStrengthIndexThresholdSignalDetector = relativeStrengthIndexThresholdSignalDetector
        self.relativeStrengthIndexThresholdVisualizer = relativeStrengthIndexThresholdVisualizer
        
    def analyze(self, tickerSymbol: str, dates: list[datetime.date], sourceData: list[float], rawSignals: bool = False) -> AnalysisResult | list[TradingSignal]:
        
        relativeStrengthIndexData = self.relativeStrengthIndexCalculator.calculate(sourceData)
        signals = self.relativeStrengthIndexThresholdSignalDetector.detect(dates, sourceData, relativeStrengthIndexData)
        
        if rawSignals:
            return signals
        
        result = self.simulate(signals)
        
        if self.relativeStrengthIndexThresholdVisualizer:
            self.relativeStrengthIndexThresholdVisualizer.visualize(dates, sourceData, relativeStrengthIndexData, result.actionedSignals)
        
        return result