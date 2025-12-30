import datetime
import uuid

class TradingSignal():
    
    def __init__(
        self,
        price: float,
        date: datetime.date,
        detectorId: uuid.UUID):
        
        self.price = price
        self.date = date
        self.detectorId = detectorId