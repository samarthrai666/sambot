import requests
import pandas as pd
from datetime import datetime
import json

def fetch_nse_ohlcv(index="NIFTY"):
    try:
        url = f"https://www.nseindia.com/api/option-chain-indices?symbol={index}"
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
            "Referer": "https://www.nseindia.com/"
        }

        session = requests.Session()
        session.headers.update(headers)
        session.get("https://www.nseindia.com")  # initialize session
        response = session.get(url)
        data = response.json()

        # Extract underlying value
        underlying = data["records"]["underlyingValue"]

        # Create dummy 5-min candle from underlying value
        now = datetime.now().replace(second=0, microsecond=0)
        candle = {
            "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
            "open": underlying - 10,
            "high": underlying + 20,
            "low": underlying - 30,
            "close": underlying,
            "volume": 100000 + int(underlying % 1000)
        }

        return pd.DataFrame([candle])
    
    except Exception as e:
        print("NSE Fetch Error:", str(e))
        return pd.DataFrame()  # empty fallback
