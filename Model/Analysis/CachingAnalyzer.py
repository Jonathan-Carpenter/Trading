import datetime
from Model.Analysis.Analyzer import Analyzer
from Model.AnalysisResult import AnalysisResult
from Model.Signals.TradingSignal import TradingSignal


class CachingAnalyzer(Analyzer):
    
    def __init__(self, amountInvestedPerTrade: int, innerAnalyzer: Analyzer):
        super().__init__(amountInvestedPerTrade)
        
        self.innerAnalyzer = innerAnalyzer
        self.cache: dict[(str, bool), AnalysisResult | list[TradingSignal]] = {}
        
    def analyze(self, tickerSymbol: str, dates: list[datetime.date], sourceData: list[float], rawSignals: bool = False) -> AnalysisResult | list[TradingSignal]:
        
        key = (tickerSymbol, rawSignals)
        
        if key in self.cache:
            return self.cache[key]
        
        result = self.innerAnalyzer.analyze(tickerSymbol, dates, sourceData, rawSignals)
        self.cache[key] = result
        
        return result
    