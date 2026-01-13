import datetime
import numpy as np
import matplotlib.pyplot as plt

from tqdm import tqdm
from imblearn.over_sampling import RandomOverSampler
from scipy.stats import norm

from Data.TradingDataClient import TradingDataClient
from Model.Indicators.AverageCalculator import AverageCalculator
from Model.Indicators.BollingerBandsCalculator import BollingerBandsCalculator
from Model.Indicators.MovingAverageConvergenceDivergenceCalculator import MovingAverageConvergenceDivergenceCalculator

class ModelInputDataProvider:
    
    def __init__(
        self,
        dataClient: TradingDataClient,
        averageCalculators: list[AverageCalculator],
        bandCalculators: list[BollingerBandsCalculator],
        macdCalculators: list[MovingAverageConvergenceDivergenceCalculator]):
        
        self.dataClient = dataClient
        self.averageCalculators = averageCalculators
        self.bandCalculators = bandCalculators
        self.macdCalculators = macdCalculators
        
    def getLabelOversamplingClass(self, label: float, oversamplingThresholds: list[float]):
        
        for i in range(len(oversamplingThresholds)):
            if label > oversamplingThresholds[i]:
                return i
            
        return len(oversamplingThresholds)
        
    def getData(
        self,
        tickerIds: list[str],
        startDate: datetime.date,
        endDate: datetime.date,
        windowSize: int,
        predictionLookAhead: int,
        oversample: bool = False,
        plotDistribution: bool = False):
        
        tickerIds = [t for t in tickerIds if self.dataClient.isDailyTickerDataContiguousOverRange(t, startDate, endDate)]
        
        sampleTickers = self.dataClient.getDailyTickers(tickerIds[0], startDate, endDate)
        tickerCount = len(tickerIds)
        
        tickerIndex = 0
        lastPredictionBound = len(sampleTickers) - predictionLookAhead
        
        dates = [datetime.date.fromisoformat(date) for date in sampleTickers[windowSize : lastPredictionBound, 0]]
        closes = sampleTickers[windowSize : lastPredictionBound, 2]
        
        columnsPerAverageCalculator = 1
        columnsPerBandCalculator = 3 # 3 = lower, average, upper
        columnsPerMacdCalculator = 1
        
        calculatedDataColumns = (
            (len(self.averageCalculators) * columnsPerAverageCalculator) +
            (len(self.bandCalculators) * columnsPerBandCalculator) +
            (len(self.macdCalculators) * columnsPerMacdCalculator))
        
        columnsPerRawTicker = 6 # 6 = date, open, close, high, low, volume
        columnsPerTickerWithData = columnsPerRawTicker + calculatedDataColumns
        
        perTickerInputCount = sampleTickers.shape[0] - windowSize - predictionLookAhead
        perInputLength = (columnsPerTickerWithData - 1) * windowSize # -1 for removal of date column
        
        inputs = np.zeros((perTickerInputCount * tickerCount, perInputLength))
        labels = np.zeros((perTickerInputCount * tickerCount, 1))
        oversamplingLabels = np.zeros((perTickerInputCount * tickerCount, 1))
        
        skippedTickerCount = 0
        
        if len(tickerIds) > 10:
            print("\n###\nForming model input data from ticker data\n###\n")
            print(f"Per ticker input count: {perTickerInputCount}")
            print(f"Per input length: {perInputLength}")
            print(f"Ticker count: {tickerCount}")
            print(f"Inputs matrix shape: {inputs.shape}")
            print("")
            
            tickerIds = tqdm(tickerIds, leave=False)

        for tickerId in tickerIds:
            
            rawDailyTickers = self.dataClient.getDailyTickers(tickerId, startDate, endDate)
            
            if rawDailyTickers.shape != sampleTickers.shape:
                skippedTickerCount += 1
                continue
            
            tickers = np.zeros((rawDailyTickers.shape[0], columnsPerTickerWithData))
            
            # print(f"Tickers with data: {tickers.shape}")
            
            tickers[ : , 1 : 6] = rawDailyTickers[ : , 1 : ]
            tickerCloses = tickers[:, 2]
            
            columnIndex = 6 # after 5 raw data columns
            
            for averageCalculator in self.averageCalculators:
                averagesIndicatorData = averageCalculator.calculate(tickerCloses)
                tickers[:, columnIndex] = averagesIndicatorData
                columnIndex += columnsPerAverageCalculator
                
            for bandCalculator in self.bandCalculators:
                bandIndicatorData = bandCalculator.calculate(tickerCloses)
                tickers[:, columnIndex : columnIndex + columnsPerBandCalculator] = bandIndicatorData
                columnIndex += columnsPerBandCalculator
                
            for macdCalculator in self.macdCalculators:
                macdSignalData = macdCalculator.calculate(tickerCloses)[ : , 2 ] # just take the signal; we already have EMAs
                tickers[:, columnIndex] = macdSignalData
                columnIndex += columnsPerMacdCalculator
            
            #    0       1       2        3       4      5         6             
            #    date    open    close    high    low    volume    avg1    avg2    band1a    band1b    band1c    macd_sig1
            #    .       .       .        .       .      .         .       .       .         .         .         .
            #    .       .       .        .       .      .         .       .       .         .         .         .
            #    .       .       .        .       .      .         .       .       .         .         .         .
            #    .       .       .        .       .      .         .       .       .         .         .         .
            
            tickerBaseIndex = tickerIndex * perTickerInputCount
            
            # First windowSize elements do not have necessary data to make a prediction
            # Last predictionLookAhead elements do not have necessary data to calculate loss
            for i in range(perTickerInputCount):
                label = (tickers[i + windowSize + predictionLookAhead][2] / tickers[i + windowSize][2]) * 100 # set label with percentage look ahead change
                labels[tickerBaseIndex + i] = label
            
            for i in range(perTickerInputCount):
                                
                windowTickers = tickers[i : i + windowSize, 1 : ] # 0th column is date
                
                # print(f"Window tickers: {windowTickers.shape}")
                
                inputs[tickerBaseIndex + i] = windowTickers.flatten() # input is backwards looking window of measured info
                
            tickerIndex += 1
            
        skippedInputCount = skippedTickerCount * perTickerInputCount
        
        if (skippedTickerCount > tickerCount / 2):
            print("Error: High number of skipped tickers.")
            exit()

        if skippedInputCount > 0:
            inputs = inputs[:-skippedInputCount, :]
            labels = labels[:-skippedInputCount, :]
            oversamplingLabels = oversamplingLabels[:-skippedInputCount, :]
        
        mu, std = norm.fit(labels)
        
        oversamplingThresholds = []
        
        for i in range(5, 96, 5):
            confidence = (100 - i) / 100
            value = norm.ppf(confidence, loc=100, scale=std)
            oversamplingThresholds.append(value)
            
        for i in range(len(labels)):
            oversamplingLabels[i] = self.getLabelOversamplingClass(labels[i], oversamplingThresholds)
        
        if plotDistribution:
            bins = list(reversed(oversamplingThresholds))
            
            _, ax = plt.subplots(1)
            
            ax.hist(labels, bins=bins, label="Original Samples", alpha=0.3)
            ax.set_xlabel("Label Value")
            ax.set_ylabel("log(Label Count)")
            
            normalX = np.arange(oversamplingThresholds[-1], oversamplingThresholds[0], 0.5)
            normalY = norm.pdf(normalX, mu, std)
            normalYOversampling = norm.pdf(normalX, 100, std)
            
            normalAxis = ax.twinx()
            
            normalAxis.plot(normalX, normalY, label="Normal Distribution Fitted To Original Samples")
            normalAxis.plot(normalX, normalYOversampling, label="Normal Distribution For Oversampling")
            
            normalAxis.legend(loc="upper right")
            
        if oversample:            
            inputs = np.hstack((inputs, labels))
            
            oversampler = RandomOverSampler()
            inputs, _ = oversampler.fit_resample(inputs, oversamplingLabels)
            
            labels = inputs[:, -1]
            inputs = inputs[:, : -1]
            
            if plotDistribution:
                ax.hist(labels, bins=bins, label="Samples After Random Oversampling", alpha=0.3)
                ax.legend(loc="upper left")
                ax.grid()
            
        if plotDistribution:
            plt.show()
        
        print(f"Inputs: {inputs.shape}")
        print(f"Labels: {labels.shape}")
        print(f"Dates: {len(dates)}")
        print(f"Closes: {closes.shape}")
        
        return (inputs, labels, dates, closes)