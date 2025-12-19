import configparser
import massive
import datetime
import time
import csv

def getTickerDetails(client: massive.RESTClient, dateString: str) -> dict[str, str]:
    # Seed results with date on the left
    details = { 'date': dateString }
    ignoredFields = { 'description', 'branding' }
    
    results = client.get_ticker_details(ticker='AAPL', date=dateString, raw=True).json()['results']
    
    for key, value in results.items():
        if key in ignoredFields:
            continue
        
        details[key] = value
    
    return details

config = configparser.ConfigParser()
config.read('dev.ini')

apiKey: str = config['massive']['ApiKey']

massiveClient = massive.RESTClient(api_key=apiKey)

stockTickers = massiveClient.get_ticker_details('AAPL')
date: datetime.date = datetime.date.today()

csvFileName = './AAPL-Apple.csv'

for i in range(10000):
    dateString = date.isoformat()
    
    print(f'\nQuerying AAPL ticker on {dateString}')
    
    tickerDetails = getTickerDetails(massiveClient, dateString)
    
    with open(csvFileName, 'a', newline='') as file:
        
        csvWriter = csv.DictWriter(file, tickerDetails.keys())
        
        if i == 0:
            csvWriter.writeheader()
        
        csvWriter.writerow(tickerDetails)
    
    date = date - datetime.timedelta(days=1)
    
    time.sleep(12)