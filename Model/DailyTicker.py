import datetime

from typing import NamedTuple

class DailyTicker(NamedTuple):
    symbol: str
    date: datetime.date
    open: float
    close: float
    high: float
    low: float
    volume: int