from enum import Enum

class MarketState(Enum):
    PRE_OPEN = "PRE_OPEN"     # 09:00 - 09:15
    OPEN = "OPEN"             # 09:15 - 15:30
    POST_CLOSE = "POST_CLOSE" # 15:30 - 16:00
    CLOSED = "CLOSED"         # After 16:00 or Before 09:00 (on trading day)
    WEEKEND = "WEEKEND"       # Sat/Sun
    HOLIDAY = "HOLIDAY"       # Exchange Holiday
    UNKNOWN = "UNKNOWN"
