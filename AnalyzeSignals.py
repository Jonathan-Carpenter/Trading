import configparser
import datetime
import matplotlib.pyplot as plt
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
from Model.Analysis.RelativeStrengthIndexThresholdAnalyzer import RelativeStrengthIndexThresholdAnalyzer
from Model.Analysis.RelativeStrengthIndexThresholdVisualizer import RelativeStrengthIndexThresholdVisualizer
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
from Model.Signals.RelativeStrengthIndexThresholdSignalDetector import RelativeStrengthIndexThresholdSignalDetector

config = configparser.ConfigParser()
config.read('dev.ini')

dbFileLocation: str = config['database']['DatabaseFileLocation']

dbClient = TradingDataClient(dbFileLocation)
dbClient.ensureSeeded()

startDate = datetime.date.fromisoformat("2024-01-01")
endDate = datetime.date.fromisoformat("2025-12-01")

simulateBearishMarket = False

if simulateBearishMarket:
    startDate = datetime.date.fromisoformat("2025-02-01")
    endDate = datetime.date.fromisoformat("2025-04-11")

amountInvestedPerTrade = 100

tickerIds = dbClient.getAllDailyTickerSymbols()
# tickerIds = [ "AAPL" ]

# visualizedTickers = { "AAPL" }
visualizedTickers = {}

def getAnalyzers(tickerId: str, compositeConfigurations: list[tuple]) -> dict[str, Analyzer]:
    
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
        
        emaWeight = configuration[0]
        bollingerWeight = configuration[1]
        macdWeight = configuration[2]
        relativeStrengthIndexWeight = configuration[3]
        windowSize = configuration[4]
        
        analyzers[f"Composite Analysis - EMA ({emaWeight}), Bollinger ({bollingerWeight}), MACD ({macdWeight}) + RSI ({relativeStrengthIndexWeight}) - Window Size {windowSize}"] = CompositeAnalyzer(
            amountInvestedPerTrade,
            windowSize,
            [
                (exponentialAverageCrossoverAnalyzer, emaWeight),
                (bollingerBandCrossoverAnalyzer, bollingerWeight),
                (movingAverageConvergenceDivergenceCrossoverAnalyzer, macdWeight),
                (relativeStrengthIndexThresholdAnalyzer, relativeStrengthIndexWeight)
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

# emaWeight = configuration[0]
# bollingerWeight = configuration[1]
# macdWeight = configuration[2]
# relativeStrengthIndexWeight = configuration[3]
# windowSize = configuration[4]
compositeConfigurations = [
    (2, 6, 1, 1, 30)
]

if True:
    
    compositeConfigurations = []
    
    for emaWeight in range(0, 6):
        for bollingerWeight in range(0, 6):
            for macdWeight in range(0, 6):
                for rsiWeight in range(0, 6):
                    for windowSize in range(10, 101, 10):
                        
                        compositeConfigurations.append(
                            (
                                emaWeight,
                                bollingerWeight,
                                macdWeight,
                                rsiWeight,
                                windowSize
                            ))

for key in getAnalyzers("SEED", compositeConfigurations):
    profitPerAnalyzer[key] = 0

for tickerId in tqdm(tickerIds):

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
        
    for key in tqdm(analyzersDict, leave=False):
                
        analysisResult = analyzersDict[key].analyze(tickerId, dates, closes)
        
        profitPerAnalyzer[key] += analysisResult.totalProfit
        
    if len(analyzersDict) > 100:
        printTop20Analyzers()
    
    print("")
    
print(f"\nAnalysis complete @ {datetime.datetime.now()}.")
print(f"Amount invested per trade: £{amountInvestedPerTrade:.2f}")

printTop20Analyzers()