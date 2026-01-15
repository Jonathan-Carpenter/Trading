import configparser
import datetime
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from tqdm import tqdm

from Data.TradingDataClient import TradingDataClient
from Model.Analysis.Analyzer import Analyzer
from Model.Analysis.BollingerBandCrossoverAnalyzer import BollingerBandCrossoverAnalyzer
from Model.Analysis.BollingerBandCrossoverVisualizer import BollingerBandCrossoverVisualizer
from Model.Analysis.CachingAnalyzer import CachingAnalyzer
from Model.Analysis.CompositeAnalyzer import CompositeAnalyzer
from Model.Analysis.CompositeVisualizer import CompositeVisualizer
from Model.Analysis.MovingAverageConvergenceDivergenceCrossoverAnalyzer import MovingAverageConvergenceDivergenceCrossoverAnalyzer
from Model.Analysis.MovingAverageConvergenceDivergenceCrossoverVisualizer import MovingAverageConvergenceDivergenceCrossoverVisualizer
from Model.Analysis.NeuralNetworkPredictionAnalyzer import NeuralNetworkPredictionAnalyzer
from Model.Analysis.NeuralNetworkPredictionVisualizer import NeuralNetworkPredictionVisualizer
from Model.Analysis.RelativeStrengthIndexThresholdAnalyzer import RelativeStrengthIndexThresholdAnalyzer
from Model.Analysis.RelativeStrengthIndexThresholdVisualizer import RelativeStrengthIndexThresholdVisualizer
from Model.Analysis.WeightedAnalyzerConfiguration import WeightedAnalyzerConfiguration
from Model.Indicators.MovingAverageConvergenceDivergenceCalculator import MovingAverageConvergenceDivergenceCalculator
from Model.Indicators.RelativeStrengthIndexCalculator import RelativeStrengthIndexCalculator
from Model.Indicators.SimpleMovingAverageCalculator import SimpleMovingAverageCalculator
from Model.Indicators.ExponentialMovingAverageCalculator import ExponentialMovingAverageCalculator
from Model.Indicators.BollingerBandsCalculator import BollingerBandsCalculator
from Model.Signals.BollingerBandCrossoverSignalDetector import BollingerBandCrossoverSignalDetector
from Model.Signals.ExponentialAverageCrossoverSignalDetector import ExponentialAverageCrossoverSignalDetector
from Model.Analysis.ExponentialAverageCrossoverAnalyzer import ExponentialAverageCrossoverAnalyzer
from Model.Analysis.ExponentialAverageCrossoverVisualizer import ExponentialAverageCrossoverVisualizer
from Model.Analysis.SimpleMarketTrackingAnalyzer import SimpleMarketTrackingAnalyzer
from Model.Signals.MovingAverageConvergenceDivergenceCrossoverSignalDetector import MovingAverageConvergenceDivergenceCrossoverSignalDetector
from Model.Signals.NeuralNetworkPredictionSignalDetector import NeuralNetworkPredictionSignalDetector
from Model.Signals.RelativeStrengthIndexThresholdSignalDetector import RelativeStrengthIndexThresholdSignalDetector
from Model.Signals.TradingSignal import TradingSignal
from ModelInputDataProvider import ModelInputDataProvider

config = configparser.ConfigParser()
config.read('dev.ini')

modelFileLocation: str = config['tensorflow']['ModelSaveLocation']

dbFileLocation: str = config['database']['DatabaseFileLocation']

dbClient = TradingDataClient(dbFileLocation)
dbClient.ensureSeeded()

startDate = datetime.date.fromisoformat("2024-01-01")
endDate = datetime.date.fromisoformat("2025-12-01")

simulateBearishMarket = False

if simulateBearishMarket:
    startDate = datetime.date.fromisoformat("2024-12-01")
    endDate = datetime.date.fromisoformat("2025-12-01")

amountInvestedPerTrade = 100

tickerIds = dbClient.getAllDailyTickerSymbols()
# tickerIds = [ "ABNB" ]

# visualizedTickers = { "AAPL" }
visualizedTickers = {}

neuralNetworkModel = tf.keras.models.load_model(modelFileLocation)

def getAnalyzers(tickerId: str) -> dict[str, Analyzer]:
    
    exponentialAverageCrossoverAnalyzer = CachingAnalyzer(
        amountInvestedPerTrade,
        ExponentialAverageCrossoverAnalyzer(
            amountInvestedPerTrade,
            ExponentialMovingAverageCalculator(10, "10 Day EMA"),
            ExponentialMovingAverageCalculator(30, "30 Day EMA"),
            ExponentialAverageCrossoverSignalDetector(),
            ExponentialAverageCrossoverVisualizer(f"{tickerId} Exponential Moving Average Crossover") if tickerId in visualizedTickers else None))
    
    bollingerBandCrossoverAnalyzer = CachingAnalyzer(
        amountInvestedPerTrade,
        BollingerBandCrossoverAnalyzer(
            amountInvestedPerTrade,
            BollingerBandsCalculator(SimpleMovingAverageCalculator(20, "20 Day SMA")),
            BollingerBandCrossoverSignalDetector(),
            BollingerBandCrossoverVisualizer(f"{tickerId} Bollinger Band Crossover") if tickerId in visualizedTickers else None))
    
    movingAverageConvergenceDivergenceCrossoverAnalyzer = CachingAnalyzer(
        amountInvestedPerTrade,
        MovingAverageConvergenceDivergenceCrossoverAnalyzer(
            amountInvestedPerTrade,
            MovingAverageConvergenceDivergenceCalculator(
                "Moving Average Convergence Divergence",
                ExponentialMovingAverageCalculator(12, "12 Day EMA"),
                ExponentialMovingAverageCalculator(26, "26 Day EMA"),
                ExponentialMovingAverageCalculator(9, "9 Day EMA")),
            MovingAverageConvergenceDivergenceCrossoverSignalDetector(),
            MovingAverageConvergenceDivergenceCrossoverVisualizer(f"{tickerId} Moving Average Convergence Divergence Crossover") if tickerId in visualizedTickers else None))
    
    relativeStrengthIndexThresholdAnalyzer = CachingAnalyzer(
        amountInvestedPerTrade,
        RelativeStrengthIndexThresholdAnalyzer(
            amountInvestedPerTrade,
            RelativeStrengthIndexCalculator(14, "14 Day Relative Strength Index Indicator"),
            RelativeStrengthIndexThresholdSignalDetector(),
            RelativeStrengthIndexThresholdVisualizer(f"{tickerId} Relative Strength Index") if tickerId in visualizedTickers else None))
    
    analyzers = {
        "Market Average": SimpleMarketTrackingAnalyzer(amountInvestedPerTrade),
        "Exponential Average Crossover": exponentialAverageCrossoverAnalyzer,
        "Bollinger Band Crossover": bollingerBandCrossoverAnalyzer,
        "Moving Average Convergence Divergence Crossover": movingAverageConvergenceDivergenceCrossoverAnalyzer,
        "Relative Strength Index Threshold": relativeStrengthIndexThresholdAnalyzer
    }    
    
    return analyzers
    
profitPerAnalyzer: dict[str, float] = { "Neural Network": 0 }

for key in getAnalyzers("SEED"):
    profitPerAnalyzer[key] = 0

def printTop20Analyzers():
    analyzersByProfit = sorted(profitPerAnalyzer.items(), key=lambda analyzerProfit: analyzerProfit[1], reverse=True)
    bestProfit = analyzersByProfit[0][1]
        
    print(f"\nTop 20 analyzers:\n")

    totalAnalyzers = len(analyzersDict)

    for i in range(20):
        
        if i >= totalAnalyzers:
            print(f"{i + 1}.\n")
            continue
        
        name = analyzersByProfit[i][0]
        profit = analyzersByProfit[i][1]
        
        print(f"{i + 1}. {name}")
        print(f"Profit: £{profit:.2f}")
        
        if i > 0:
            print(f"({(profit / bestProfit) * 100:.1f}% of best)")
            
        print("")

recentNeuralNetworkSignals: list[(str, TradingSignal)] = []

for tickerId in tqdm(tickerIds):
    
    if not dbClient.isDailyTickerDataContiguousOverRange(tickerId, startDate, endDate):
        continue

    dates = []
    closes = []
    indicators = []

    date = startDate

    while date < endDate:
        ticker = dbClient.getDailyTicker(tickerId, date)
        date += datetime.timedelta(days=1)
        
        if not ticker:
            continue
        
        dates.append(date)
        closes.append(ticker.close)
        
    if len(closes) < (endDate - startDate).days / 2:
        continue
    
    analyzersDict = getAnalyzers(tickerId)
    if len(analyzersDict) > 20:
        analyzersDict = tqdm(analyzersDict, leave=False)
        
    for key in analyzersDict:
                
        analysisResult = analyzersDict[key].analyze(tickerId, dates, np.array(closes))
        
        profitPerAnalyzer[key] += analysisResult.totalProfit
    
    neuralNetworkAnalyzer = NeuralNetworkPredictionAnalyzer(
        amountInvestedPerTrade,
        ModelInputDataProvider(
            dbClient,
            [ExponentialMovingAverageCalculator(10, "EMA 10"), ExponentialMovingAverageCalculator(30, "EMA 30")],
            [BollingerBandsCalculator(SimpleMovingAverageCalculator(20, "SMA 20"))],
            [MovingAverageConvergenceDivergenceCalculator(
                "Moving Average Convergence Divergence",
                ExponentialMovingAverageCalculator(12, "12 Day EMA"),
                ExponentialMovingAverageCalculator(26, "26 Day EMA"),
                ExponentialMovingAverageCalculator(9, "9 Day EMA"))],
            [RelativeStrengthIndexCalculator(14, "14 Day Relative Strength Index Indicator")]),
        neuralNetworkModel,
        NeuralNetworkPredictionSignalDetector(neuralNetworkModel, 4.85),
        NeuralNetworkPredictionVisualizer(f"{tickerId} Neural Network Prediction") if False else None)
    
    analysisResult = neuralNetworkAnalyzer.analyzeTicker(tickerId, startDate, endDate, 90, 10)
    
    for signal in analysisResult.actionedSignals:
        if endDate - signal.date <= datetime.timedelta(days=10):
            recentNeuralNetworkSignals.append((tickerId, signal))
    
    profitPerAnalyzer["Neural Network"] += analysisResult.totalProfit
        
    if len(analyzersDict) > 1000:
        printTop20Analyzers()
    
    print("")
    
recentNeuralNetworkSignals.sort(key=(lambda s: s[1].date), reverse=True)
    
print(f"\nAnalysis complete @ {datetime.datetime.now()}.")
print(f"Amount invested per trade: £{amountInvestedPerTrade:.2f}")

printTop20Analyzers()

print("\nRecent neural network signals:")

for ticker, signal in recentNeuralNetworkSignals:
    print(f"[{ticker}] {signal}")