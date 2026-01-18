import pandas as pd
import os
from datetime import date

PARQUET_FILE = r"e:\brijesh_Stocks\MarketAnalyticsSystem\data\processed\breakout_scan.parquet"

def seed_bse():
    if not os.path.exists(PARQUET_FILE):
        print("Parquet file not found.")
        return

    df = pd.read_parquet(PARQUET_FILE)
    
    # Create dummy rows
    dummies = [
        {
            'exchange': 'NSE',
            'symbol': 'BREAKDOWN_TEST', 
            'trade_date': date.today(),
            'breakout_type': 'D10',
            'breakout_level': 1000.0,
            'close_price': 950.0,
            'breakout_pct': -5.0, # Negative breakout (Breakdown)
            'volume': 100000,
            'avg_volume_n': 50000,
            'volume_confirmation': True,
            'data_source_date': date.today()
        },
        {
            'exchange': 'BSE',
            'symbol': '500325', # Reliance
            'trade_date': date.today(),
            'breakout_type': 'W52',
            'breakout_level': 2500.0,
            'close_price': 2550.0,
            'breakout_pct': 2.0,
            'volume': 100000,
            'avg_volume_n': 50000,
            'volume_confirmation': True,
            'data_source_date': date.today()
        }
    ]
    
    new_data = pd.DataFrame(dummies)
    
    # Clean existing tests
    df = df[df['symbol'] != 'BREAKDOWN_TEST']
    
    if df.empty:
        final_df = new_data
    else:
        final_df = pd.concat([df, new_data], ignore_index=True)
        
    # Deduplicate
    final_df = final_df.drop_duplicates(subset=['exchange', 'symbol', 'breakout_type'])
        
    final_df.to_parquet(PARQUET_FILE)
    print("Seeded breakdown data successfully.")

if __name__ == "__main__":
    seed_bse()
