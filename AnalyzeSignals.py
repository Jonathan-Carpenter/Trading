import configparser
import datetime
import matplotlib.pyplot as plt
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
from ModelInputDataProvider import ModelInputDataProvider

config = configparser.ConfigParser()
config.read('dev.ini')

modelFileLocation: str = config['tensorflow']['ModelFileLocation']

dbFileLocation: str = config['database']['DatabaseFileLocation']

dbClient = TradingDataClient(dbFileLocation)
dbClient.ensureSeeded()

startDate = datetime.date.fromisoformat("2021-02-01")
endDate = datetime.date.fromisoformat("2025-12-01")

simulateBearishMarket = False

if simulateBearishMarket:
    startDate = datetime.date.fromisoformat("2024-12-01")
    endDate = datetime.date.fromisoformat("2025-06-01")

amountInvestedPerTrade = 100

tickerIds = dbClient.getAllDailyTickerSymbols()
# tickerIds = [ "ABNB" ]

# visualizedTickers = { "AAPL" }
visualizedTickers = {}

neuralNetworkModel = tf.keras.models.load_model(modelFileLocation)

def getAnalyzers(tickerId: str, compositeConfigurations: list[list[tuple]]) -> dict[str, Analyzer]:
    
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
    
    for configuration in compositeConfigurations:
        
        emaWeight = configuration[0][0]
        emaWindowSize = configuration[0][1]
        bollingerWeight = configuration[1][0]
        bollingerWindowSize = configuration[1][1]
        macdWeight = configuration[2][0]
        macdWindowSize = configuration[2][1]
        relativeStrengthIndexWeight = configuration[3][0]
        relativeStrengthIndexWindowSize = configuration[3][1]
        windowSize = configuration[4][0]
        threshold = configuration[4][1]
        
        analyzers[f"Composite Analysis - EMA (wt={emaWeight}, wd={emaWindowSize}), Bollinger (wt={bollingerWeight}, wd={bollingerWindowSize}), MACD (wt={macdWeight}, wd={macdWindowSize}) + RSI (wt={relativeStrengthIndexWeight}, wd={relativeStrengthIndexWindowSize}) - Window Size {windowSize} - Threshold {threshold}"] = CompositeAnalyzer(
            amountInvestedPerTrade,
            windowSize,
            threshold,
            [
                WeightedAnalyzerConfiguration(exponentialAverageCrossoverAnalyzer, emaWeight, emaWindowSize),
                WeightedAnalyzerConfiguration(bollingerBandCrossoverAnalyzer, bollingerWeight, bollingerWindowSize),
                WeightedAnalyzerConfiguration(movingAverageConvergenceDivergenceCrossoverAnalyzer, macdWeight, macdWindowSize),
                WeightedAnalyzerConfiguration(relativeStrengthIndexThresholdAnalyzer, relativeStrengthIndexWeight, relativeStrengthIndexWindowSize)
            ],
            CompositeVisualizer(f"{tickerId} Composite EMA, Bollinger, MACD, RSI Analysis") if tickerId in visualizedTickers else None)
    
    
    return analyzers
    
profitPerAnalyzer: dict[str, float] = {}


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

# emaWeight = configuration[0][0]
# emaWindowSize = configuration[0][1]
# bollingerWeight = configuration[1][0]
# bollingerWindowSize = configuration[1][1]
# macdWeight = configuration[2][0]
# macdWindowSize = configuration[2][1]
# relativeStrengthIndexWeight = configuration[3][0]
# relativeStrengthIndexWindowSize = configuration[3][1]
# windowSize = configuration[4][0]
# threshold = configuration[4][1]
compositeConfigurations = [
    # [(1, 30), (6, 5), (1, 30), (1, 30), (5, 0.03)]
]

if False:
    
    compositeConfigurations = []
    
    possibleAnalyzerWeightings = [0, 1, 2, 6]
    possibleAnalyzerWindowSizes = [5, 10, 30]
    possibleWindowSizes = [1, 5, 20]
    possibleThresholds = [0.03, 0.1, 0.2]
    
    for emaWeight in possibleAnalyzerWeightings:
        for emaWindowSize in possibleAnalyzerWindowSizes:
            
            for bollingerWeight in possibleAnalyzerWeightings:
                for bollingerWindowSize in possibleAnalyzerWindowSizes:
                    
                    for macdWeight in possibleAnalyzerWeightings:
                        for macdWindowSize in possibleAnalyzerWindowSizes:
                            
                            for rsiWeight in possibleAnalyzerWeightings:
                                for rsiWindowSize in possibleAnalyzerWindowSizes:
                                    
                                    for windowSize in possibleWindowSizes:
                                        for threshold in possibleThresholds:
                                        
                                            compositeConfigurations.append([
                                                (emaWeight, emaWindowSize),
                                                (bollingerWeight, bollingerWindowSize),
                                                (macdWeight, macdWindowSize),
                                                (rsiWeight, rsiWindowSize),
                                                (windowSize, threshold),
                                            ])

for key in getAnalyzers("SEED", compositeConfigurations):
    profitPerAnalyzer[key] = 0
    profitPerAnalyzer["Neural Network"] = 0

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
    
    analyzersDict = getAnalyzers(tickerId, compositeConfigurations)
    if len(analyzersDict) > 20:
        analyzersDict = tqdm(analyzersDict, leave=False)
        
    for key in analyzersDict:
                
        analysisResult = analyzersDict[key].analyze(tickerId, dates, closes)
        
        profitPerAnalyzer[key] += analysisResult.totalProfit
    
    neuralNetworkAnalyzer = NeuralNetworkPredictionAnalyzer(
        amountInvestedPerTrade,
        ModelInputDataProvider(dbClient),
        neuralNetworkModel,
        NeuralNetworkPredictionSignalDetector(neuralNetworkModel, 7.5),
        NeuralNetworkPredictionVisualizer(f"{tickerId} Neural Network Prediction") if False else None)
    
    analysisResult = neuralNetworkAnalyzer.analyzeTicker(tickerId, startDate, endDate, 30, 10)
    
    profitPerAnalyzer["Neural Network"] += analysisResult.totalProfit
        
    if len(analyzersDict) > 1000:
        printTop20Analyzers()
    
    print("")
    
print(f"\nAnalysis complete @ {datetime.datetime.now()}.")
print(f"Amount invested per trade: £{amountInvestedPerTrade:.2f}")

printTop20Analyzers()