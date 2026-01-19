from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import pandas as pd
from datetime import datetime

from src.market_state.resolver import MarketStateResolver
from src.historical.store import HistoricalDataCache
from config.settings import PROCESSED_DIR

router = APIRouter()

@router.get("/system/status")
def get_system_status():
    """Get current market state and system time."""
    resolver = MarketStateResolver()
    context = resolver.resolve()
    return {
        "system_time": context.run_timestamp.isoformat(),
        "market_state": context.state.value,
        "trade_date": context.effective_trade_date.isoformat(),
        "is_market_open": context.is_market_open
    }

@router.get("/breakouts")
def get_breakouts(
    exchange: Optional[List[str]] = Query(None),
    timeframe: Optional[List[str]] = Query(None),
    confirmed_only: bool = True
):
    """Get breakout scan results with optional filtering."""
    path = PROCESSED_DIR / "breakout_scan.parquet"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Breakout scan data not found. Please run the backend scan.")
    
    df = pd.read_parquet(path)
    
    if df.empty:
        return []
        
    # Load Dismissed List
    dismissed_path = PROCESSED_DIR / "dismissed.json"
    dismissed_symbols = []
    if dismissed_path.exists():
        try:
            import json
            with open(dismissed_path, "r") as f:
                dismissed_symbols = json.load(f)
        except Exception:
            pass
            
    # Filter specific exchange/symbol combinations
    # Currently dismissed_symbols can be list of "EXCHANGE:SYMBOL" strings
    if dismissed_symbols:
        df['unique_id'] = df['exchange'] + ":" + df['symbol']
        df = df[~df['unique_id'].isin(dismissed_symbols)]
        
    # Apply filters
    if exchange:
        df = df[df['exchange'].isin(exchange)]
        
    if timeframe:
        df = df[df['breakout_type'].isin(timeframe)]
        
    if confirmed_only:
        df = df[df['volume_confirmation'] == True]
        
    # Convert to list of dicts for JSON response
    # Handle NaN values for JSON compliance
    return df.fillna("").to_dict(orient="records")

from pydantic import BaseModel

class DismissRequest(BaseModel):
    symbol: str
    exchange: str

@router.post("/dismiss")
def dismiss_breakout(request: DismissRequest):
    """Dismiss a breakout signal (add to ignored list)."""
    dismissed_path = PROCESSED_DIR / "dismissed.json"
    
    unique_id = f"{request.exchange}:{request.symbol}"
    
    current_list = []
    if dismissed_path.exists():
        try:
            import json
            with open(dismissed_path, "r") as f:
                current_list = json.load(f)
        except Exception:
            pass
            
    if unique_id not in current_list:
        current_list.append(unique_id)
        import json
        with open(dismissed_path, "w") as f:
            json.dump(current_list, f)
            
    return {"status": "success", "message": f"Dismissed {unique_id}"}

@router.post("/restore")
def restore_breakout(request: DismissRequest):
    """Restore a dismissed breakout signal."""
    dismissed_path = PROCESSED_DIR / "dismissed.json"
    
    unique_id = f"{request.exchange}:{request.symbol}"
    
    current_list = []
    if dismissed_path.exists():
        try:
            import json
            with open(dismissed_path, "r") as f:
                current_list = json.load(f)
        except Exception:
            pass
            
    if unique_id in current_list:
        current_list.remove(unique_id)
        import json
        with open(dismissed_path, "w") as f:
            json.dump(current_list, f)
            
    return {"status": "success", "message": f"Restored {unique_id}"}

@router.get("/dismissed")
def get_dismissed_list():
    """Get list of dismissed signals."""
    dismissed_path = PROCESSED_DIR / "dismissed.json"
    if dismissed_path.exists():
        try:
            import json
            with open(dismissed_path, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []



@router.get("/history/{symbol}")
def get_history(symbol: str, exchange: str = "NSE"):
    """Get historical candle data for a symbol."""
    cache = HistoricalDataCache()
    df = cache.load(symbol, exchange)
    
    if df.empty:
        raise HTTPException(status_code=404, detail=f"No data found for {symbol}")
        
    # Ensure dates are strings
    df['trade_date'] = df['trade_date'].astype(str)
    
    return df.to_dict(orient="records")
