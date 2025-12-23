import datetime

from typing import NamedTuple

class TradingSignal(NamedTuple):
    price: float
    date: datetime.date