import configparser
import datetime
import matplotlib.pyplot as plt

from Data.TradingDataClient import TradingDataClient
from Model.Analysis.BollingerBandCrossoverAnalyzer import BollingerBandCrossoverAnalyzer
from Model.Analysis.BollingerBandCrossoverVisualizer import BollingerBandCrossoverVisualizer
from Model.Analysis.CompositeAnalyzer import CompositeAnalyzer
from Model.Analysis.CompositeVisualizer import CompositeVisualizer
from Model.Indicators.SimpleMovingAverageCalculator import SimpleMovingAverageCalculator
from Model.Indicators.ExponentialMovingAverageCalculator import ExponentialMovingAverageCalculator
from Model.Indicators.BollingerBandsCalculator import BollingerBandsCalculator
from Model.Signals.BollingerBandCrossoverSignalDetector import BollingerBandCrossoverSignalDetector
from Model.Signals.ExponentialAverageCrossoverSignalDetector import ExponentialAverageCrossoverSignalDetector
from Model.Analysis.ExponentialAverageCrossoverAnalyzer import ExponentialAverageCrossoverAnalyzer
from Model.Analysis.ExponentialAverageCrossoverVisualizer import ExponentialAverageCrossoverVisualizer
from Model.Analysis.SimpleMarketTrackingAnalyzer import SimpleMarketTrackingAnalyzer
from Model.Signals.TradingSignal import TradingSignal

config = configparser.ConfigParser()
config.read('dev.ini')

dbFileLocation: str = config['database']['DatabaseFileLocation']

dbClient = TradingDataClient(dbFileLocation)
dbClient.ensureSeeded()

startDate = datetime.date.fromisoformat("2024-01-01")
endDate = datetime.date.fromisoformat("2025-12-01")

amountInvestedPerTrade = 100

tickerIds = dbClient.getAllDailyTickerSymbols()

# visualizedTickers = { "ABT" }
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
    
    analyzers = {
        "market average": SimpleMarketTrackingAnalyzer(amountInvestedPerTrade),
        "exponential average crossover": exponentialAverageCrossoverAnalyzer,
        "bollinger band crossover": bollingerBandCrossoverAnalyzer
    }
    
    for i in range(1, 2):
        
        # scoreThreshold = i / 10
        scoreThreshold = 1.6
        
        analyzers[f"{scoreThreshold:.2f} composite EMA + Bollinger"] = CompositeAnalyzer(
            amountInvestedPerTrade,
            30,
            scoreThreshold,
            2,
            [exponentialAverageCrossoverAnalyzer, bollingerBandCrossoverAnalyzer],
            CompositeVisualizer(f"{tickerId} Composite Analysis") if tickerId in visualizedTickers else None)
    
    return analyzers
    
profitPerAnalyzer: dict[str, float] = {}

for key in getAnalyzers("SEED"):
    profitPerAnalyzer[key] = 0

for tickerId in tickerIds:
    
    print(f"Analyzing {tickerId}...")

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
        
    for key in analyzersDict:
                
        analysisResult = analyzersDict[key].analyze(dates, closes)
        
        profitPerAnalyzer[key] += analysisResult.totalProfit
    
print("Analysis complete.")
print(f"Amount invested per trade: £{amountInvestedPerTrade:.2f}")
print("Simulated total profit per analyzer:")

for key in profitPerAnalyzer:
    print(f"\t{key}: £{profitPerAnalyzer[key]:.2f}")
    
plt.show()