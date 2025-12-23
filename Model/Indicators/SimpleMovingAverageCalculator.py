from Model.Indicators.IndicatorData import IndicatorData

class SimpleMovingAverageCalculator:
    
    def __init__(self, windowSize: int, description: str):
        self.windowSize = windowSize
        self.description = description
    
    def calculate(self, sourceData):
        
        length = len(sourceData)
        
        assert length > self.windowSize
        
        results = [None] * length
        
        windowStart = 0
        windowEnd = self.windowSize
        
        while windowEnd < length:
            values = sourceData[windowStart:windowEnd]
            
            results[windowEnd] = sum(values) / len(values)
            
            windowStart += 1
            windowEnd += 1
            
        return IndicatorData(self.description, results)