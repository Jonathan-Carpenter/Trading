import datetime
import uuid
from Model.Analysis.Analyzer import Analyzer
from Model.AnalysisResult import AnalysisResult
from Model.Signals.BuySignal import BuySignal
from Model.Signals.SellSignal import SellSignal
from Model.Signals.TradingSignal import TradingSignal

class SimpleMarketTrackingAnalyzer(Analyzer):
    
    def __init__(self, amountInvestedPerTrade: int):
        super().__init__(amountInvestedPerTrade)
        
        self.id = uuid.uuid4()
        
    def analyze(self, tickerSymbol: str, dates: list[datetime.date], sourceData: list[float], rawSignals: bool = False) -> AnalysisResult | list[TradingSignal]:
        
        buySignal = BuySignal(sourceData[0], dates[0], self.id)
        sellSignal = SellSignal(sourceData[-1], dates[-1], self.id)
        
        if rawSignals:
            return [buySignal, sellSignal]
        
        return self.simulate([buySignal, sellSignal])