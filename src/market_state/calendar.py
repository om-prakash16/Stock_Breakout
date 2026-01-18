import pandas_market_calendars as mcal
from datetime import date, timedelta
from typing import Optional

class ExchangeCalendarService:
    def __init__(self):
        # XBOM covers NSE/BSE holidays generally
        try:
            self.cal = mcal.get_calendar('XBOM')
        except:
            self.cal = mcal.get_calendar('NYSE') # Fallback if setup issue, though unlikely
            
    def is_trading_day(self, check_date: date) -> bool:
        schedule = self.cal.schedule(start_date=check_date, end_date=check_date)
        return not schedule.empty

    def is_weekend(self, check_date: date) -> bool:
        # 5=Saturday, 6=Sunday
        return check_date.weekday() >= 5

    def get_last_session_date(self, reference_date: date) -> date:
        """Finds the last confirmed trading session date."""
        # Look back up to 20 days
        start = reference_date - timedelta(days=20)
        schedule = self.cal.schedule(start_date=start, end_date=reference_date)
        if schedule.empty:
            return reference_date # Should fail safely
        
        # If reference_date is IN the schedule, it means it's a trading day.
        # But is the session over? This method strictly returns LAST VALID session date.
        # If today is trading day, it returns Today. (MarketStateResolver decides if we use Today or Prev based on time)
        return schedule.index[-1].date()
