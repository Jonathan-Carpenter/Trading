import matplotlib.pyplot as plt

from Model.Visualizer import Visualizer

class CompositeVisualizer(Visualizer):
    
    def __init__(self, description: str):
        self.description = description
        
    def visualize(self, dates, sourceData, signals):
        fig, ax = plt.subplots(label=self.description, layout='constrained')
        
        ax.plot(dates, sourceData)
        
        self.plotSignals(ax, signals)