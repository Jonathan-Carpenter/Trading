import configparser
import datetime
import matplotlib.pyplot as plt
from tqdm import tqdm

from Data.TradingDataClient import TradingDataClient
from Model.Analysis.BollingerBandCrossoverAnalyzer import BollingerBandCrossoverAnalyzer
from Model.Analysis.BollingerBandCrossoverVisualizer import BollingerBandCrossoverVisualizer
from Model.Analysis.CompositeAnalyzer import CompositeAnalyzer
from Model.Analysis.CompositeVisualizer import CompositeVisualizer
from Model.Analysis.MovingAverageConvergenceDivergenceCrossoverAnalyzer import MovingAverageConvergenceDivergenceCrossoverAnalyzer
from Model.Analysis.MovingAverageConvergenceDivergenceCrossoverVisualizer import MovingAverageConvergenceDivergenceCrossoverVisualizer
from Model.Indicators.MovingAverageConvergenceDivergenceCalculator import MovingAverageConvergenceDivergenceCalculator
from Model.Indicators.SimpleMovingAverageCalculator import SimpleMovingAverageCalculator
from Model.Indicators.ExponentialMovingAverageCalculator import ExponentialMovingAverageCalculator
from Model.Indicators.BollingerBandsCalculator import BollingerBandsCalculator
from Model.Signals.BollingerBandCrossoverSignalDetector import BollingerBandCrossoverSignalDetector
from Model.Signals.ExponentialAverageCrossoverSignalDetector import ExponentialAverageCrossoverSignalDetector
from Model.Analysis.ExponentialAverageCrossoverAnalyzer import ExponentialAverageCrossoverAnalyzer
from Model.Analysis.ExponentialAverageCrossoverVisualizer import ExponentialAverageCrossoverVisualizer
from Model.Analysis.SimpleMarketTrackingAnalyzer import SimpleMarketTrackingAnalyzer
from Model.Signals.MovingAverageConvergenceDivergenceCrossoverSignalDetector import MovingAverageConvergenceDivergenceCrossoverSignalDetector

config = configparser.ConfigParser()
config.read('dev.ini')

dbFileLocation: str = config['database']['DatabaseFileLocation']

dbClient = TradingDataClient(dbFileLocation)
dbClient.ensureSeeded()

startDate = datetime.date.fromisoformat("2024-01-01")
endDate = datetime.date.fromisoformat("2025-12-01")

amountInvestedPerTrade = 100

tickerIds = dbClient.getAllDailyTickerSymbols()
# tickerIds = [ "AAPL" ]

# visualizedTickers = { "AAPL" }
visualizedTickers = {}

def getAnalyzers(tickerId: str):
    
    exponentialAverageCrossoverAnalyzer = ExponentialAverageCrossoverAnalyzer(
        amountInvestedPerTrade,
        ExponentialMovingAverageCalculator(15, "15 Day EMA"),
        ExponentialMovingAverageCalculator(50, "50 Day EMA"),
        ExponentialAverageCrossoverSignalDetector(),
        ExponentialAverageCrossoverVisualizer(f"{tickerId} Exponential Moving Average Crossover") if tickerId in visualizedTickers else None)
    
    bollingerBandCrossoverAnalyzer = BollingerBandCrossoverAnalyzer(
        amountInvestedPerTrade,
        BollingerBandsCalculator(SimpleMovingAverageCalculator(20, "20 Day SMA")),
        BollingerBandCrossoverSignalDetector(),
        BollingerBandCrossoverVisualizer(f"{tickerId} Bollinger Band Crossover") if tickerId in visualizedTickers else None)
    
    movingAverageConvergenceDivergenceCrossoverAnalyzer = MovingAverageConvergenceDivergenceCrossoverAnalyzer(
        amountInvestedPerTrade,
        MovingAverageConvergenceDivergenceCalculator(
            "Moving Average Convergence Divergence",
            ExponentialMovingAverageCalculator(12, "12 Day EMA"),
            ExponentialMovingAverageCalculator(26, "26 Day EMA"),
            ExponentialMovingAverageCalculator(9, "9 Day EMA")),
        MovingAverageConvergenceDivergenceCrossoverSignalDetector(),
        MovingAverageConvergenceDivergenceCrossoverVisualizer(f"{tickerId} Moving Average Convergence Divergence Crossover") if tickerId in visualizedTickers else None
    )
    
    analyzers = {
        "Market Average": SimpleMarketTrackingAnalyzer(amountInvestedPerTrade),
        "Exponential Average Crossover": exponentialAverageCrossoverAnalyzer,
        "Bollinger Band Crossover": bollingerBandCrossoverAnalyzer,
        "Moving Average Convergence Divergence Crossover": movingAverageConvergenceDivergenceCrossoverAnalyzer
    }
    
    for i in range(1, 2):
        
        # scoreThreshold = i / 10
        scoreThreshold = 0.5
        
        analyzers[f"{scoreThreshold:.2f} Composite EMA + Bollinger - Threshold {scoreThreshold:.2f}"] = CompositeAnalyzer(
            amountInvestedPerTrade,
            30,
            scoreThreshold,
            2,
            [
                (exponentialAverageCrossoverAnalyzer, 1),
                (bollingerBandCrossoverAnalyzer, 1)
            ],
            CompositeVisualizer(f"{tickerId} Composite EMA + Bollinger Analysis") if tickerId in visualizedTickers else None)
        
    for scoreThresholdSeed in range(1, 2):
        for emaWeight in range(1, 2):
            for bollingerWeight in range(1, 2):
                for macdWeight in range(1, 2):
                    for windowSize in range(1, 2):
                        for confidenceRatioThresholdSeed in range(1, 2):
        
                            # Dynamic values
                            scoreThreshold = scoreThresholdSeed / 10.0
                            confidenceRatioThreshold = confidenceRatioThresholdSeed / 10.0
                            
                            # Static values
                            scoreThreshold = 0.9
                            emaWeight = 10
                            bollingerWeight = 17
                            macdWeight = 6
                            windowSize = 30
                            confidenceRatioThreshold = 2.3
                            
                            analyzers[f"Composite EMA ({emaWeight}), Bollinger ({bollingerWeight}) + MACD ({macdWeight}) Analysis - Score Threshold {scoreThreshold:.2f} - Confidence Ratio Threshold {confidenceRatioThreshold:.2f} - Window Size {windowSize}"] = CompositeAnalyzer(
                                amountInvestedPerTrade,
                                windowSize,
                                scoreThreshold,
                                confidenceRatioThreshold,
                                [
                                    (exponentialAverageCrossoverAnalyzer, emaWeight),
                                    (bollingerBandCrossoverAnalyzer, bollingerWeight),
                                    (movingAverageConvergenceDivergenceCrossoverAnalyzer, macdWeight)
                                ],
                                CompositeVisualizer(f"{tickerId} Composite EMA, Bollinger + MACD Analysis") if tickerId in visualizedTickers else None)
    
    return analyzers
    
profitPerAnalyzer: dict[str, float] = {}

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
        
    analyzersDict = getAnalyzers(tickerId)
        
    for key in tqdm(analyzersDict):
                
        analysisResult = analyzersDict[key].analyze(dates, closes)
        
        profitPerAnalyzer[key] += analysisResult.totalProfit
        
    print("")
    
print("\nAnalysis complete.")
print(f"Amount invested per trade: £{amountInvestedPerTrade:.2f}")
    
analyzersByProfit = sorted(profitPerAnalyzer.items(), key=lambda analyzerProfit: analyzerProfit[1], reverse=True)
    
print(f"\nTop 20 analyzers:\n")

totalAnalyzers = len(analyzersDict)

for i in range(20):
    
    if i >= totalAnalyzers:
        print(f"{i + 1}.\n")
        continue
    
    print(f"{i + 1}. {analyzersByProfit[i][0]}\nProfit: £{profitPerAnalyzer[analyzersByProfit[i][0]]:.2f}\n")
    
plt.show()