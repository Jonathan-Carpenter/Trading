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
throttledMassiveClient = ThrottledMassiveClient(12, massiveClient)

dbFileLocation: str = config['database']['DatabaseFileLocation']

dbClient = TradingDataClient(dbFileLocation)
dbClient.ensureSeeded()

tickerIds = Tickers().sp500tickers()

startDate = datetime.date.fromisoformat('2024-01-01')
endDate = datetime.date.fromisoformat('2025-12-01')

skippedTickers = []

for tickerId in tickerIds:
    
    print("\n###\n###\n###\n")
    
    ticker = dbClient.getLatestDailyTicker(tickerId)
    fetchStartDate = startDate
    
    if ticker:
        print(f"Last-known ticker data found for {tickerId} from {ticker.date}.")
        
        if ticker.date >= endDate:
            print(f"WARNING: Skipping fetching ticker data for {tickerId} as last-known data is more recent than the specified range.")
            
            skippedTickers.append((ticker, "Last-known data is more recent than the specified range."))
            
            continue
        
        if ticker.date > startDate:
            fetchStartDate = ticker.date + datetime.timedelta(days=1)
        
        elif startDate - ticker.date > datetime.timedelta(days=5):
            print(f"WARNING: Skipping fetching ticker data for {tickerId} as it looks like you might have specified a date range which is discontinuous with previously fetched data.")
            
            skippedTickers.append((ticker, "Specified date range is discontinuous with previously fetched data."))
            
            continue
        
        print(f"Beginning fetching data for {tickerId} starting from {fetchStartDate}")
        
    else:
        print(f"No last-known ticker data found for {tickerId}.")
        print(f"Beginning fetching data for {tickerId} starting from beginning of specified range.")
    
    print("...")
    
    results = throttledMassiveClient.getTickerOpenCloseSummary(
        tickerId,
        fetchStartDate,
        endDate)

    for result in results:
        dbClient.addDailyTicker(result)
        
print("\n###\n###\n###\n")
print(f"Fetch complete.\nStart date: {startDate}.\nEnd date: {endDate}.\n\nSkipped the following tickers:\n")

for ticker in skippedTickers:
    print({ticker[0]})
    print(f"Reason for skipping: {ticker[1]}")