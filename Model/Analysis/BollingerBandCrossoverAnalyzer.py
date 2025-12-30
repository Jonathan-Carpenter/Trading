import datetime
from Model.Analysis.BollingerBandCrossoverVisualizer import BollingerBandCrossoverVisualizer
from Model.AnalysisResult import AnalysisResult
from Model.Analysis.Analyzer import Analyzer
from Model.Indicators.BollingerBandsCalculator import BollingerBandsCalculator
from Model.Signals.BollingerBandCrossoverSignalDetector import BollingerBandCrossoverSignalDetector
from Model.Signals.TradingSignal import TradingSignal


class BollingerBandCrossoverAnalyzer(Analyzer):
    
    def __init__(
        self,
        amountInvestedPerTrade: int,
        bollingerCalculator: BollingerBandsCalculator,
        bollingerSignalDetector: BollingerBandCrossoverSignalDetector,
        bollingerVisualizer: BollingerBandCrossoverVisualizer | None):
        
        super().__init__(amountInvestedPerTrade)
        
        self.bollingerCalculator = bollingerCalculator
        self.bollingSignalDetector = bollingerSignalDetector
        self.bollingerVisualizer = bollingerVisualizer
        
    def analyze(self, tickerSymbol: str, dates: list[datetime.date], sourceData: list[float], rawSignals: bool = False) -> AnalysisResult | list[TradingSignal]:
        bollingerData = self.bollingerCalculator.calculate(sourceData)
        signals = self.bollingSignalDetector.detect(dates, sourceData, bollingerData)
        
        if rawSignals:
            return signals
        
        result = self.simulate(signals)
        
        if self.bollingerVisualizer:
            self.bollingerVisualizer.visualize(dates, sourceData, bollingerData, result.actionedSignals)
        
        return result