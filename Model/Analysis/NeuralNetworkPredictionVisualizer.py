import datetime
import matplotlib.pyplot as plt

from Model.Indicators.UpperLowerBoundIndicatorData import UpperLowerBoundIndicatorData
from Model.Signals.TradingSignal import TradingSignal
from Model.Visualizer import Visualizer

class NeuralNetworkPredictionVisualizer(Visualizer):
    
    def __init__(self, description: str):
        self.description = description
        
    def visualize(self, dates: list[datetime.date], closes: list[float], percentages: list[float], signals: list[TradingSignal]):
        fig, axs = plt.subplots(2, label=self.description, layout='constrained', sharex=True)
        
        axs[0].plot(dates, closes)
        axs[0].set_xlabel("Date")
        axs[0].set_ylabel("Stock close price")
        
        axs[0].grid()
        
        axs[1].plot(dates, percentages)
        axs[1].set_xlabel("Date")
        axs[1].set_ylabel("Predicted price movement (%)")
        
        axs[1].grid()
        axs[1].legend()
        
        self.plotSignals(axs[0], signals)