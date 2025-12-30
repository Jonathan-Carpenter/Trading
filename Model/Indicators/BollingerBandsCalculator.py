import statistics

from Model.Indicators.AverageCalculator import AverageCalculator
from Model.Indicators.UpperLowerBoundIndicatorData import UpperLowerBoundIndicatorData

class BollingerBandsCalculator:
    def __init__(self, averageCalculator: AverageCalculator):
        self.averageCalculator = averageCalculator
        
    def calculate(self, sourceData: list[float]) -> UpperLowerBoundIndicatorData:
        
        length = len(sourceData)
        
        assert length > self.averageCalculator.windowSize
        
        averages = self.averageCalculator.calculate(sourceData).data
        
        windowStart = 0
        windowEnd = self.averageCalculator.windowSize
        
        upperBandResults: list[float | None] = [None] * length
        lowerBandResults: list[float | None] = [None] * length
        
        while windowEnd < length:
            
            window = sourceData[windowStart:windowEnd]
            standardDeviation = statistics.stdev(window)
            
            bollingerDeviation = 2 * standardDeviation
            upperBand = averages[windowEnd] + bollingerDeviation
            lowerBand = averages[windowEnd] - bollingerDeviation
            
            upperBandResults[windowEnd] = upperBand
            lowerBandResults[windowEnd] = lowerBand
            
            windowStart += 1
            windowEnd += 1
            
        return UpperLowerBoundIndicatorData("Bollinger bands", averages, upperBandResults, lowerBandResults)