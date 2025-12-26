import datetime
import uuid

from typing import NamedTuple

class TradingSignal(NamedTuple):
    price: float
    date: datetime.date
    detectorId: uuid.UUID