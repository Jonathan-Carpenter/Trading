import datetime
from Model.Signals.TradingSignal import TradingSignal
from Model.Signals.BuySignal import BuySignal
from Model.Signals.SellSignal import SellSignal
from Model.AnalysisResult import AnalysisResult

class Analyzer:
    
    def __init__(self, amountInvestedPerTrade: int):
        self.amountInvestedPerTrade = amountInvestedPerTrade
    
    def simulate(self, signals: list[TradingSignal]) -> AnalysisResult:
        
        totalProfit = 0
        
        positionOpen = False
        positionStart = 0
        
        actionedSignals = []
        
        for signal in signals:
        
            if (not positionOpen) and isinstance(signal, BuySignal):
                positionOpen = True
                positionStart = signal.price
                
                actionedSignals.append(signal)
                
            if positionOpen and isinstance(signal, SellSignal):
                positionOpen = False
                profitRatio = signal.price / positionStart
                
                simulatedClosePrice = self.amountInvestedPerTrade * profitRatio
                
                profit = simulatedClosePrice - self.amountInvestedPerTrade
                totalProfit += profit
                
                actionedSignals.append(signal)
                
        return AnalysisResult(totalProfit, actionedSignals)
    
    def analyze(self, dates: list[datetime.date], sourceData: list[float], rawSignals: bool = False) -> AnalysisResult | list[TradingSignal]:
        return None