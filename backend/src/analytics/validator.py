import pandas as pd
from typing import Optional

class BreakoutValidator:
    @staticmethod
    def validate_data(df: pd.DataFrame, min_rows: int = 2) -> bool:
        """
        Validates if dataframe has enough data for minimal calculation.
        """
        if df is None or df.empty:
            return False
            
        required_cols = {'open', 'high', 'low', 'close', 'volume', 'trade_date'}
        if not required_cols.issubset(df.columns):
            return False
            
        if len(df) < min_rows:
            return False
            
        return True
