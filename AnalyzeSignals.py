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
endDate = datetime.date.fromisoformat("2024-04-01")

amountInvestedPerTrade = 100

tickerIds = dbClient.getAllDailyTickerSymbols()
# tickerIds = [ "AAPL" ]

# visualizedTickers = { "AAPL" }
visualizedTickers = {}

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
    
    for i in range(1, 2):
        
        # scoreThreshold = i / 10
        scoreThreshold = 0.5
        
        analyzers[f"Composite EMA (1) + Bollinger (1) - Threshold {scoreThreshold:.2f}"] = CompositeAnalyzer(
            amountInvestedPerTrade,
            30,
            scoreThreshold,
            2,
            [
                (exponentialAverageCrossoverAnalyzer, 1),
                (bollingerBandCrossoverAnalyzer, 1)
            ],
            CompositeVisualizer(f"{tickerId} Composite EMA + Bollinger Analysis") if tickerId in visualizedTickers else None)
        
    if True:
        
        for scoreThresholdSeed in range(0, 13, 3):
            for emaWeight in range(0, 8):
                for bollingerWeight in range(0, 8):
                    for macdWeight in range(0, 8):
                        for relativeStrengthIndexWeight in range(0, 8):
                            for windowSize in range(35, 36):
                                for confidenceRatioThresholdSeed in range(0, 21, 4):
                
                                    scoreThreshold = scoreThresholdSeed / 10.0
                                    confidenceRatioThreshold = confidenceRatioThresholdSeed / 10.0
                                    
                                    analyzers[f"Composite EMA ({emaWeight}), Bollinger ({bollingerWeight}), MACD ({macdWeight}) + RSI ({relativeStrengthIndexWeight}) Analysis - Score Threshold {scoreThreshold:.2f} - Confidence Ratio Threshold {confidenceRatioThreshold:.2f} - Window Size {windowSize}"] = CompositeAnalyzer(
                                        amountInvestedPerTrade,
                                        windowSize,
                                        scoreThreshold,
                                        confidenceRatioThreshold,
                                        [
                                            (exponentialAverageCrossoverAnalyzer, emaWeight),
                                            (bollingerBandCrossoverAnalyzer, bollingerWeight),
                                            (movingAverageConvergenceDivergenceCrossoverAnalyzer, macdWeight),
                                            (relativeStrengthIndexThresholdAnalyzer, relativeStrengthIndexWeight)
                                        ],
                                        CompositeVisualizer(f"{tickerId} Composite EMA, Bollinger + MACD Analysis") if tickerId in visualizedTickers else None)
    
    if False:
            
        # Static values
        # TODO: Do a big run over the ranges above. The static values below were only after running over 3/4 stocks, and don't perform very well at all.
        scoreThreshold = 0.5
        emaWeight = 3
        bollingerWeight = 7
        macdWeight = 6
        relativeStrengthIndexWeight = 4
        windowSize = 35
        confidenceRatioThreshold = 2.1
        
        analyzers[f"Composite EMA ({emaWeight}), Bollinger ({bollingerWeight}), MACD ({macdWeight}) + RSI ({relativeStrengthIndexWeight}) Analysis - Score Threshold {scoreThreshold:.2f} - Confidence Ratio Threshold {confidenceRatioThreshold:.2f} - Window Size {windowSize}"] = CompositeAnalyzer(
            amountInvestedPerTrade,
            windowSize,
            scoreThreshold,
            confidenceRatioThreshold,
            [
                (exponentialAverageCrossoverAnalyzer, emaWeight),
                (bollingerBandCrossoverAnalyzer, bollingerWeight),
                (movingAverageConvergenceDivergenceCrossoverAnalyzer, macdWeight),
                (relativeStrengthIndexThresholdAnalyzer, relativeStrengthIndexWeight)
            ],
            CompositeVisualizer(f"{tickerId} Composite EMA, Bollinger + MACD Analysis") if tickerId in visualizedTickers else None)
    
    
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

for key in getAnalyzers("SEED"):
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
    
    analyzersDict = getAnalyzers(tickerId)
        
    for key in tqdm(analyzersDict, leave=False):
                
        analysisResult = analyzersDict[key].analyze(tickerId, dates, closes)
        
        profitPerAnalyzer[key] += analysisResult.totalProfit
        
    if len(analyzersDict) > 100:
        printTop20Analyzers()
    
    print("")
    
print(f"\nAnalysis complete @ {datetime.datetime.now()}.")
print(f"Amount invested per trade: £{amountInvestedPerTrade:.2f}")

printTop20Analyzers()