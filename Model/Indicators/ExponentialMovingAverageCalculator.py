from Model.Indicators.IndicatorData import IndicatorData

class ExponentialMovingAverageCalculator:
    
    def __init__(self, windowSize: int, description: str):
        self.windowSize = windowSize
        self.description = description
    
    def calculate(self, sourceData) -> IndicatorData:
        
        length = len(sourceData)
        
        assert length > 0
        
        results = [None] * length
        
        results[0] = sourceData[0]
        smoothingValue = 2 / (self.windowSize + 1)
        
        for i in range(1, length):
            
            weightedCurrentValue = sourceData[i] * smoothingValue
            weightedPreviousAverage = results[i - 1] * (1 - smoothingValue)
            
            newAverage = weightedCurrentValue + weightedPreviousAverage
            results[i] = newAverage
            
        return IndicatorData(self.description, results)