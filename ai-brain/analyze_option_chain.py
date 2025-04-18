import requests
import json

def fetch_nse_option_chain(index="NIFTY"):
    try:
        url = f"https://www.nseindia.com/api/option-chain-indices?symbol={index}"
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
            "Referer": "https://www.nseindia.com/"
        }

        session = requests.Session()
        session.headers.update(headers)
        session.get("https://www.nseindia.com")
        res = session.get(url)

        data = res.json()
        records = data['records']['data']
        underlying_value = data['records']['underlyingValue']

        option_data = []

        for item in records:
            strike = item.get("strikePrice")

            ce = item.get("CE", {})
            pe = item.get("PE", {})

            option_data.append({
                "strike": strike,
                "ce_oi": ce.get("openInterest", 0),
                "ce_change_oi": ce.get("changeinOpenInterest", 0),
                "pe_oi": pe.get("openInterest", 0),
                "pe_change_oi": pe.get("changeinOpenInterest", 0),
            })

        return {
            "underlying": underlying_value,
            "option_chain": option_data
        }

    except Exception as e:
        print(f"Option Chain Fetch Error: {str(e)}")
        return { "error": str(e) }
