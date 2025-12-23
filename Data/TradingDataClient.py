import sqlite3
import datetime

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
            ticker[1],
            ticker[2],
            ticker[3],
            ticker[4],
            ticker[5],
            ticker[6])