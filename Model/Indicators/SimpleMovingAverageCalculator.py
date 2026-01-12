from Model.Indicators.IndicatorData import IndicatorData
from Model.Indicators.AverageCalculator import AverageCalculator

class SimpleMovingAverageCalculator(AverageCalculator):
    
    def __init__(self, windowSize: int, description: str):
        super().__init__(windowSize, description)
    
    def calculate(self, sourceData: list[float]):
        
        length = len(sourceData)
        
        assert length > self.windowSize
        
        results: list[float | None] = [None] * length
        results[0] = sourceData[0]
        
        windowStart = 0
        windowEnd = 1
        
        while windowEnd < length:
            values = sourceData[windowStart:windowEnd]
            
            results[windowEnd] = sum(values) / len(values)
            
            if windowEnd >= self.windowSize:
                windowStart += 1
            
            windowEnd += 1
            
        return IndicatorData(self.description, results)