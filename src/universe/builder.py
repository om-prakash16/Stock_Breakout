import pandas as pd
import io
from typing import Optional
from config.settings import NSE_EQUITY_URL, BSE_EQ_API_URL, PROCESSED_DIR
from src.utils.network import fetch_url

def fetch_nse_equity_list() -> Optional[pd.DataFrame]:
    """Fetches and normalizes NSE equity list."""
    print("Fetching NSE Equity List...")
    content = fetch_url(NSE_EQUITY_URL)
    
    if not content:
        print("Failed to fetch NSE data (content empty).")
        return None
        
    try:
        print(f"NSE Content Length: {len(content)}")
        # NSE CSV usually needs minimal cleaning
        df = pd.read_csv(io.BytesIO(content))
        print(f"NSE Raw Rows: {len(df)}")
        print(f"NSE Columns: {df.columns.tolist()}")
        
        # Normalize columns
        # Expected: SYMBOL, NAME OF COMPANY, SERIES, DATE OF LISTING, PAID UP VALUE, MARKET LOT, ISIN, FACE VALUE
        if 'SERIES' in df.columns:
             df = df[df['SERIES'] == 'EQ'].copy() # Filter for Equity only
        
        rename_map = {
            'SYMBOL': 'symbol',
            'NAME OF COMPANY': 'company_name',
            'ISIN': 'isin',
            'DATE OF LISTING': 'listing_date'
        }
        df = df.rename(columns=rename_map)
        df['exchange'] = 'NSE'
        df['status'] = 'Active' # Assumed active if in this list
        
        # Select required columns
        required_cols = ['symbol', 'company_name', 'isin', 'exchange', 'status']
        for col in required_cols:
            if col not in df.columns:
                print(f"Missing NSE column: {col}")
                df[col] = ''
                
        return df[required_cols]
        
    except Exception as e:
        print(f"Error parsing NSE data: {e}")
        return None

def fetch_bse_equity_list() -> Optional[pd.DataFrame]:
    """Fetches and normalizes BSE equity list from API."""
    print("Fetching BSE Equity List...")
    # The API returns a direct JSON list of dicts if headers are correct.
    # Expected format: [{"Scrip Code": "500325", "Scrip Name": "RELIANCE", ...}, ...]
    
    content = fetch_url(BSE_EQ_API_URL, is_json=False)
    
    if not content:
        print("Failed to fetch BSE data.")
        return None
        
    try:
        # Decode content
        text_content = content.decode('utf-8', errors='ignore')
        
        import json
        data = json.loads(text_content)
        
        # Check if data is list or wrapped
        if isinstance(data, dict):
            # Sometimes wrapped in a key
            if "Table" in data:
                data = data["Table"]
            else:
                # Try finding any list value
                for k, v in data.items():
                    if isinstance(v, list):
                        data = v
                        break
        
        if not isinstance(data, list):
            print(f"BSE Data is not a list: {type(data)}")
            return None
            
        print(f"BSE Raw Rows Fetched: {len(data)}")
        
        df = pd.DataFrame(data)
        
        # Determine column names based on potential API variations
        # Usually: 'ScripCode', 'ScripName', 'ScripId', 'Status', 'Group' etc.
        # Check actual columns
        cols = df.columns.tolist()
        print(f"BSE Columns Found: {cols}")
        
        rename_map = {}
        # Map Symbol
        if 'ScripCode' in cols:
            rename_map['ScripCode'] = 'symbol'
        elif 'Scrip Code' in cols:
            rename_map['Scrip Code'] = 'symbol'
        elif 'SCRIP_CD' in cols:
            rename_map['SCRIP_CD'] = 'symbol'
            
        # Map Company Name
        if 'ScripName' in cols:
            rename_map['ScripName'] = 'company_name'
        elif 'Scrip Name' in cols:
            rename_map['Scrip Name'] = 'company_name'
        elif 'Scrip_Name' in cols:
             rename_map['Scrip_Name'] = 'company_name'
        elif 'SCRIP_NAME' in cols:
            rename_map['SCRIP_NAME'] = 'company_name'
            
        if not rename_map:
            print("Could not map BSE columns.")
            return None
            
        df = df.rename(columns=rename_map)
        df['exchange'] = 'BSE'
        df['status'] = 'Active' # Assumed from URL parameter
        df['isin'] = '' # Not always available
        
        # Ensure 'symbol' is string
        if 'symbol' in df.columns:
            df['symbol'] = df['symbol'].astype(str)
            
        required_cols = ['symbol', 'company_name', 'isin', 'exchange', 'status']
        for col in required_cols:
            if col not in df.columns:
                df[col] = ''
                
        # Filter valid rows
        df = df[df['symbol'].str.len() >= 4] # Basic validation
        
        return df[required_cols]
        
    except Exception as e:
        print(f"Error parsing BSE data: {e}")
        return None


def build_universe() -> bool:
    """Orchestrates the universe building process."""
    nse_df = fetch_nse_equity_list()
    bse_df = fetch_bse_equity_list()
    
    dfs = []
    if nse_df is not None:
        dfs.append(nse_df)
    if bse_df is not None:
        dfs.append(bse_df)
        
    if not dfs:
        print("No universe data fetched.")
        return False
        
    universe_df = pd.concat(dfs, ignore_index=True)
    
    # Clean up names
    universe_df['company_name'] = universe_df['company_name'].str.title().str.strip()
    universe_df['symbol'] = universe_df['symbol'].str.upper().str.strip()
    
    # Save
    output_path = PROCESSED_DIR / "universe.parquet"
    try:
        universe_df.to_parquet(output_path, index=False)
        print(f"Universe saved to {output_path}")
        print(f"Total Stocks: {len(universe_df)}")
        print(universe_df.groupby('exchange').size())
        return True
    except Exception as e:
        print(f"Error saving universe: {e}")
        return False

if __name__ == "__main__":
    build_universe()
