import configparser
import datetime
import matplotlib.pyplot as plt

from Data.TradingDataClient import TradingDataClient
from Model.Indicators.IdentityCalculator import IdentityCalculator
from Model.Indicators.ExponentialMovingAverageCalculator import ExponentialMovingAverageCalculator

config = configparser.ConfigParser()
config.read('dev.ini')

dbFileLocation: str = config['database']['DatabaseFileLocation']

dbClient = TradingDataClient(dbFileLocation)
dbClient.ensureSeeded()

startDate = datetime.date.fromisoformat("2024-01-01")
endDate = datetime.date.fromisoformat("2024-12-21")

tickerId = "META"

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

for calculator in calculators:
    indicatorData = calculator.calculate(closes)
    indicators.append(indicatorData)
    
    
fig, ax = plt.subplots(label=f"Close price of {tickerId} with Exponential Moving Averages", layout='constrained')

for indicator in indicators:
    ax.plot(dates, indicator.data, label=indicator.description)

plt.legend(loc="upper left")
plt.show()