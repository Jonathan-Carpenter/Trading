class ExponentialMovingAverageCalculator:
    
    def calculate(self, values):
        
        length = len(values)
        
        assert length > 0
        
        previousAverage = values[0]
        smoothingValue = 2 / (length + 1)
        
        for value in values:
            
            weightedCurrentValue = value * smoothingValue
            weightedPreviousAverage = previousAverage * (1 - smoothingValue)
            
            newAverage = weightedCurrentValue + weightedPreviousAverage
            previousAverage = newAverage
            
        return previousAverage