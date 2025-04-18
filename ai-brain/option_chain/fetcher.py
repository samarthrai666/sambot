"""
NSE Option Chain Data Fetcher

This module handles fetching option chain data from NSE's website,
handling sessions, cookies, and retries appropriately.
"""

import requests
import time
import json
import pandas as pd
from datetime import datetime


class OptionChainFetcher:
    """Fetches option chain data from NSE."""
    
    def __init__(self, index="NIFTY"):
        """
        Initialize the fetcher.
        
        Args:
            index (str): Index name (NIFTY, BANKNIFTY, etc.)
        """
        self.index = index
        self.session = self._create_session()
        self.last_fetch_time = None
        self.data = None
        self.expiry_dates = []
        self.selected_expiry = None
        self.underlying_value = None
        
    def _create_session(self):
        """Create a session with appropriate headers for NSE website."""
        session = requests.Session()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://www.nseindia.com/option-chain"
        }
        session.headers.update(headers)
        
        # Visit the homepage first to get cookies
        try:
            session.get("https://www.nseindia.com", timeout=15)
        except requests.exceptions.RequestException as e:
            print(f"Error initializing session: {e}")
        
        return session
    
    def fetch_option_chain(self, expiry=None, max_retries=3):
        """
        Fetch the option chain data from NSE.
        
        Args:
            expiry (str, optional): Specific expiry date to fetch
            max_retries (int): Maximum number of retry attempts
            
        Returns:
            bool: True if fetch was successful, False otherwise
        """
        retry_count = 0
        while retry_count < max_retries:
            try:
                base_url = "https://www.nseindia.com/api/option-chain-indices"
                params = {"symbol": self.index}
                if expiry:
                    params["expiryDate"] = expiry
                    
                # Add a small delay to avoid rate limiting
                time.sleep(1)
                    
                response = self.session.get(base_url, params=params, timeout=15)
                
                if response.status_code != 200:
                    print(f"Error fetching data: Status {response.status_code}")
                    retry_count += 1
                    time.sleep(2)  # Wait before retrying
                    continue
                    
                data = response.json()
                self.data = data
                self.last_fetch_time = datetime.now()
                self.underlying_value = data.get('records', {}).get('underlyingValue', None)
                
                # Extract all available expiry dates
                filtered_data = data.get('filtered', {}).get('data', [])
                if filtered_data:
                    self.expiry_dates = sorted(list(set([item.get('expiryDate') for item in filtered_data if 'expiryDate' in item])))
                    if not expiry and self.expiry_dates:
                        self.selected_expiry = self.expiry_dates[0]  # Select the nearest expiry by default
                    else:
                        self.selected_expiry = expiry
                        
                return True
                    
            except requests.exceptions.RequestException as e:
                print(f"Error fetching option chain (attempt {retry_count+1}/{max_retries}): {e}")
                retry_count += 1
                time.sleep(2)  # Wait before retrying
                
            except json.JSONDecodeError:
                print(f"Error decoding JSON response (attempt {retry_count+1}/{max_retries})")
                retry_count += 1
                time.sleep(2)  # Wait before retrying
                
        # If we've exhausted all retries
        print(f"Failed to fetch option chain after {max_retries} attempts")
        return False
    
    def prepare_dataframe(self):
        """
        Convert the option chain data to a pandas DataFrame for analysis.
        
        Returns:
            pandas.DataFrame: Processed option chain data or None if no data
        """
        if not self.data:
            print("No data available. Please fetch the option chain first.")
            return None
            
        try:
            records = self.data.get('filtered', {}).get('data', [])
            if not records:
                records = self.data.get('records', {}).get('data', [])
                
            # Extract data from records
            option_data = []
            for item in records:
                strike = item.get('strikePrice')
                if not strike:
                    continue
                    
                ce = item.get('CE', {})
                pe = item.get('PE', {})
                
                option_data.append({
                    'strike': strike,
                    'expiry': item.get('expiryDate', ''),
                    'ce_oi': ce.get('openInterest', 0),
                    'ce_volume': ce.get('totalTradedVolume', 0),
                    'ce_iv': ce.get('impliedVolatility', 0),
                    'ce_ltp': ce.get('lastPrice', 0),
                    'ce_net_change': ce.get('change', 0),
                    'ce_change_oi': ce.get('changeinOpenInterest', 0),
                    'ce_bid_qty': ce.get('bidQty', 0),
                    'ce_bid_price': ce.get('bidprice', 0),
                    'ce_ask_price': ce.get('askPrice', 0),
                    'ce_ask_qty': ce.get('askQty', 0),
                    'ce_underlying': ce.get('underlyingValue', self.underlying_value),
                    'pe_oi': pe.get('openInterest', 0),
                    'pe_volume': pe.get('totalTradedVolume', 0),
                    'pe_iv': pe.get('impliedVolatility', 0),
                    'pe_ltp': pe.get('lastPrice', 0),
                    'pe_net_change': pe.get('change', 0),
                    'pe_change_oi': pe.get('changeinOpenInterest', 0),
                    'pe_bid_qty': pe.get('bidQty', 0),
                    'pe_bid_price': pe.get('bidprice', 0),
                    'pe_ask_price': pe.get('askPrice', 0),
                    'pe_ask_qty': pe.get('askQty', 0),
                    'pe_underlying': pe.get('underlyingValue', self.underlying_value),
                })
                
            # Create DataFrame
            df = pd.DataFrame(option_data)
            
            # Filter by selected expiry if available
            if self.selected_expiry and 'expiry' in df.columns:
                df = df[df['expiry'] == self.selected_expiry]
                
            # Sort by strike price and reset index
            if not df.empty:
                df = df.sort_values('strike').reset_index(drop=True)
                
            return df
                
        except Exception as e:
            print(f"Error preparing DataFrame: {e}")
            return None
    
    def get_available_indices(self):
        """
        Returns a list of indices available for option chain analysis.
        
        Returns:
            list: List of available indices
        """
        return ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]
    
    def get_nearest_expiry(self):
        """
        Returns the nearest expiry date available.
        
        Returns:
            str: Nearest expiry date or None if not available
        """
        if not self.expiry_dates:
            return None
        return self.expiry_dates[0] if self.expiry_dates else None
    
    def get_data_freshness(self):
        """
        Returns information about the freshness of the data.
        
        Returns:
            dict: Information about data age and timestamps
        """
        if not self.last_fetch_time:
            return {"status": "No data fetched yet"}
        
        now = datetime.now()
        age_seconds = (now - self.last_fetch_time).total_seconds()
        
        return {
            "last_fetch": self.last_fetch_time.strftime("%Y-%m-%d %H:%M:%S"),
            "age_seconds": age_seconds,
            "is_fresh": age_seconds < 300,  # Consider data fresh if less than 5 minutes old
            "underlying_value": self.underlying_value
        }