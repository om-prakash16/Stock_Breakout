import pandas as pd
from datetime import date
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from config.settings import PROCESSED_DIR
from src.historical.fetcher import HistoricalDataFetcher
from src.historical.store import HistoricalDataCache
from src.historical.calendar import MarketCalendarService

class HistoricalDataService:
    def __init__(self):
        self.fetcher = HistoricalDataFetcher()
        self.cache = HistoricalDataCache()
        self.calendar = MarketCalendarService()
        self.market_status = self.calendar.get_market_status()
        self.universe_path = PROCESSED_DIR / "universe.parquet"

    def load_universe(self) -> pd.DataFrame:
        if not self.universe_path.exists():
            raise FileNotFoundError("Universe file not found. Run Phase 1 first.")
        return pd.read_parquet(self.universe_path)

    def _process_stock(self, row) -> dict:
        symbol = row['symbol']
        exchange = row['exchange']
        
        try:
            # 1. Load Existing
            existing_df = self.cache.load(symbol, exchange)
            
            start_date = None
            mode = "full"
            
            if not existing_df.empty:
                last_date = existing_df['trade_date'].max()
                # Check if up to date
                # We need data up to last valid trading day
                target_date = self.market_status['last_valid_day']
                
                if last_date >= target_date:
                    return {"symbol": symbol, "status": "skipped", "msg": "Up to date"}
                
                start_date = last_date + pd.Timedelta(days=1)
                mode = "incremental"
            
            # 2. Fetch Data
            if mode == "full":
                new_df = self.fetcher.fetch_history(symbol, exchange, period="5y")
            else:
                # If incremental, end_date defaults to today in fetcher if None
                new_df = self.fetcher.fetch_history(symbol, exchange, start_date=start_date)
            
            if new_df is None or new_df.empty:
                return {"symbol": symbol, "status": "failed", "msg": "No data returned"}
            
            # 3. Merge
            if mode == "incremental" and not existing_df.empty:
                # Filter out overlap if any
                combined_df = pd.concat([existing_df, new_df])
                combined_df = combined_df.drop_duplicates(subset=['trade_date'], keep='last')
            else:
                combined_df = new_df
            
            # 4. Enhance/Validate
            combined_df = combined_df.sort_values('trade_date')
            
            # Add metadata columns
            combined_df['data_source_date'] = self.market_status['today']
            
            # Vectorized 'is_last_trading_day'
            # The last row IS the last available trading data. 
            # Does it match the market's specific last trading day?
            # If market is OPEN (mid-day), last row might be TODAY.
            # If market is CLOSED (evening), last row should be TODAY.
            # If Holiday, last row is PREV BUS DAY.
            # Simple logic: check if date == last_valid_day
            last_valid_day = self.market_status['last_valid_day']
            combined_df['is_last_trading_day'] = combined_df['trade_date'] == last_valid_day
            
            # 5. Save
            self.cache.save(combined_df, symbol, exchange)
            
            return {"symbol": symbol, "status": "success", "msg": f"Updated ({mode})"}
            
        except Exception as e:
            return {"symbol": symbol, "status": "error", "msg": str(e)}

    def update_all(self, max_workers=10):
        print("Loading universe...")
        universe = self.load_universe()
        print(f"Market Status: {self.market_status}")
        
        tasks = []
        rows = [row for _, row in universe.iterrows()]
        
        # Testing Limit? User said 3000+, but for verify we might want to see progress.
        # We will process ALL.
        
        print(f"Updating {len(rows)} stocks with {max_workers} workers...")
        
        results = {
            "success": 0,
            "failed": 0,
            "skipped": 0,
            "error": 0
        }
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_stock = {executor.submit(self._process_stock, row): row['symbol'] for row in rows}
            
            for future in tqdm(as_completed(future_to_stock), total=len(rows)):
                res = future.result()
                status = res['status']
                results[status] = results.get(status, 0) + 1
                
        print("\nPhase 2 Update Complete.")
        print(f"Summary: {results}")

if __name__ == "__main__":
    svc = HistoricalDataService()
    svc.update_all()
