import numpy as np
from Model.Indicators.IndicatorData import IndicatorData
from Model.Indicators.AverageCalculator import AverageCalculator

class ExponentialMovingAverageCalculator(AverageCalculator):
    
    def __init__(self, windowSize: int, description: str):
        super().__init__(windowSize, description)
    
    def calculate(self, sourceData: np.ndarray) -> np.ndarray:
        '''Calculates averages for the given data.
        
        Keyword arguments:
        sourceData -- The source data column matrix used as input for the calculation.
                
        Returns np array with equal shape to input.
        '''
        
        length = sourceData.shape[0]
        
        assert length > 0
        
        results = np.zeros(sourceData.shape)
        
        results[0] = sourceData[0]
        smoothingValue = 2 / (self.windowSize + 1)
        
        for i in range(1, length):
            
            weightedCurrentValue = sourceData[i] * smoothingValue
            weightedPreviousAverage = results[i - 1] * (1 - smoothingValue)
            
            newAverage = weightedCurrentValue + weightedPreviousAverage
            results[i] = newAverage
            
        return results