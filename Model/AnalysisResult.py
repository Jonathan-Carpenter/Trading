from typing import NamedTuple

from Model.Signals.TradingSignal import TradingSignal

class AnalysisResult(NamedTuple):
    totalProfit: int
    actionedSignals: list[TradingSignal]