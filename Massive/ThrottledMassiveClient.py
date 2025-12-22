import datetime
import massive
import time

from Model.DailyTicker import DailyTicker

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
            lambda currentDate: print(f'Querying details for {ticker} on {currentDate.isoformat()}')
        )
        
    def getTickerSummary(self, ticker: str, startDate: datetime.date, endDate: datetime.date):
        
        assert startDate < endDate
            
        def getSummary(currentDate):
            try:
                response = self.innerClient.get_daily_open_close_agg(ticker, date=currentDate.isoformat())
                return DailyTicker(ticker, currentDate, response.open, response.close, response.high, response.low, response.volume)
            
            except massive.exceptions.BadResponse as badResponseException:
                print(f"Failed to get open-close summary for {ticker} on {currentDate.isoformat()} due to a bad response. The error will be ignored. Exception details:\n{badResponseException}")
                return None
        
        return self.__doClientOperation(
            getSummary,
            startDate,
            lambda _, currentDate: currentDate == endDate,
            lambda _, currentDate: currentDate + datetime.timedelta(days=1),
            lambda currentDate: print(f'Querying open-close summary for {ticker} on {currentDate.isoformat()}')
        )
    
    def __doClientOperation(self, clientFunc, state, shouldEndFunc, resolveStateFunc, logFunc):
        
        shouldContinue = True
        
        while shouldContinue:
            
            logFunc(state)
            
            result = clientFunc(state)
            
            # TODO: Make this less gross and single-threaded with the delay below.
            if result:
                yield result
            
            shouldContinue = not shouldEndFunc(result, state)
            state = resolveStateFunc(result, state)
            
            if shouldContinue:
                time.sleep(self.secondsPerFetch)