import datetime
import matplotlib.pyplot as plt

from Model.Indicators.UpperLowerBoundIndicatorData import UpperLowerBoundIndicatorData
from Model.Signals.TradingSignal import TradingSignal
from Model.Visualizer import Visualizer

class BollingerBandCrossoverVisualizer(Visualizer):
    
    def __init__(self, description: str):
        self.description = description
        
    def visualize(self, dates: list[datetime.date], sourceData: list[float], bollingerData: UpperLowerBoundIndicatorData, signals: list[TradingSignal]):
        fig, ax = plt.subplots(label=self.description, layout='constrained')
        
        ax.plot(dates, sourceData)
        ax.plot(dates, bollingerData.data)
        ax.plot(dates, bollingerData.upperBoundData, color='#ababab')
        ax.plot(dates, bollingerData.lowerBoundData, color='#ababab')
        
        self.plotSignals(ax, signals)