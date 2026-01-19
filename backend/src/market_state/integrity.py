import pandas as pd
from src.market_state.resolver import MarketContext

class DataIntegrityService:
    @staticmethod
    def validate_breakouts(df: pd.DataFrame, context: MarketContext) -> pd.DataFrame:
        """
        Enforces data integrity on the breakout dataframe.
        1. Tags market state and run timestamp.
        2. Ensures 'data_source_date' matches 'effective_trade_date' (Warning if not).
        """
        if df.empty:
            return df
            
        # Add Context Tags
        df['market_state'] = context.state.value
        df['run_timestamp'] = context.run_timestamp
        df['effective_trade_date'] = context.effective_trade_date
        
        # Validation Logic
        # If we are in 'OPEN' state, breakout date should be Today.
        # If we are 'CLOSED', breakout date should be Last Session.
        
        # We won't drop rows blindly but we will flag them.
        # Check consistency
        # Vectorized check: df['trade_date'] == context.effective_trade_date
        # Note: dates in DF are objects or dates, ensure type match
        
        # Convert to strict date for comparison
        df['trade_date'] = pd.to_datetime(df['trade_date']).dt.date
        
        # Consistency Flag
        df['is_date_consistent'] = df['trade_date'] == context.effective_trade_date
        
        return df
