from Model.Indicators.IndicatorData import IndicatorData

class AverageCalculator:
    def __init__(self, windowSize: int, description: str):
        self.windowSize = windowSize
        self.description = description
        
    def calculate(self, sourceData: list[float]) -> IndicatorData:
        return IndicatorData(self.description, [])