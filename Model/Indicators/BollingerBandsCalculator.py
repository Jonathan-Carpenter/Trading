import statistics

import numpy as np

from Model.Indicators.AverageCalculator import AverageCalculator
from Model.Indicators.UpperLowerBoundIndicatorData import UpperLowerBoundIndicatorData

class BollingerBandsCalculator:
    def __init__(self, averageCalculator: AverageCalculator):
        self.averageCalculator = averageCalculator
        
    def calculate(self, sourceData: list[float]) -> UpperLowerBoundIndicatorData:
        
        length = len(sourceData)
        
        assert length > self.averageCalculator.windowSize
        
        averages = self.averageCalculator.calculate(sourceData).data
        averages = np.array(averages)
        averages = np.reshape(averages, (length, 1))
        
        windowStart = 0
        windowEnd = 2
        
        upperBandResults = np.zeros((length, 1))
        lowerBandResults = np.zeros((length, 1))
        
        upperBandResults[0:2, :] = averages[0:2, :]
        lowerBandResults[0:2, :] = averages[0:2, :]
        
        while windowEnd < length:
            
            window = sourceData[windowStart:windowEnd]
            standardDeviation = statistics.stdev(window)
            
            bollingerDeviation = 2 * standardDeviation
            upperBand = averages[windowEnd] + bollingerDeviation
            lowerBand = averages[windowEnd] - bollingerDeviation
            
            upperBandResults[windowEnd] = upperBand
            lowerBandResults[windowEnd] = lowerBand
            
            if windowEnd >= self.averageCalculator.windowSize:
                windowStart += 1
                
            windowEnd += 1
            
        return UpperLowerBoundIndicatorData("Bollinger bands", averages, upperBandResults, lowerBandResults)