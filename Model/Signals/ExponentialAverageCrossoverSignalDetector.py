import datetime
import uuid

from Model.Signals.TradingSignal import TradingSignal
from Model.Signals.BuySignal import BuySignal
from Model.Signals.SellSignal import SellSignal

class ExponentialAverageCrossoverSignalDetector:
    
    def __init__(self):
        self.id = uuid.uuid4()
    
    def detect(
        self,
        dates: list[datetime.date],
        sourceData: list[float],
        shortTermAverageData: list[float],
        longTermAverageData: list[float]) -> list[TradingSignal]:
        
        dataSetLength = len(dates)
        
        assert dataSetLength == len(sourceData) == len(shortTermAverageData) == len(longTermAverageData)
        
        previousShortAboveLong = None
        signals: list[TradingSignal] = []
        
        for i in range(1, dataSetLength):
            
            if (not shortTermAverageData[i]) or (not longTermAverageData[i]):
                continue
            
            shortAboveLong = shortTermAverageData[i] > longTermAverageData[i]
            
            if previousShortAboveLong == None:
                previousShortAboveLong = shortAboveLong
                continue
            
            if (not previousShortAboveLong) and shortAboveLong:
                
                buySignal = BuySignal(sourceData[i], dates[i], self.id)
                signals.append(buySignal)
                
            if previousShortAboveLong and (not shortAboveLong):
                
                sellSignal = SellSignal(sourceData[i], dates[i], self.id)
                signals.append(sellSignal)
                
            previousShortAboveLong = shortAboveLong
                
        return signals