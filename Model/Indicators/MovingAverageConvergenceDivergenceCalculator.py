import numpy as np
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
        
    def calculate(self, sourceData: np.ndarray) -> np.ndarray:
        '''Calculates a MACD indicator for the given data.
        
        Keyword arguments:
        sourceData -- The source data column matrix used as input for the calculation.
                
        Returns np array with shape (sourceData.shape[0], 3). Columns of returned array are:
        - 0 = short term average data
        - 1 = long term average data
        - 2 = MACD signal
        '''
        
        results = np.zeros((sourceData.shape[0], 3))
        
        results[ : , 0 ] = self.shortTermAverageCalculator.calculate(sourceData)
        results[ : , 1 ] = self.longTermAverageCalculator.calculate(sourceData)
        
        divergenceData = results[ : , 0 ] - results[ : , 1 ]
        
        results[ : , 2 ] = self.signalCalculator.calculate(divergenceData)
        
        return results