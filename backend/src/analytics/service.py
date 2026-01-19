import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from pathlib import Path
from config.settings import DATA_DIR, PROCESSED_DIR
from src.analytics.config import BreakoutConfig
from src.analytics.calculator import BreakoutCalculator
from src.historical.store import HistoricalDataCache

class BreakoutService:
    MAX_WORKERS = 20 # Safe default for most PCs

    def __init__(self):
        self.config = BreakoutConfig()
        self.calculator = BreakoutCalculator(self.config)
        self.cache = HistoricalDataCache()
        self.universe_path = PROCESSED_DIR / "universe.parquet"
        
    def _scan_stock(self, row) -> list:
        symbol = row['symbol']
        exchange = row['exchange']
        
        try:
            # Load Data
            df = self.cache.load(symbol, exchange)
            if df.empty:
                return []
                
            # Calculate
            results = self.calculator.compute(df)
            return results
            
        except Exception as e:
            # Silent fail or log? For mass scan, usually silent or lightweight log
            return []

    def scan_universe(self, max_workers=60) -> pd.DataFrame:
        if not self.universe_path.exists():
            print("Universe not found. Attempting to build universe...")
            from src.universe.builder import build_universe
            if not build_universe():
                print("Failed to build universe. Aborting scan.")
                return pd.DataFrame()
            print("Universe built successfully.")
            
        universe = pd.read_parquet(self.universe_path)
        print(f"Scanning {len(universe)} stocks for breakouts...")
        
        all_breakouts = []
        rows = [row for _, row in universe.iterrows()]
        
        # Parallel Execution
        # Validating Input: Are we doing I/O? Yes (loading parquet files).
        # Threading is suitable.
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_stock = {executor.submit(self._scan_stock, row): row['symbol'] for row in rows}
            
            for future in tqdm(as_completed(future_to_stock), total=len(rows)):
                results = future.result()
                if results:
                    # Inject detection time
                    import datetime
                    now_str = datetime.datetime.now().isoformat()
                    for r in results:
                        r['detected_at'] = now_str
                    all_breakouts.extend(results)
                    
        # Consolidate
        if not all_breakouts:
            print("No breakouts detected.")
            # Don't return early; proceed to save empty dataframe so API doesn't 404
            
        breakout_df = pd.DataFrame(all_breakouts)
        
        # Sort
        if not breakout_df.empty:
            # Custom sort by Breakout Type Priority then Pct
            # Map type to priority
            breakout_df['priority'] = breakout_df['breakout_type'].map(self.config.PRIORITY)
            
            breakout_df = breakout_df.sort_values(
                by=['priority', 'breakout_pct'], 
                ascending=[True, False]
            ).drop(columns=['priority'])
        else:
             # Ensure schema is present for empty parquet if needed, or just save empty
             pass
        
        # Save
        # Atomic Save
        output_path = PROCESSED_DIR / "breakout_scan.parquet"
        temp_path = output_path.with_suffix(".tmp")
        
        breakout_df.to_parquet(temp_path, index=False)
        
        # Windows requires unlink before rename if target exists
        if output_path.exists():
            output_path.unlink()
            
        temp_path.rename(output_path)
        
        print(f"Breakout Scan saved to {output_path}")
        print(f"Total Breakouts: {len(breakout_df)}")

        
        return breakout_df

if __name__ == "__main__":
    svc = BreakoutService()
    df = svc.scan_universe()
    if not df.empty:
        print(df.head())
