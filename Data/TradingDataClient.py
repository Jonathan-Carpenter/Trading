import sqlite3
import datetime

import pandas as pd

from Model.DailyTicker import DailyTickerOpenCloseSummary

class TradingDataClient:
    def __init__(self, dbFileLocation: str):
        self.dbFileLocation = dbFileLocation
        
    def ensureSeeded(self):
        connection = sqlite3.connect(self.dbFileLocation)
        cursor = connection.cursor()
        
        results = cursor.execute("SELECT name FROM sqlite_master")
        schemaRecords = [result[0] for result in results.fetchall()]
        
        if "tickers" in schemaRecords:
            return
        
        print("It looks like your DB has not been seeded. Seed it now? (Y/N)")
        response = input()
        
        if response != "Y":
            print("Skipped DB seed.")
            return
        
        print("Seeding DB now...")

        cursor.execute("CREATE TABLE tickers(symbol, date, open, close, high, low, volume)")
        cursor.execute("CREATE UNIQUE INDEX 'ticker_index' ON 'tickers' ('symbol', 'date')")
        
        connection.close()
        
        print("DB seeding completed.")
        
    def getAllDailyTickerSymbols(self) -> list[str]:
        connection = sqlite3.connect(self.dbFileLocation)
        cursor = connection.cursor()
        
        results = cursor.execute("SELECT DISTINCT symbol FROM tickers")
        tickers = results.fetchall()
        
        connection.close()
        
        return [ticker[0] for ticker in tickers]
        
    def addDailyTicker(self, ticker: DailyTickerOpenCloseSummary):        
        connection = sqlite3.connect(self.dbFileLocation)
        cursor = connection.cursor()
        
        cursor.execute(
            "INSERT INTO tickers VALUES(?, ?, ?, ?, ?, ?, ?)",
            (
                ticker.symbol,
                ticker.date,
                ticker.open,
                ticker.close,
                ticker.high,
                ticker.low,
                ticker.volume))
        
        connection.commit()
        connection.close()
        
    def getDailyTickers(self, symbol: str, startDate: datetime.date, endDate: datetime.date):
        connection = sqlite3.connect(self.dbFileLocation)
        
        dataframe = pd.read_sql_query(
            "SELECT date, open, close, high, low, volume FROM tickers WHERE symbol = ? AND date >= ? AND date < ? ORDER BY date ASC",
            params=(symbol, startDate, endDate),
            con=connection)
        
        connection.close()
        
        npArray = dataframe.to_numpy()
        
        return npArray
        
    def getDailyTicker(self, symbol: str, date: datetime.date) -> DailyTickerOpenCloseSummary:
        connection = sqlite3.connect(self.dbFileLocation)
        cursor = connection.cursor()
        
        results = cursor.execute("SELECT symbol, date, open, close, high, low, volume FROM tickers WHERE symbol = ? AND date = ?", (symbol, date))
        ticker = results.fetchone()
        
        connection.close()
        
        if not ticker:
            return None
        
        return DailyTickerOpenCloseSummary(
            ticker[0],
            datetime.date.fromisoformat(ticker[1]),
            ticker[2],
            ticker[3],
            ticker[4],
            ticker[5],
            ticker[6])
        
    def isDailyTickerDataContiguousOverRange(self, symbol: str, startDate: datetime.date, endDate: datetime.date) -> bool:
        connection = sqlite3.connect(self.dbFileLocation)
        cursor = connection.cursor()
        
        results = cursor.execute("SELECT symbol, date, open, close, high, low, volume FROM tickers WHERE symbol = ? ORDER BY date", (symbol,))
        tickers = results.fetchall()
        connection.close()
        
        tickerDatesInRange = []
        
        for ticker in tickers:
            date = datetime.date.fromisoformat(ticker[1])
            
            if (date >= startDate) and (date <= endDate):
                tickerDatesInRange.append(date)
        
        if (not tickerDatesInRange) or (endDate - tickerDatesInRange[-1] > datetime.timedelta(days=4)):
            return False
        
        previousDate = tickerDatesInRange[0]
        
        for i in range(1, len(tickerDatesInRange)):
            date = tickerDatesInRange[i]
            
            if date - previousDate > datetime.timedelta(days=4):
                return False
            
            previousDate = date
        
        return True