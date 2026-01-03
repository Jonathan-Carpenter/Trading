import datetime
from Model.Analysis.BollingerBandCrossoverVisualizer import BollingerBandCrossoverVisualizer
from Model.Analysis.NeuralNetworkPredictionVisualizer import NeuralNetworkPredictionVisualizer
from Model.AnalysisResult import AnalysisResult
from Model.Analysis.Analyzer import Analyzer
from Model.DailyTicker import DailyTickerOpenCloseSummary
from Model.Indicators.BollingerBandsCalculator import BollingerBandsCalculator
from Model.Signals.BollingerBandCrossoverSignalDetector import BollingerBandCrossoverSignalDetector
from Model.Signals.NeuralNetworkPredictionSignalDetector import NeuralNetworkPredictionSignalDetector
from Model.Signals.TradingSignal import TradingSignal
from ModelInputDataProvider import ModelInputDataProvider


class NeuralNetworkPredictionAnalyzer(Analyzer):
    
    def __init__(
        self,
        amountInvestedPerTrade: int,
        dataProvider: ModelInputDataProvider,
        model,
        signalDetector: NeuralNetworkPredictionSignalDetector,
        visualizer: NeuralNetworkPredictionVisualizer):
        
        super().__init__(amountInvestedPerTrade)
        
        self.dataProvider = dataProvider
        self.model = model
        self.signalDetector = signalDetector
        self.visualizer = visualizer
        
    def analyzeTicker(self, tickerSymbol: str, startDate: datetime.date, endDate: datetime.date, windowSize: int, predictionLookAhead: int) -> AnalysisResult:
        
        inputs, _, dates, closes = self.dataProvider.getData([tickerSymbol], startDate, endDate, windowSize, predictionLookAhead)
        
        predictions = self.model.predict(inputs).flatten().tolist()
        predictions = ([None] * windowSize) + predictions[:-predictionLookAhead]
        signals, percentages = self.signalDetector.detect(predictions, dates, closes)
        
        result = self.simulate(signals)
        
        # Align prediction with actual over time - for the sake of easier comparison.
        visualizedPredictions = predictions + ([None] * predictionLookAhead)
        
        if self.visualizer:
            self.visualizer.visualize(dates, closes, visualizedPredictions, percentages, result.actionedSignals)
        
        return result