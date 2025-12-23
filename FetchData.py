import configparser
import massive
import datetime
import time

from Massive.ThrottledMassiveClient import ThrottledMassiveClient
from Data.TradingDataClient import TradingDataClient

config = configparser.ConfigParser()
config.read('dev.ini')

apiKey: str = config['massive']['ApiKey']

massiveClient = massive.RESTClient(api_key=apiKey)
throttledMassiveClient = ThrottledMassiveClient(12, massiveClient)

dbFileLocation: str = config['database']['DatabaseFileLocation']

dbClient = TradingDataClient(dbFileLocation)
dbClient.ensureSeeded()

tickers = ["META", "BA", "BLK", "BAC", "MSFT", "ROK", "TTWO", "VRTX"]

for ticker in tickers:
    
    results = throttledMassiveClient.getTickerOpenCloseSummary(
        ticker,
        datetime.date.fromisoformat('2024-01-01'),
        datetime.date.fromisoformat('2025-12-20'))

    for result in results:
        dbClient.addDailyTicker(result)
        
    time.sleep(12)