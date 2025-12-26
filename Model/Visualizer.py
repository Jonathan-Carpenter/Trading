import matplotlib.pyplot as plt
from Model.Signals.TradingSignal import TradingSignal
from Model.Signals.BuySignal import BuySignal
from Model.Signals.SellSignal import SellSignal

class Visualizer:
    
    def plotSignals(self, ax: plt.Axes, signals: list[TradingSignal]):
        
        buySignals: list[BuySignal] = []
        sellSignals: list[SellSignal] = []
        
        for signal in signals:
            
            if isinstance(signal, BuySignal):
                buySignals.append(signal)
                
            if isinstance(signal, SellSignal):
                sellSignals.append(signal)
                
        ax.scatter(x=[s.date for s in buySignals], y=[s.price for s in buySignals], c="g", label="Buy signals")
        ax.scatter(x=[s.date for s in sellSignals], y=[s.price for s in sellSignals], c="r", label="Sell signals")