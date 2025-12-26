from Model.Indicators.IndicatorData import IndicatorData

class UpperLowerBoundIndicatorData(IndicatorData):
        
    def __init__(self, description: str, data: list[float], upperBoundData: list[float | None], lowerBoundData: list[float | None]):
        super().__init__(description, data)
        
        self.upperBoundData = upperBoundData
        self.lowerBoundData = lowerBoundData