import datetime
import uuid

import numpy as np

from Model.Indicators.MovingAverageConvergenceDivergenceIndicatorData import MovingAverageConvergenceDivergenceIndicatorData
from Model.Signals.TradingSignal import TradingSignal
from Model.Signals.BuySignal import BuySignal
from Model.Signals.SellSignal import SellSignal

# TODO: Extract shared detector for this and exponential average crossover.
class MovingAverageConvergenceDivergenceCrossoverSignalDetector:
    
    def __init__(self):
        self.id = uuid.uuid4()
    
    def detect(self, dates: list[datetime.date], sourceData: list[float], indicatorData: np.ndarray) -> list[TradingSignal]:
        
        dataSetLength = len(dates)
        
        movingAverageConvergenceDivergenceData = indicatorData[ : , 2]
        signalData = indicatorData[ : , 3 ]
        
        assert len(sourceData) == signalData.shape[0]
        
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