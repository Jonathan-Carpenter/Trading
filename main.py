import configparser
import massive
import datetime

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

results = throttledMassiveClient.getTickerSummary(
    'AAPL',
    datetime.date.fromisoformat('2025-01-01'),
    datetime.date.fromisoformat('2025-12-20'))

for result in results:
    dbClient.addDailyTicker(result)