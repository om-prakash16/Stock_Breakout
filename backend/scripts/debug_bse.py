
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(str(Path.cwd()))

from src.universe.builder import fetch_bse_equity_list

print("Attempting to fetch BSE list...")
df = fetch_bse_equity_list()
if df is not None:
    print(f"Success! Fetched {len(df)} BSE stocks.")
    print(df.head())
    print(df.columns)
else:
    print("Failed to fetch BSE list.")
