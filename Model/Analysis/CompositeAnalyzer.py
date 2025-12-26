import datetime
import uuid
from Model.AnalysisResult import AnalysisResult
from Model.Analysis.Analyzer import Analyzer
from Model.Signals.TradingSignal import TradingSignal
from Model.Signals.BuySignal import BuySignal
from Model.Signals.SellSignal import SellSignal

class CompositeAnalyzer(Analyzer):
    
    def __init__(
        self,
        amountInvestedPerTrade: int,
        agreementWindowDays: int,
        agreementThreshold: int,
        analyzers: list[Analyzer]):
        
        super().__init__(amountInvestedPerTrade)
        
        self.agreementWindowDays = agreementWindowDays
        self.agreementThreshold = agreementThreshold
        self.analyzers = analyzers
        self.id = uuid.uuid4()
        
    def analyze(self, dates: list[datetime.date], sourceData: list[float]) -> AnalysisResult:
        
        signalsByDate: dict[datetime.date, list[TradingSignal]] = {}
        
        for date in dates:
            signalsByDate[date] = []
        
        for analyzer in self.analyzers:
            result = analyzer.analyze(dates, sourceData)
            
            for signal in result.actionedSignals:
                signalsByDate[signal.date].append(signal)
            
        windowStart = 0
        windowEnd = self.agreementWindowDays
        
        compositeSignals = []
        
        while windowEnd < len(dates):
            
            windowDates = [dates[windowStart] + datetime.timedelta(days=i) for i in range(self.agreementWindowDays)]
            
            uniqueAnalyzersWithBuySignals = set()
            uniqueAnalyzersWithSellSignals = set()
            
            for date in windowDates:
                
                if date not in signalsByDate:
                    continue
                
                signals = signalsByDate[date]
                
                for signal in signals:
                    if isinstance(signal, BuySignal):
                        # print(signal)
                        uniqueAnalyzersWithBuySignals.add(signal.detectorId)
                        
                    if isinstance(signal, SellSignal):
                        # print(signal)
                        uniqueAnalyzersWithSellSignals.add(signal.detectorId)
                        
            # print(len(uniqueAnalyzersWithBuySignals))
            # print(len(uniqueAnalyzersWithSellSignals))
            # print("\n")
                
            if len(uniqueAnalyzersWithSellSignals) >= self.agreementThreshold:
                # print("Composite sell")
                compositeSignals.append(SellSignal(sourceData[windowEnd], dates[windowEnd], self.id))
                        
            elif len(uniqueAnalyzersWithBuySignals) >= self.agreementThreshold:
                # print("Composite buy")
                compositeSignals.append(BuySignal(sourceData[windowEnd], dates[windowEnd], self.id))
                        
            windowStart += 1
            windowEnd += 1
        
        result = self.simulate(compositeSignals)
        
        return result