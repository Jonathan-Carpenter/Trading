from Model.Indicators.IndicatorData import IndicatorData

class IdentityCalculator:
    def __init__(self, description):
        self.description = description
        
    def calculate(self, sourceData) -> IndicatorData:
        return IndicatorData(self.description, sourceData)