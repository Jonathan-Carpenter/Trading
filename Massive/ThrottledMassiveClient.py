import datetime
import massive
import time

class ThrottledMassiveClient:
    
    def __init__(self, secondsPerFetch: int, innerClient: massive.RESTClient):
        
        self.secondsPerFetch = secondsPerFetch
        self.innerClient = innerClient
        
    def getTickerDetails(self, ticker: str, startDate: datetime.date, endDate: datetime.date):
        
        assert startDate < endDate
        
        return self.__doClientOperation(
            lambda currentDate: self.innerClient.get_ticker_details(ticker, date=currentDate.isoformat()),
            startDate,
            lambda _, currentDate: currentDate == endDate,
            lambda _, currentDate: currentDate + datetime.timedelta(days=1),
            lambda currentDate: print(f'Querying {ticker} on {currentDate.isoformat()}')
        )
    
    def __doClientOperation(self, clientFunc, state, shouldEndFunc, resolveStateFunc, logFunc):
        
        shouldContinue = True
        results = []
        
        while shouldContinue:
            
            logFunc(state)
            
            result = clientFunc(state)
            results.append(result)
            
            shouldContinue = not shouldEndFunc(result, state)
            state = resolveStateFunc(result, state)
            
            if shouldContinue:
                time.sleep(self.secondsPerFetch)
            
        return results