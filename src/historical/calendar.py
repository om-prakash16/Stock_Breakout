import pandas_market_calendars as mcal
from datetime import date, timedelta, datetime
import pandas as pd
from typing import Optional

class MarketCalendarService:
    def __init__(self):
        # XBOM is Bombay Stock Exchange, which follows same holidays as NSE
        try:
            self.cal = mcal.get_calendar('XBOM')
        except Exception:
            # Fallback or generic if XBOM specific not found (should exist)
            print("Warning: XBOM calendar not found, falling back to NYSE for test or generic.") 
            self.cal = mcal.get_calendar('NYSE') # Dangerous fallback, but better than crash. 
            # Ideally we'd define custom if missing.
            
    def is_trading_day(self, check_date: date) -> bool:
        schedule = self.cal.schedule(start_date=check_date, end_date=check_date)
        return not schedule.empty

    def get_last_trading_day(self, from_date: date = None) -> date:
        """
        Returns the last valid trading day relative to from_date (inclusive).
        If today is trading day and market is closed (evening), it counts.
        If today is trading day and market is OPEN, yfinance might not have full data yet.
        However, the requirement says 'Auto-detect last trading session'.
        """
        if from_date is None:
            from_date = date.today()
            
        # Get schedule for last 15 days to be safe
        start_date = from_date - timedelta(days=15)
        schedule = self.cal.schedule(start_date=start_date, end_date=from_date)
        
        if schedule.empty:
            return start_date # Should not happen
            
        return schedule.index[-1].date()
        
    def get_market_status(self) -> dict:
        today = date.today()
        is_open = self.is_trading_day(today)
        last_trading = self.get_last_trading_day(today)
        
        return {
            "is_trading_day": is_open,
            "last_valid_day": last_trading,
            "today": today
        }
