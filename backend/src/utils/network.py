import requests
import time
from typing import Optional, Dict, Any
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from config.settings import DEFAULT_TIMEOUT, REQUEST_HEADERS

def get_session():
    """Creates a requests session with retry logic."""
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session

def fetch_url(url: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None, is_json: bool = False) -> Any:
    """
    Robust URL fetcher.
    
    Args:
        url: Target URL
        headers: Optional headers (merged with default)
        params: Optional query parameters
        is_json: If True, returns parsed JSON, else text content.
        
    Returns:
        Response content (text or dict) or None if failed.
    """
    session = get_session()
    final_headers = REQUEST_HEADERS.copy()
    if headers:
        final_headers.update(headers)
        
    try:
        # NSE/BSE often have legacy SSL issues or block standard python requests
        # We disable verification for stability in this context, though not ideal for prod security.
        response = session.get(
            url, 
            headers=final_headers, 
            params=params, 
            timeout=DEFAULT_TIMEOUT,
            verify=False 
        )
        response.raise_for_status()
        
        if is_json:
            return response.json()
        return response.content
        
    except requests.exceptions.RequestException as e:
        msg = f"Error fetching {url}: {e}\n"
        if hasattr(e, 'response') and e.response is not None:
             msg += f"Status Code: {e.response.status_code}\n"
             msg += f"Response: {e.response.text[:200]}\n"
        print(msg)
        with open("network_errors.log", "a") as f:
            f.write(msg + "\n")
        return None
    except Exception as e:
        msg = f"Unexpected error fetching {url}: {e}\n"
        print(msg)
        with open("network_errors.log", "a") as f:
            f.write(msg + "\n")
        return None
