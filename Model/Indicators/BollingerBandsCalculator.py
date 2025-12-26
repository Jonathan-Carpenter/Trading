import statistics

from Model.Indicators.AverageCalculator import AverageCalculator
from Model.Indicators.IndicatorData import IndicatorData

class BollingerBandsCalculator:
    def __init__(self, averageCalculator: AverageCalculator):
        self.averageCalculator = averageCalculator
        
    def calculate(self, sourceData):
        
        length = len(sourceData)
        
        assert length > self.averageCalculator.windowSize
        
        averages = self.averageCalculator.calculate(sourceData).data
        
        windowStart = 0
        windowEnd = self.averageCalculator.windowSize
        
        upperBandResults = [None] * length
        lowerBandResults = [None] * length
        
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
            
        return IndicatorData("Bollinger bands", (upperBandResults, lowerBandResults, averages))