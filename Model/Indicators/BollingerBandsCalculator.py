import statistics

import numpy as np

from Model.Indicators.AverageCalculator import AverageCalculator
from Model.Indicators.UpperLowerBoundIndicatorData import UpperLowerBoundIndicatorData

class BollingerBandsCalculator:
    def __init__(self, averageCalculator: AverageCalculator):
        self.averageCalculator = averageCalculator
        
    def calculate(
        self,
        sourceData: np.ndarray) -> np.ndarray:
        '''Calculates Bollinger Bands for the given data.
        
        Keyword arguments:
        sourceData -- The source data column matrix used as input for the calculation.
                
        Returns np array with shape (sourceData.shape[0], 3). Columns of returned array are:
        - 0 = lower bound
        - 1 = average
        - 2 = upper bound
        '''
        
        length = sourceData.shape[0]
        
        assert length > self.averageCalculator.windowSize
        
        results = np.zeros((sourceData.shape[0], 3))
        
        results[ : , 1 ] = self.averageCalculator.calculate(sourceData)
        results[ 0 : 2 , 0 ] = results[ 0 : 2, 1 ]
        results[ 0 : 2 , 2 ] = results[ 0 : 2, 1 ]
        
        windowStart = 0
        windowEnd = 2
        
        while windowEnd < length:
            
            window = sourceData[windowStart:windowEnd]
            standardDeviation = statistics.stdev(window)
            
            bollingerDeviation = 2 * standardDeviation
            lowerBand = results[windowEnd][1] - bollingerDeviation
            upperBand = results[windowEnd][1] + bollingerDeviation
            
            results[windowEnd][0] = lowerBand
            results[windowEnd][2] = upperBand
            
            if windowEnd >= self.averageCalculator.windowSize:
                windowStart += 1
                
            windowEnd += 1
            
        return results