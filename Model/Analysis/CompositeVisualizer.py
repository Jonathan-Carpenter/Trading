import datetime
import matplotlib.pyplot as plt

from Model.Signals.BuySignal import BuySignal
from Model.Signals.SellSignal import SellSignal
from Model.Signals.TradingSignal import TradingSignal
from Model.Visualizer import Visualizer

class CompositeVisualizer(Visualizer):
    
    def __init__(self, description: str):
        self.description = description
        
    def visualize(self, dates: list[datetime.date], sourceData: list[float], innerSignals: list[TradingSignal], compositeSignals: list[TradingSignal], compositeStrengthIndexData: list[float]):
        fig, axs = plt.subplots(2, label=self.description, layout='constrained', sharex=True)
        
        axs[0].plot(dates, sourceData)
        axs[1].plot(dates, compositeStrengthIndexData)
        
        buySignals: list[BuySignal] = []
        sellSignals: list[SellSignal] = []
        
        for signal in innerSignals:
            
            if isinstance(signal, BuySignal):
                buySignals.append(signal)
                
            if isinstance(signal, SellSignal):
                sellSignals.append(signal)
        
        axs[0].scatter(x=[s.date for s in buySignals], y=[s.price for s in buySignals], c="#96ffad", marker="x", label="Inner buy signals")
        axs[0].scatter(x=[s.date for s in sellSignals], y=[s.price for s in sellSignals], c="#ff9b9b", marker="x", label="Inner sell signals")
        
        axs[0].legend()
        
        self.plotSignals(axs[0], compositeSignals)