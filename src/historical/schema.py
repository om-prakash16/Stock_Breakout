from dataclasses import dataclass
from datetime import date

@dataclass
class HistoricalRecord:
    exchange: str
    symbol: str
    trade_date: date
    open: float
    high: float
    low: float
    close: float
    volume: int
    data_source_date: date
    is_last_trading_day: bool
