import datetime
import uuid
from Model.Indicators.UpperLowerBoundIndicatorData import UpperLowerBoundIndicatorData
from Model.Signals.TradingSignal import TradingSignal
from Model.Signals.BuySignal import BuySignal
from Model.Signals.SellSignal import SellSignal

class NeuralNetworkPredictionSignalDetector:
    
    def __init__(self, model, thresholdPercentage):
        self.model = model
        self.thresholdPercentage = thresholdPercentage
        
        self.id = uuid.uuid4()
    
    def detect(self, predictions, dates, closes):
        
        signals = []
        
        for i in range(len(predictions)):
            
            currentClose = closes[i]
            currentDate = dates[i]
            
            if predictions[i] == None:
                continue
            
            if predictions[i] > 100 and predictions[i] > 100 + self.thresholdPercentage:
                signals.append(BuySignal(currentClose, currentDate, self.id))
                
            elif predictions[i] < 100 and predictions[i] < 100 - self.thresholdPercentage:
                signals.append(SellSignal(currentClose, currentDate, self.id))
            
        return signals