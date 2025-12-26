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

config = configparser.ConfigParser()
config.read('dev.ini')

dbFileLocation: str = config['database']['DatabaseFileLocation']

dbClient = TradingDataClient(dbFileLocation)
dbClient.ensureSeeded()

startDate = datetime.date.fromisoformat("2024-01-01")
endDate = datetime.date.fromisoformat("2025-12-01")
amountInvestedPerTrade = 100

tickerIds = ["AAPL", "GOOGL", "META", "BA", "BLK"]
# tickerIds = ["AAPL"]

bollingerCalculator = BollingerBandsCalculator(SimpleMovingAverageCalculator(20, "20 Day SMA"))

analyzer = ExponentialAverageCrossoverAnalyzer(
    amountInvestedPerTrade,
    ExponentialMovingAverageCalculator(15, "15 Day EMA"),
    ExponentialMovingAverageCalculator(50, "50 Day EMA"),
    ExponentialAverageCrossoverSignalDetector(),
    ExponentialAverageCrossoverVisualizer())

totalProfit = 0

for i in range(len(tickerIds)):

    tickerId = tickerIds[i]

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
        
    totalProfit += analyzer.analyze(dates, closes).totalProfit
    

print(f"\n\nAnalysis complete.\nAmount invested per trade: £{amountInvestedPerTrade:.2f}\nSimulated total profit: £{totalProfit:.2f}")