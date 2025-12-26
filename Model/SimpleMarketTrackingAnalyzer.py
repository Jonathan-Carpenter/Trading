from Model.Analyzer import Analyzer
from Model.AnalysisResult import AnalysisResult
from Model.Signals.BuySignal import BuySignal
from Model.Signals.SellSignal import SellSignal

class SimpleMarketTrackingAnalyzer(Analyzer):
    
    def __init__(self, amountInvestedPerTrade: int):
        super().__init__(amountInvestedPerTrade)
        
    def analyze(self, dates, sourceData) -> AnalysisResult:
        
        buySignal = BuySignal(sourceData[0], dates[0])
        sellSignal = SellSignal(sourceData[-1], dates[-1])
        
        return self.simulate([buySignal, sellSignal])