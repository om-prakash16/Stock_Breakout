from src.historical.fetcher import HistoricalDataFetcher
import pandas as pd

def test_bse():
    fetcher = HistoricalDataFetcher()
    symbol = "500325" # Reliance
    print(f"Fetching {symbol} BSE...")
    df = fetcher.fetch_history(symbol, "BSE", period="1mo")
    
    if df is not None and not df.empty:
        print("Success!")
        print(df.tail())
    else:
        print("Failed to fetch data.")

if __name__ == "__main__":
    test_bse()
