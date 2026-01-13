import numpy as np
from Model.Indicators.IndicatorData import IndicatorData
from Model.Indicators.AverageCalculator import AverageCalculator

class SimpleMovingAverageCalculator(AverageCalculator):
    
    def __init__(self, windowSize: int, description: str):
        super().__init__(windowSize, description)
    
    def calculate(self, sourceData: np.ndarray) -> np.ndarray:
        '''Calculates averages for the given data.
        
        Keyword arguments:
        sourceData -- The source data column matrix used as input for the calculation.
                
        Returns np array with equal shape to input.
        '''
        
        length = sourceData.shape[0]
        
        assert length > self.windowSize
        
        results = np.zeros(sourceData.shape)
        results[0] = sourceData[0]
        
        windowStart = 0
        windowEnd = 1
        
        while windowEnd < length:
            values = sourceData[windowStart:windowEnd]
            
            results[windowEnd] = sum(values) / (windowEnd - windowStart)
            
            if windowEnd >= self.windowSize:
                windowStart += 1
            
            windowEnd += 1
            
        return results