from Model.Indicators.IndicatorData import IndicatorData

class IdentityCalculator:
    def __init__(self, description: str):
        self.description = description
        
    def calculate(self, sourceData: list[float]) -> IndicatorData:
        return IndicatorData(self.description, sourceData)