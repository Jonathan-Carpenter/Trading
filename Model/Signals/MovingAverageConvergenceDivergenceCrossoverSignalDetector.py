import datetime
import uuid

from Model.Indicators.MovingAverageConvergenceDivergenceIndicatorData import MovingAverageConvergenceDivergenceIndicatorData
from Model.Signals.TradingSignal import TradingSignal
from Model.Signals.BuySignal import BuySignal
from Model.Signals.SellSignal import SellSignal

# TODO: Extract shared detector for this and exponential average crossover.
class MovingAverageConvergenceDivergenceCrossoverSignalDetector:
    
    def __init__(self):
        self.id = uuid.uuid4()
    
    def detect(self, dates: list[datetime.date], sourceData: list[float], indicatorData: MovingAverageConvergenceDivergenceIndicatorData) -> list[TradingSignal]:
        
        dataSetLength = len(dates)
        
        movingAverageConvergenceDivergenceData = indicatorData.data
        signalData = indicatorData.signalData
        
        assert dataSetLength == len(sourceData) == len(movingAverageConvergenceDivergenceData) == len(signalData)
        
        previousMacdAboveSignal = None
        signals: list[TradingSignal] = []
        
        for i in range(1, dataSetLength):
            
            if (not movingAverageConvergenceDivergenceData[i]) or (not signalData[i]):
                continue
            
            macdAboveSignal = movingAverageConvergenceDivergenceData[i] > signalData[i]
            
            if previousMacdAboveSignal == None:
                previousMacdAboveSignal = macdAboveSignal
                continue
            
            if (not previousMacdAboveSignal) and macdAboveSignal:
                
                buySignal = BuySignal(sourceData[i], dates[i], self.id)
                signals.append(buySignal)
                
            if previousMacdAboveSignal and (not macdAboveSignal):
                
                sellSignal = SellSignal(sourceData[i], dates[i], self.id)
                signals.append(sellSignal)
                
            previousMacdAboveSignal = macdAboveSignal
                
        return signals