import pandas as pd
import numpy as np
from typing import List, Dict, Any
from src.analytics.config import BreakoutConfig
from src.analytics.validator import BreakoutValidator

class BreakoutCalculator:
    def __init__(self, config: BreakoutConfig = None):
        self.config = config or BreakoutConfig()

    def compute(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Computes breakouts for the LATEST available date in the dataframe.
        """
        if not BreakoutValidator.validate_data(df):
            return []

        # Ensure sorted by date
        df = df.sort_values('trade_date').reset_index(drop=True)
        
        # Get the target row (Latest)
        current_row = df.iloc[-1]
        
        current_close = current_row['close']
        current_vol = current_row['volume']
        current_date = current_row['trade_date']
        symbol = current_row['symbol']
        exchange = current_row['exchange']
        data_source_date = current_row.get('data_source_date', None)
        
        # Pre-calculate rolling Highs and Volume Averages
        # Only up to the previous day (shift 1)
        # We need efficient lookups. Since we are only checking the LAST row, 
        # we can just take the window max from the tail.
        
        # Actually, for correctness and speed on single DF:
        # window_max = df['high'].iloc[-N-1:-1].max()
        # This is strictly complying with "Exclude current candle".
        
        detected_breakouts = []
        
        total_rows = len(df)
        
        for name, lookback in self.config.LOOKBACKS.items():
            
            # 1. Determine Window
            if lookback == -1: # All Time
                # All history EXCEPT current
                if total_rows < 2: 
                    continue
                window_high = df['high'].iloc[:-1].max()
                # Volume lookback for all time? 
                # Usually we take a standard avg like 50 days for volume confirmation even on ATH.
                # Let's use 50 for volume reference on ATH or full if less.
                vol_window_size = min(total_rows - 1, 50)
                window_vol_avg = df['volume'].iloc[-vol_window_size-1:-1].mean()
                
            else:
                if total_rows <= lookback: 
                    # Not enough history for this specific timeframe
                    # Example: Stock listed 10 days ago, cannot have D50 breakout.
                    continue
                    
                # Slice: From (End - 1 - Lookback) to (End - 1)
                # e.g., if Lookback=1, we want index -2 (only one candle, the previous one)
                start_idx = -1 - lookback
                end_idx = -1
                
                subset_high = df['high'].iloc[start_idx:end_idx]
                subset_low = df['low'].iloc[start_idx:end_idx]
                subset_vol = df['volume'].iloc[start_idx:end_idx]
                
                window_high = subset_high.max()
                window_low = subset_low.min()
                window_vol_avg = subset_vol.mean()
                
            # 2. Check Breakout/Breakdown Condition
            if np.isnan(window_high) or np.isnan(window_low):
                continue
            
            breakout_detected = False
            breakout_level = 0.0
            pct_dist = 0.0
                
            if current_close > window_high:
                # BULLISH BREAKOUT
                breakout_detected = True
                breakout_level = window_high
                pct_dist = ((current_close - window_high) / window_high) * 100
            
            elif current_close < window_low:
                # BEARISH BREAKDOWN
                breakout_detected = True
                breakout_level = window_low
                pct_dist = ((current_close - window_low) / window_low) * 100
                
            if breakout_detected:
                # Volume Logic
                # If avg vol is 0 or nan, handle
                if window_vol_avg > 0:
                    vol_confirmed = current_vol > (window_vol_avg * self.config.VOLUME_MULT)
                else:
                    vol_confirmed = False # Can't confirm if no history volume
                
                result = {
                    "exchange": exchange,
                    "symbol": symbol,
                    "trade_date": current_date,
                    "breakout_type": name,
                    "breakout_level": round(breakout_level, 2),
                    "close_price": round(current_close, 2),
                    "breakout_pct": round(pct_dist, 2),
                    "volume": int(current_vol),
                    "avg_volume_n": int(window_vol_avg) if not np.isnan(window_vol_avg) else 0,
                    "volume_confirmation": bool(vol_confirmed),
                    "data_source_date": data_source_date
                }
                detected_breakouts.append(result)
                
        return detected_breakouts

