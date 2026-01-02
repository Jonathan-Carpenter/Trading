from Model.Analysis.Analyzer import Analyzer


class WeightedAnalyzerConfiguration:
    
    def __init__(self, analyzer: Analyzer, weighting: int, windowSize: int):
        
        self.analyzer = analyzer
        self.weighting = weighting
        self.windowSize = windowSize