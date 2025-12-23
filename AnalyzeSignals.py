import configparser
import datetime
import matplotlib.pyplot as plt

from Data.TradingDataClient import TradingDataClient
from Model.Indicators.ExponentialMovingAverageCalculator import ExponentialMovingAverageCalculator
from Model.ExponentialAverageCrossoverSignalDetector import ExponentialAverageCrossoverSignalDetector

from Model.Signals.BuySignal import BuySignal
from Model.Signals.SellSignal import SellSignal

config = configparser.ConfigParser()
config.read('dev.ini')

dbFileLocation: str = config['database']['DatabaseFileLocation']

dbClient = TradingDataClient(dbFileLocation)
dbClient.ensureSeeded()

startDate = datetime.date.fromisoformat("2024-01-01")
endDate = datetime.date.fromisoformat("2025-01-01")

tickerIds = ["AAPL", "GOOGL", "META", "BA"]
# tickerIds = ["BA"]

shortTermAverageCalculator = ExponentialMovingAverageCalculator(15, "15 Day EMA")
longTermAverageCalculator = ExponentialMovingAverageCalculator(50, "50 Day EMA")

signalDetector = ExponentialAverageCrossoverSignalDetector()

# For a conservative estimate, keep this low and constant. Eliminates any compounding effect.
# TODO: Implement a realistic max for the total invested at one time. While the number of ticker IDs in the simulation is low, we can be sure this is low.
amountInvestedPerTrade = 100
totalProfit = 0

showGraphs = True
gridDimensions = [2, 2]

fig, ax = plt.subplots(*gridDimensions, label=f"Trading signals", layout='constrained')

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
        
    shortTermAverageData = shortTermAverageCalculator.calculate(closes).data
    longTermAverageData = longTermAverageCalculator.calculate(closes).data
    buySignalData = []
    sellSignalData = []
    
    signals = signalDetector.detect(dates, closes, shortTermAverageData, longTermAverageData)
    
    if not signals:
        continue
    
    positionOpen = False
    positionStart = 0
    
    for signal in signals:
        
        if (not positionOpen) and isinstance(signal, BuySignal):
            positionOpen = True
            positionStart = signal.price
            
            buySignalData.append((signal.date, signal.price))
            
            print(f"\nOpened long position on {tickerId}\nDate: {signal.date}\nPrice: {signal.price}")
            
        if positionOpen and isinstance(signal, SellSignal):
            positionOpen = False
            profitRatio = signal.price / positionStart
            
            simulatedClosePrice = amountInvestedPerTrade * profitRatio
            
            profit = simulatedClosePrice - amountInvestedPerTrade
            totalProfit += profit
            
            sellSignalData.append([signal.date, signal.price])
            
            print(f"\nClosed long position on {tickerId}\nDate: {signal.date}\nPrice: {signal.price}\nProfit: £{profit:.2f}")
            
    if showGraphs:
        
        axis = ax.flat[i]
        
        axis.plot(dates, closes, label="Close price")
        axis.plot(dates, shortTermAverageData, label=shortTermAverageCalculator.description)
        axis.plot(dates, longTermAverageData, label=longTermAverageCalculator.description)
        
        axis.scatter(x=[s[0] for s in buySignalData], y=[s[1] for s in buySignalData], c="g", label="Buy signals")
        axis.scatter(x=[s[0] for s in sellSignalData], y=[s[1] for s in sellSignalData], c="r", label="Sell signals")
        
        axis.set_title(tickerId)
        axis.legend(loc="upper left")

print(f"\n\nAnalysis complete.\nAmount invested per trade: £{amountInvestedPerTrade:.2f}\nSimulated total profit: £{totalProfit:.2f}")

plt.show()