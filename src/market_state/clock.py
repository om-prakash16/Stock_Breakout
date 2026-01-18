from datetime import datetime
import pytz

class MarketClock:
    TIMEZONE = pytz.timezone('Asia/Kolkata')
    
    @classmethod
    def now(cls) -> datetime:
        return datetime.now(cls.TIMEZONE)
    
    @classmethod
    def get_time_tuple(cls):
        """Returns (hour, minute) of current time in market timezone."""
        now = cls.now()
        return now.hour, now.minute
