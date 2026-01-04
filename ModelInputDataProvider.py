import datetime

import numpy as np
from tqdm import tqdm
from Data.TradingDataClient import TradingDataClient
from Model.DailyTicker import DailyTickerOpenCloseSummary


class ModelInputDataProvider:
    
    def __init__(self, dataClient: TradingDataClient):
        self.dataClient = dataClient
        
    def getData(self, tickerIds: list[str], startDate: datetime.date, endDate: datetime.date, windowSize: int, predictionLookAhead: int):
        
        tickerIds = [t for t in tickerIds if self.dataClient.isDailyTickerDataContiguousOverRange(t, startDate, endDate)]
        
        sampleTickers = self.dataClient.getDailyTickers(tickerIds[0], startDate, endDate)
        tickerCount = len(tickerIds)
        
        tickerIndex = 0
        lastPredictionBound = len(sampleTickers) - predictionLookAhead
        
        dates = [datetime.date.fromisoformat(date) for date in sampleTickers[windowSize : lastPredictionBound, 0]]
        closes = sampleTickers[windowSize : lastPredictionBound, 2]
        
        perTickerInputCount = sampleTickers.shape[0] - windowSize - predictionLookAhead
        perInputLength = 5 * windowSize # 5 = open, close, high, low, volume
        
        inputs = np.zeros((perTickerInputCount * tickerCount, perInputLength))
        labels = np.zeros((perTickerInputCount * tickerCount, 1))
        
        skippedTickerCount = 0
        
        if len(tickerIds) > 10:
            print("\n###\nForming model input data from ticker data\n###\n")
            tickerIds = tqdm(tickerIds, leave=False)

        for tickerId in tickerIds:
            
            tickers = self.dataClient.getDailyTickers(tickerId, startDate, endDate)
            
            if tickers.shape[0] != sampleTickers.shape[0]:
                skippedTickerCount += 1
                continue
            
            tickerBaseIndex = tickerIndex * perTickerInputCount
            
            # First windowSize elements do not have necessary data to make a predication
            # Last predictionLookAhead elements do not have necessary data to calculate loss
            for i in range(perTickerInputCount):
                labels[tickerBaseIndex + i] = (tickers[i + windowSize + predictionLookAhead][2] / tickers[i + windowSize][2]) * 100 # set label with percentage look ahead change
            
            for i in range(perTickerInputCount):
                                
                windowTickers = tickers[i : i + windowSize, 1 : ]
                
                inputs[tickerBaseIndex + i] = windowTickers.flatten() # input is backwards looking window of measured info
                
            tickerIndex += 1
            
        skippedInputCount = skippedTickerCount * perTickerInputCount
        
        if (skippedTickerCount > tickerCount / 2):
            print("Error: High number of skipped tickers.")
            exit()

        if skippedInputCount > 0:
            inputs = inputs[:-skippedInputCount, :]
            labels = labels[:-skippedInputCount, :]
            
        # print(f"Inputs: {inputs.shape}")
        # print(f"Labels: {labels.shape}")
        # print(f"Dates: {len(dates)}")
        # print(f"Closes: {closes.shape}")
            
        # print(labels)
        # print(sum(labels))
        # exit()
            
        if ((inputs.shape[0] != labels.shape[0] != len(dates) != closes.shape[0]) or
            (inputs.shape[1] != perInputLength)):
            
            print("Error: Shape mismatch when fetching data.")
            print(inputs.shape)
            print(labels.shape)
            print(len(dates))
            print(closes.shape)
            
            exit()
        
        return (inputs, labels, dates, closes)