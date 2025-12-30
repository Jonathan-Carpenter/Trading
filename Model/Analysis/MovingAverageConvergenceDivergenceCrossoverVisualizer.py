import datetime
import matplotlib.pyplot as plt

from Model.Indicators.MovingAverageConvergenceDivergenceIndicatorData import MovingAverageConvergenceDivergenceIndicatorData
from Model.Signals.TradingSignal import TradingSignal
from Model.Visualizer import Visualizer

class MovingAverageConvergenceDivergenceCrossoverVisualizer(Visualizer):
    
    def __init__(self, description: str):
        self.description = description
        
    def visualize(self, dates: list[datetime.date], sourceData: list[float], movingAverageConvergenceDivergenceData: MovingAverageConvergenceDivergenceIndicatorData, signals: list[TradingSignal]):
        fig, axs = plt.subplots(2, label=self.description, layout='constrained', sharex=True)
        
        axs[0].plot(dates, sourceData)
        axs[0].plot(dates, movingAverageConvergenceDivergenceData.shortTermAverageData, label="Short-term EMA")
        axs[0].plot(dates, movingAverageConvergenceDivergenceData.longTermAverageData, label="Long-term EMA")
        
        axs[1].plot(dates, movingAverageConvergenceDivergenceData.data, label="MACD (short-term - long-term)")
        axs[1].plot(dates, movingAverageConvergenceDivergenceData.signalData, label="MACD signal (EMA of MACD)")
        
        self.plotSignals(axs[0], signals)
        
        axs[0].legend()
        axs[1].legend()