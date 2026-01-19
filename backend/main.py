import sys
from pathlib import Path

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

from src.universe.builder import build_universe
from src.historical.service import HistoricalDataService
from src.analytics.service import BreakoutService

def run_phase1():
    print("--- Phase 1: Market Universe Builder ---")
    if build_universe():
        print("Phase 1 Complete.")
    else:
        print("Phase 1 Failed.")
        sys.exit(1)

def run_phase2():
    print("\n--- Phase 2: Historical Data Engine ---")
    svc = HistoricalDataService()
    svc.update_all(max_workers=20)
    print("Phase 2 Complete.")

def run_phase3():
    print("\n--- Phase 3: Breakout Detection Engine ---")
    svc = BreakoutService()
    df = svc.scan_universe(max_workers=20)
    print("Phase 3 Complete.")
    if not df.empty:
         print("\nTop 5 Breakouts:")
         print(df[['symbol', 'breakout_type', 'breakout_pct', 'volume_confirmation']].head().to_string())

import argparse

def main():
    parser = argparse.ArgumentParser(description="Market Analytics System CLI")
    parser.add_argument("--mode", type=str, choices=['universe', 'history', 'scan', 'all'], default='all', help="Execution mode")
    args = parser.parse_args()
    
    print(f"Initializing Market Analytics System (Mode: {args.mode})...")
    
    if args.mode in ['universe', 'all']:
        # Force rebuild if specific mode requested? Or just run if missing?
        # If user explicitly asks for 'universe', we should rebuild even if exists.
        if args.mode == 'universe' or not (BASE_DIR / "data/processed/universe.parquet").exists():
            run_phase1()
        else:
             # In 'all' mode, skip if exists to save time, unless user forced?
             # Standard behavior: skip if exists in auto mode.
             if (BASE_DIR / "data/processed/universe.parquet").exists():
                 print("Phase 1 data found. Skipping build (use --mode universe to force rebuild).")
             else:
                 run_phase1()

    if args.mode in ['history', 'all']:
        run_phase2()
        
    if args.mode in ['scan', 'all']:
        run_phase3()

if __name__ == "__main__":
    main()

