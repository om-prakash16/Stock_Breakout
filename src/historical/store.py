import pandas as pd
from pathlib import Path
from config.settings import DATA_DIR
import os

class HistoricalDataCache:
    def __init__(self):
        self.base_path = DATA_DIR / "historical"
        
    def _get_path(self, exchange: str, symbol: str) -> Path:
        # Avoid special chars in filename
        clean_symbol = "".join(c for c in symbol if c.isalnum() or c in ('-','_'))
        return self.base_path / exchange / f"{clean_symbol}.parquet"

    def save(self, df: pd.DataFrame, symbol: str, exchange: str):
        path = self._get_path(exchange, symbol)
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            df.to_parquet(path, index=False)
        except Exception as e:
            print(f"Error caching {symbol}: {e}")

    def load(self, symbol: str, exchange: str) -> pd.DataFrame:
        path = self._get_path(exchange, symbol)
        if path.exists():
            return pd.read_parquet(path)
        return pd.DataFrame()

    def exists(self, symbol: str, exchange: str) -> bool:
        return self._get_path(exchange, symbol).exists()
