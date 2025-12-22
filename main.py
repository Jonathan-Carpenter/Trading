import configparser
import massive
import datetime

from Massive.ThrottledMassiveClient import ThrottledMassiveClient

config = configparser.ConfigParser()
config.read('dev.ini')

apiKey: str = config['massive']['ApiKey']

massiveClient = massive.RESTClient(api_key=apiKey)
throttledMassiveClient = ThrottledMassiveClient(12, massiveClient)

results = throttledMassiveClient.getTickerDetails(
    'AAPL',
    datetime.date.fromisoformat('2025-12-20'),
    datetime.date.fromisoformat('2025-12-22'))

for result in results:
    print(result)
    print('\n')