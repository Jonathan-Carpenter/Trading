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
    
    def detect(self, predictions, dates, closes) -> tuple[list[TradingSignal], list[float]]:
        
        signals = []
        predictedPercentages = [None] * len(dates)
        
        for i in range(len(predictions)):
            
            currentClose = closes[i]
            currentDate = dates[i]
            
            predictedFutureClose = predictions[i]
            
            if predictedFutureClose == None:
                continue
            
            if predictedFutureClose > currentClose:
                ratio = predictedFutureClose / currentClose
                percentageMove = (ratio * 100) - 100
                
                predictedPercentages[i] = percentageMove
                
                if percentageMove > self.thresholdPercentage:
                    signals.append(BuySignal(currentClose, currentDate, self.id))
                
            else:
                ratio = currentClose / predictedFutureClose
                percentageMove = 100 - (ratio * 100)
                
                predictedPercentages[i] = percentageMove
                
                if percentageMove < -self.thresholdPercentage:
                    signals.append(SellSignal(currentClose, currentDate, self.id))
            
        return (signals, predictedPercentages)