import datetime
import uuid

import numpy as np
from Model.Indicators.UpperLowerBoundIndicatorData import UpperLowerBoundIndicatorData
from Model.Signals.TradingSignal import TradingSignal
from Model.Signals.BuySignal import BuySignal
from Model.Signals.SellSignal import SellSignal

class BollingerBandCrossoverSignalDetector:
    
    def __init__(self):
        self.id = uuid.uuid4()
    
    def detect(self, dates: list[datetime.date], sourceData: list[float], bollingerData: np.ndarray) -> list[TradingSignal]:
        
        lowerBandData = bollingerData[:, 0]
        upperBandData = bollingerData[:, 2]
        
        wasPreviousPriceBelowLowerBand = False
        wasPreviousPriceAboveUpperBand = False
        
        signals = []
        
        for i in range(bollingerData.shape[0]):
            
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