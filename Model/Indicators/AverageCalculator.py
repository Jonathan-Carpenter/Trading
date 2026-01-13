import numpy as np
from Model.Indicators.IndicatorData import IndicatorData

class AverageCalculator:
    def __init__(self, windowSize: int, description: str):
        self.windowSize = windowSize
        self.description = description
        
    def calculate(self, sourceData: list[float]) -> np.ndarray:
        '''Calculates averages for the given data.
        
        Keyword arguments:
        sourceData -- The source data column matrix used as input for the calculation.
                
        Returns np array with equal shape to input.
        '''
        
        return None