from Model.Indicators.IndicatorData import IndicatorData
from Model.Indicators.AverageCalculator import AverageCalculator

class ExponentialMovingAverageCalculator(AverageCalculator):
    
    def __init__(self, windowSize: int, description: str):
        super().__init__(windowSize, description)
    
    def calculate(self, sourceData: list[float]) -> IndicatorData:
        
        length = len(sourceData)
        
        assert length > 0
        
        results: list[float] = [0] * length
        
        results[0] = sourceData[0]
        smoothingValue = 2 / (self.windowSize + 1)
        
        for i in range(1, length):
            
            weightedCurrentValue = sourceData[i] * smoothingValue
            weightedPreviousAverage = results[i - 1] * (1 - smoothingValue)
            
            newAverage = weightedCurrentValue + weightedPreviousAverage
            results[i] = newAverage
            
        return IndicatorData(self.description, results)