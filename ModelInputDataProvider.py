import datetime

import numpy as np
from tqdm import tqdm
from Data.TradingDataClient import TradingDataClient
from Model.DailyTicker import DailyTickerOpenCloseSummary


class ModelInputDataProvider:
    
    def __init__(self, dataClient: TradingDataClient):
        self.dataClient = dataClient
        
    def getData(self, tickerIds: list[str], startDate: datetime.date, endDate: datetime.date, windowSize: int, predictionLookAhead: int):
        
        if len(tickerIds) > 10:
            print("\n###\nForming model input data from ticker data\n###\n")
            tickerIds = tqdm(tickerIds)
        
        first = True
        inputs = None
        labels = None
        
        dates = []
        closes = []

        for tickerId in tickerIds:
            
            if not self.dataClient.isDailyTickerDataContiguousOverRange(tickerId, startDate, endDate):
                continue
            
            tickers: list[DailyTickerOpenCloseSummary] = []
            
            date = startDate
            
            while date < endDate:
                ticker = self.dataClient.getDailyTicker(tickerId, date)
                date += datetime.timedelta(days=1)
                
                if not ticker:
                    continue
                
                dates.append(date)
                closes.append(ticker.close)
                tickers.append(ticker)
                
            sampleCount = len(tickers) - windowSize
            
            if sampleCount < 0:
                continue
            
            sampleLength = windowSize * 5 # 5 = len( [ t.open, t.close, t.high, t.low, t.volume ] )
            
            tickerSamples = np.zeros((sampleCount, sampleLength))
            tickerLabels = np.zeros((sampleCount, 1))
                
            rawTickers: list[list[float]] = [
                [t.open, t.close, t.high, t.low, t.volume]
                for t in tickers]
                
            windowStart = 0
            windowEnd = windowSize
            lookAhead = windowEnd + predictionLookAhead
            
            while lookAhead < len(rawTickers):
                
                windowTickers = rawTickers[windowStart:windowEnd]
                label = tickers[lookAhead].close
                
                windowSample = np.array(windowTickers).flatten()
                
                tickerSamples[windowStart] = windowSample
                tickerLabels[windowStart] = label
                
                windowStart += 1
                windowEnd += 1
                lookAhead += 1
                
            if first:
                inputs = tickerSamples
                labels = tickerLabels
            else:
                inputs = np.vstack((inputs, tickerSamples))
                labels = np.vstack((labels, tickerLabels))
                
            first = False
            
        return (inputs, labels, dates, closes)