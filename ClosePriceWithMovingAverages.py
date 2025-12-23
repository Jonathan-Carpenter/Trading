import configparser
import massive
import datetime
import matplotlib.pyplot as plt
import numpy as np

from Massive.ThrottledMassiveClient import ThrottledMassiveClient
from Data.TradingDataClient import TradingDataClient
from Model.Indicators.IdentityCalculator import IdentityCalculator
from Model.Indicators.ExponentialMovingAverageCalculator import ExponentialMovingAverageCalculator
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
endDate = datetime.date.fromisoformat("2025-11-30")

tickerId = "AAPL"

calculators = [
    IdentityCalculator("Daily close price"),
    ExponentialMovingAverageCalculator(15, "15 Day EMA"),
    ExponentialMovingAverageCalculator(50, "50 Day EMA")]

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
    
dataCount = len(dates)

for calculator in calculators:
    indicatorData = calculator.calculate(closes)
    indicators.append(indicatorData)
    
    
fig, ax = plt.subplots(label=f"Close price of {tickerId} with Exponential Moving Averages", layout='constrained')

for indicator in indicators:
    ax.plot(dates, indicator.data, label=indicator.description)

plt.legend(loc="upper left")
plt.show()