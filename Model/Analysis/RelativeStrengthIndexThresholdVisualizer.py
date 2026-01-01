import datetime
import matplotlib.pyplot as plt

from Model.Indicators.IndicatorData import IndicatorData
from Model.Indicators.MovingAverageConvergenceDivergenceIndicatorData import MovingAverageConvergenceDivergenceIndicatorData
from Model.Signals.TradingSignal import TradingSignal
from Model.Visualizer import Visualizer

class RelativeStrengthIndexThresholdVisualizer(Visualizer):
    
    def __init__(self, description: str):
        self.description = description
        
    def visualize(self, dates: list[datetime.date], sourceData: list[float], relativeStrengthIndexData: IndicatorData, signals: list[TradingSignal]):
        fig, axs = plt.subplots(2, label=self.description, layout='constrained', sharex=True)
        
        axs[0].plot(dates, sourceData)
        
        axs[1].plot(dates, relativeStrengthIndexData.data, label="Relative Strength Index")
        
        self.plotSignals(axs[0], signals)
        
        axs[0].legend()
        axs[1].legend()