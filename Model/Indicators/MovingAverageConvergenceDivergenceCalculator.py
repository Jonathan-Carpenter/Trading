from Model.Indicators.AverageCalculator import AverageCalculator
from Model.Indicators.IndicatorData import IndicatorData
from Model.Indicators.MovingAverageConvergenceDivergenceIndicatorData import MovingAverageConvergenceDivergenceIndicatorData


class MovingAverageConvergenceDivergenceCalculator:
    
    def __init__(
        self,
        description: str,
        shortTermAverageCalculator: AverageCalculator,
        longTermAverageCalculator: AverageCalculator,
        signalCalculator: AverageCalculator):
        
        self.description = description
        self.shortTermAverageCalculator = shortTermAverageCalculator
        self.longTermAverageCalculator = longTermAverageCalculator
        self.signalCalculator = signalCalculator
        
    def calculate(self, sourceData: list[float]) -> MovingAverageConvergenceDivergenceIndicatorData:
        
        shortTermAverageData = self.shortTermAverageCalculator.calculate(sourceData).data
        longTermAverageData = self.longTermAverageCalculator.calculate(sourceData).data
        
        movingAverageConvergenceDivergenceData = [short - long for (short, long) in zip(shortTermAverageData, longTermAverageData)]
        
        signalData = self.signalCalculator.calculate(movingAverageConvergenceDivergenceData).data
        
        return MovingAverageConvergenceDivergenceIndicatorData(self.description, shortTermAverageData, longTermAverageData, movingAverageConvergenceDivergenceData, signalData)