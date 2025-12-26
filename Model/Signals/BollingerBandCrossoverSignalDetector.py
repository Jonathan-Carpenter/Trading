import datetime
import uuid
from Model.Indicators.UpperLowerBoundIndicatorData import UpperLowerBoundIndicatorData
from Model.Signals.TradingSignal import TradingSignal
from Model.Signals.BuySignal import BuySignal
from Model.Signals.SellSignal import SellSignal

class BollingerBandCrossoverSignalDetector:
    
    def __init__(self):
        self.id = uuid.uuid4()
    
    def detect(self, dates: list[datetime.date], sourceData: list[float], bollingerData: UpperLowerBoundIndicatorData) -> list[TradingSignal]:
        
        length = len(dates)
        
        assert length == len(sourceData) == len(bollingerData.data) == len(bollingerData.lowerBoundData) == len(bollingerData.upperBoundData)
        
        lowerBandData = bollingerData.lowerBoundData
        upperBandData = bollingerData.upperBoundData
        
        wasPreviousPriceBelowLowerBand = False
        wasPreviousPriceAboveUpperBand = False
        
        signals = []
        
        for i in range(length):
            
            if (not lowerBandData[i]) or (not upperBandData[i]):
                continue
            
            if wasPreviousPriceBelowLowerBand and (sourceData[i] > lowerBandData[i]):
                buySignal = BuySignal(sourceData[i], dates[i], self.id)
                signals.append(buySignal)
                
            if wasPreviousPriceAboveUpperBand and (sourceData[i] < upperBandData[i]):
                sellSignal = SellSignal(sourceData[i], dates[i], self.id)
                signals.append(sellSignal)
            
            wasPreviousPriceBelowLowerBand = sourceData[i] < lowerBandData[i]
            wasPreviousPriceAboveUpperBand = sourceData[i] > upperBandData[i]
            
        return signals