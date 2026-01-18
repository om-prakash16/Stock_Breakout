import yfinance as yf
import pandas as pd
from datetime import date, timedelta
from typing import Optional, List
from src.historical.schema import HistoricalRecord

class HistoricalDataFetcher:
    def __init__(self):
        pass
        
    def _get_yfinance_ticker(self, symbol: str, exchange: str) -> str:
        if exchange == 'NSE':
            return f"{symbol}.NS"
        elif exchange == 'BSE':
            return f"{symbol}.BO"
        return symbol

    def fetch_history(self, symbol: str, exchange: str, start_date: Optional[date] = None, end_date: Optional[date] = None, period: str = "5y") -> Optional[pd.DataFrame]:
        """
        Fetches historical data for a single stock.
        """
        ticker_symbol = self._get_yfinance_ticker(symbol, exchange)
        
        try:
            # yfinance download
            # using 'auto_adjust=True' to get adjusted OHLC? 
            # Request says "OHLCV", usually for breakout detection we want Adjusted Close for longterm, 
            # but standard OHLC for breakout levels. Breakouts are usually on raw price action?
            # Actually, standard practice for Technical Analysis is ADJUSTED for splits, but maybe NOT for dividends depending on strategy.
            # Let's use auto_adjust=True (default is usually False in older versions, False handles splits better in some contexts? No, auto_adjust=True is simpler).
            # Wait, breakout at 52-week high needs real levels. If a stock split, raw prices drop, adjusted back-adjusts past. 
            # Adjusted data is MANDATORY for consistent breakouts over long periods (5y).
            
            ticker = yf.Ticker(ticker_symbol)
            
            # Efficient fetching
            if start_date:
                df = ticker.history(start=start_date, end=end_date, auto_adjust=True)
            else:
                df = ticker.history(period=period, auto_adjust=True)
                
            if df.empty:
                return None
                
            # Normalize
            df = df.reset_index()
            
            # Ensure columns exist (Date, Open, High, Low, Close, Volume)
            # yfinance returns: Date (index), Open, High, Low, Close, Volume, Dividends, Stock Splits
            
            rename_map = {
                'Date': 'trade_date',
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            }
            df = df.rename(columns=rename_map)
            
            # Filter cols
            cols = ['trade_date', 'open', 'high', 'low', 'close', 'volume']
            df = df[cols].copy()
            
            # Convert date
            df['trade_date'] = pd.to_datetime(df['trade_date']).dt.date
            
            # Add metadata columns required by schema (filled by Service usually, but we can structure here)
            df['symbol'] = symbol
            df['exchange'] = exchange
            
            return df
            
        except Exception as e:
            print(f"Error fetching {ticker_symbol}: {e}")
            return None

    def fetch_batch(self, tasks: List[tuple]) -> List[pd.DataFrame]:
        # yfinance generic batch download is faster but requires list of tickers
        # However, we need to map results back to exchange/symbol.
        # For robustness, we implement per-ticker fetch here or investigate yf.download(tickers=...)
        # yf.download is faster for bulk.
        # But we have mix of NSE and BSE. 
        # Detailed implementation: Let's stick to single fetch for simplicity and robustness in Phase 2 
        # unless 3000 stocks is too slow. 3000 requests might take ~10 mins with threading.
        # We will use threading in the Service layer.
        pass
