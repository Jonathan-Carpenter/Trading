import configparser
import massive
import datetime

from Massive.ThrottledMassiveClient import ThrottledMassiveClient
from Data.TradingDataClient import TradingDataClient
from Tickers import Tickers

config = configparser.ConfigParser()
config.read('dev.ini')

apiKey: str = config['massive']['ApiKey']

massiveClient = massive.RESTClient(api_key=apiKey)
throttledMassiveClient = ThrottledMassiveClient(None, massiveClient)

dbFileLocation: str = config['database']['DatabaseFileLocation']

dbClient = TradingDataClient(dbFileLocation)
dbClient.ensureSeeded()

tickerIds = Tickers().sp500tickers()

startDate = datetime.date.fromisoformat('2021-02-01')
endDate = datetime.date.fromisoformat('2024-01-01')

for tickerId in tickerIds:
    
    if dbClient.isDailyTickerDataContiguousOverRange(tickerId, startDate, endDate):
        print(f"Skipping fetch for {tickerId} as previously fetched data appears to be contiguous over the specified range.")
        continue
    
    print("\n###\n###\n###\n")
    
    results = throttledMassiveClient.getTickerOpenCloseSummary(
        tickerId,
        startDate,
        endDate)

    for result in results:
        ticker = dbClient.getDailyTicker(result.symbol, result.date)
        
        if ticker:
            continue
        
        dbClient.addDailyTicker(result)
        
print("\n###\n###\n###\n")
print(f"Fetch complete.\nStart date: {startDate}.\nEnd date: {endDate}.")