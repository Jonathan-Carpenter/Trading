from Model.Indicators.IndicatorData import IndicatorData

class MovingAverageConvergenceDivergenceIndicatorData(IndicatorData):
        
    def __init__(
        self,
        description: str,
        shortTermAverageData: list[float],
        longTermAverageData: list[float],
        movingAverageConvergenceDivergenceData: list[float],
        signalData: list[float | None]):
        
        super().__init__(description, movingAverageConvergenceDivergenceData)
        
        self.shortTermAverageData = shortTermAverageData
        self.longTermAverageData = longTermAverageData
        self.signalData = signalData