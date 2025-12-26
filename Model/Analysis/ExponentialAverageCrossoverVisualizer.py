import matplotlib.pyplot as plt

from Model.Visualizer import Visualizer

class ExponentialAverageCrossoverVisualizer(Visualizer):
    
    def __init__(self, description: str):
        self.description = description
        
    def visualize(self, dates, sourceData, shortTermAverageData, longTermAverageData, signals):
        fig, ax = plt.subplots(label=self.description, layout='constrained')
        
        ax.plot(dates, sourceData)
        ax.plot(dates, shortTermAverageData)
        ax.plot(dates, longTermAverageData)
        
        self.plotSignals(ax, signals)