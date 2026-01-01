import datetime
import uuid
from Model.Indicators.IndicatorData import IndicatorData
from Model.Signals.TradingSignal import TradingSignal
from Model.Signals.BuySignal import BuySignal
from Model.Signals.SellSignal import SellSignal

class RelativeStrengthIndexThresholdSignalDetector:
    
    def __init__(self):
        self.id = uuid.uuid4()
    
    def detect(self, dates: list[datetime.date], sourceData: list[float], relativeStrengthIndexData: IndicatorData) -> list[TradingSignal]:
        
        length = len(dates)
        
        assert length == len(sourceData) == len(relativeStrengthIndexData.data)
        
        signals = []
        
        previousAboveUpperThreshold = False
        previousBelowLowerThreshold = False
        
        for i in range(length):
            
            if relativeStrengthIndexData.data[i] == None:
                continue
            
            if (relativeStrengthIndexData.data[i] < 30) and (not previousBelowLowerThreshold):
                buySignal = BuySignal(sourceData[i], dates[i], self.id)
                signals.append(buySignal)
                
                previousBelowLowerThreshold = True
                
            if (relativeStrengthIndexData.data[i] > 70) and (not previousAboveUpperThreshold):
                sellSignal = SellSignal(sourceData[i], dates[i], self.id)
                signals.append(sellSignal)
                
                previousAboveUpperThreshold = True
                
            if relativeStrengthIndexData.data[i] > 30:
                previousBelowLowerThreshold = False
                
            if relativeStrengthIndexData.data[i] < 70:
                previousAboveUpperThreshold = False
            
        return signals