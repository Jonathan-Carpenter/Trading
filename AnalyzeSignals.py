import configparser
import datetime
import matplotlib.pyplot as plt

from Data.TradingDataClient import TradingDataClient
from Model.Indicators.SimpleMovingAverageCalculator import SimpleMovingAverageCalculator
from Model.Indicators.ExponentialMovingAverageCalculator import ExponentialMovingAverageCalculator
from Model.Indicators.BollingerBandsCalculator import BollingerBandsCalculator
from Model.ExponentialAverageCrossoverSignalDetector import ExponentialAverageCrossoverSignalDetector
from Model.ExponentialAverageCrossoverAnalyzer import ExponentialAverageCrossoverAnalyzer
from Model.ExponentialAverageCrossoverVisualizer import ExponentialAverageCrossoverVisualizer
from Model.SimpleMarketTrackingAnalyzer import SimpleMarketTrackingAnalyzer
from Model.Signals.TradingSignal import TradingSignal

config = configparser.ConfigParser()
config.read('dev.ini')

dbFileLocation: str = config['database']['DatabaseFileLocation']

dbClient = TradingDataClient(dbFileLocation)
dbClient.ensureSeeded()

startDate = datetime.date.fromisoformat("2024-01-01")
endDate = datetime.date.fromisoformat("2025-12-01")

amountInvestedPerTrade = 100
showGraphs = False

tickerIds = ["AAPL", "GOOGL", "META", "BA", "BLK", "BAC"]
# tickerIds = ["AAPL"]

bollingerCalculator = BollingerBandsCalculator(SimpleMovingAverageCalculator(20, "20 Day SMA"))

def getAnalyzers(tickerId: str, visualize: bool):
    return {
        "market average": SimpleMarketTrackingAnalyzer(amountInvestedPerTrade),
        "exponential average crossover": ExponentialAverageCrossoverAnalyzer(
            amountInvestedPerTrade,
            ExponentialMovingAverageCalculator(15, "15 Day EMA"),
            ExponentialMovingAverageCalculator(50, "50 Day EMA"),
            ExponentialAverageCrossoverSignalDetector(),
            ExponentialAverageCrossoverVisualizer(tickerId) if visualize else None)
    }
    
profitPerAnalyzer: dict[str, float] = {}

for key in getAnalyzers("SEED", False):
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
        
    analyzersDict = getAnalyzers(tickerId, showGraphs)
        
    for key in analyzersDict:
                
        analysisResult = analyzersDict[key].analyze(dates, closes)
        
        profitPerAnalyzer[key] += analysisResult.totalProfit
    
print("Analysis complete.")
print(f"Amount invested per trade: £{amountInvestedPerTrade:.2f}")
print("Simulated total profit per analyzer:")

for key in profitPerAnalyzer:
    print(f"\t{key}: £{profitPerAnalyzer[key]:.2f}")