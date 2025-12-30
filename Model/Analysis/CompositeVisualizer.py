import datetime
import matplotlib.pyplot as plt

from Model.Signals.BuySignal import BuySignal
from Model.Signals.SellSignal import SellSignal
from Model.Signals.TradingSignal import TradingSignal
from Model.Visualizer import Visualizer

class CompositeVisualizer(Visualizer):
    
    def __init__(self, description: str):
        self.description = description
        
    def visualize(self, dates: list[datetime.date], sourceData: list[float], innerSignals: list[TradingSignal], compositeSignals: list[TradingSignal]):
        fig, ax = plt.subplots(label=self.description, layout='constrained')
        
        ax.plot(dates, sourceData)
        
        buySignals: list[BuySignal] = []
        sellSignals: list[SellSignal] = []
        
        for signal in innerSignals:
            
            if isinstance(signal, BuySignal):
                buySignals.append(signal)
                
            if isinstance(signal, SellSignal):
                sellSignals.append(signal)
        
        ax.scatter(x=[s.date for s in buySignals], y=[s.price for s in buySignals], c="#8cdb8f", label="Inner buy signals")
        ax.scatter(x=[s.date for s in sellSignals], y=[s.price for s in sellSignals], c="#db8c8c", label="Inner sell signals")
        
        ax.legend()
        
        self.plotSignals(ax, compositeSignals)