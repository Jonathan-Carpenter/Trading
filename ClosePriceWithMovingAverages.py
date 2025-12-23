import configparser
import massive
import datetime
import matplotlib.pyplot as plt
import numpy as np

from Massive.ThrottledMassiveClient import ThrottledMassiveClient
from Data.TradingDataClient import TradingDataClient
from Model.SimpleMovingAverageCalculator import SimpleMovingAverageCalculator
from Model.ExponentialMovingAverageCalculator import ExponentialMovingAverageCalculator
from typing import NamedTuple, Any

class IndicatorInfo(NamedTuple):
    windowSize: int
    description: str
    calculator: Any

config = configparser.ConfigParser()
config.read('dev.ini')

apiKey: str = config['massive']['ApiKey']

massiveClient = massive.RESTClient(api_key=apiKey)
throttledMassiveClient = ThrottledMassiveClient(12, massiveClient)

dbFileLocation: str = config['database']['DatabaseFileLocation']

dbClient = TradingDataClient(dbFileLocation)
dbClient.ensureSeeded()

startDate = datetime.date.fromisoformat("2024-01-01")
endDate = datetime.date.fromisoformat("2024-12-31")

calculators = [
    IndicatorInfo(15, "15 Day EMA", ExponentialMovingAverageCalculator()),
    IndicatorInfo(50, "50 Day EMA", ExponentialMovingAverageCalculator())]

dates = []
closes = []
indicators = []

date = startDate

while date < endDate:
    ticker = dbClient.getDailyTicker("AAPL", date)
    date += datetime.timedelta(days=1)
    
    if not ticker:
        continue
    
    dates.append(date)
    closes.append(ticker.close)
    
dataCount = len(dates)

for indicatorInfo in calculators:
    
    calculatedData = [None]*dataCount
    
    windowStart = 0
    windowEnd = indicatorInfo.windowSize
    
    while windowEnd < dataCount:
        
        window = closes[windowStart:windowEnd]
        
        result = indicatorInfo.calculator.calculate(window)
        
        calculatedData[windowEnd - 1] = result
        windowStart += 1
        windowEnd += 1
        
    indicators.append((indicatorInfo.description, calculatedData))

    
fig, ax = plt.subplots(layout='constrained')
ax.plot(dates, closes, label="Daily close price")

for indicator in indicators:
    ax.plot(dates, indicator[1], label=indicator[0])

plt.legend(loc="upper left")
plt.show()