from dataclasses import dataclass
from datetime import date, datetime
from src.market_state.enums import MarketState
from src.market_state.clock import MarketClock
from src.market_state.calendar import ExchangeCalendarService

@dataclass
class MarketContext:
    state: MarketState
    effective_trade_date: date
    run_timestamp: datetime
    description: str

    @property
    def is_market_open(self) -> bool:
        return self.state == MarketState.OPEN


class MarketStateResolver:
    def __init__(self):
        self.clock = MarketClock
        self.calendar = ExchangeCalendarService()
        
    def resolve(self) -> MarketContext:
        now = self.clock.now()
        today = now.date()
        current_time = (now.hour, now.minute)
        
        # 1. Check Weekend
        if self.calendar.is_weekend(today):
            last_date = self.calendar.get_last_session_date(today)
            return MarketContext(
                state=MarketState.WEEKEND,
                effective_trade_date=last_date,
                run_timestamp=now,
                description=f"Weekend. Using last session: {last_date}"
            )
            
        # 2. Check Holiday (if not weekend)
        if not self.calendar.is_trading_day(today):
            last_date = self.calendar.get_last_session_date(today)
            return MarketContext(
                state=MarketState.HOLIDAY,
                effective_trade_date=last_date,
                run_timestamp=now,
                description=f"Exchange Holiday. Using last session: {last_date}"
            )
            
        # 3. It is a Trading Day. Check Time.
        # 09:00 - 09:15 : Pre-Open
        # 09:15 - 15:30 : Open
        # 15:30 - 16:00 : Post-Close
        # > 16:00       : Closed (Day Done)
        # < 09:00       : Closed (Pre-Market)
        
        hh, mm = current_time
        time_val = hh * 100 + mm
        
        if time_val < 900:
            # Before Market (Morning of trading day) -> Use PREVIOUS day data
            # effectively, market hasn't opened, so we look at yesterday's close.
            # But wait, if we are running morning scan, we probably want yesterday's data.
            # get_last_session_date(today) returns today because it IS in schedule.
            # So we must manually subtract one day and find last session.
            prev_day = today - timedelta(days=1)
            last_date = self.calendar.get_last_session_date(prev_day)
            return MarketContext(
                state=MarketState.CLOSED,
                effective_trade_date=last_date,
                run_timestamp=now,
                description=f"Pre-Market Morning. Using last session: {last_date}"
            )
            
        elif 900 <= time_val < 915:
            return MarketContext(
                state=MarketState.PRE_OPEN,
                effective_trade_date=today, # Pre-open quotes coming in
                run_timestamp=now,
                description="Pre-Open Session"
            )
            
        elif 915 <= time_val < 1530:
            return MarketContext(
                state=MarketState.OPEN,
                effective_trade_date=today,
                run_timestamp=now,
                description="Market Open (Live)"
            )
            
        elif 1530 <= time_val < 1600:
            # Post Close session, data is finalizing. Treat as Today.
            return MarketContext(
                state=MarketState.POST_CLOSE,
                effective_trade_date=today,
                run_timestamp=now,
                description="Post-Close Session"
            )
            
        else: # >= 1600
            # Market Closed for the day. Data is final.
            return MarketContext(
                state=MarketState.CLOSED,
                effective_trade_date=today,
                run_timestamp=now,
                description="Market Closed (EOD)"
            )
