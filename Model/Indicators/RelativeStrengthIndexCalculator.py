import numpy as np
from Model.Indicators.IndicatorData import IndicatorData

class RelativeStrengthIndexCalculator:
    def __init__(self, windowSize: int, description: str):
        self.windowSize = windowSize
        self.description = description
        
    def calculate(self, sourceData: np.ndarray) -> np.ndarray:
        
        length = len(sourceData)
        
        percentageGains = [0] * length
        percentagelosses = [0] * length
        
        for i in range(1, len(sourceData)):
            
            if sourceData[i] > sourceData[i - 1]:
                percentageGains[i] = (sourceData[i] / sourceData[i - 1]) - 1
                
            if sourceData[i] < sourceData[i - 1]:
                percentagelosses[i] = 1 - (sourceData[i] / sourceData[i - 1])
                
        windowStart = 0
        windowEnd = self.windowSize
        
        relativeStrengthIndexData = np.zeros(sourceData.shape)
        relativeStrengthIndexData[0 : self.windowSize] = 50
        
        while windowEnd < length:
            
            windowGains = percentageGains[windowStart:windowEnd]
            windowLosses = percentagelosses[windowStart:windowEnd]
            
            windowAverageGain = sum(windowGains) / len(windowGains)
            windowAverageLoss = sum(windowLosses) / len(windowLosses)
            
            smoothedCurrentGain = (windowAverageGain * (self.windowSize - 1)) + percentageGains[windowEnd]
            smoothedCurrentLoss = (windowAverageLoss * (self.windowSize - 1)) + percentagelosses[windowEnd]
            
            if smoothedCurrentLoss == 0:
                relativeStrengthIndexData[windowEnd] = 100
                
            else:
                smoothedGainLossRatio = smoothedCurrentGain / smoothedCurrentLoss
                relativeStrengthIndexData[windowEnd] = 100 / (1 + smoothedGainLossRatio)
            
            windowStart += 1
            windowEnd += 1
            
        return relativeStrengthIndexData