"""
Enhanced Option Chain Analysis Module

This module integrates with the new option_chain package to provide
comprehensive option chain analysis for Sambot.
"""

import os
import json
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='option_chain.log'
)
logger = logging.getLogger('option_chain')

# Try to import the new option chain package
try:
    from option_chain.main import OptionChainManager
    NEW_SYSTEM_AVAILABLE = True
    logger.info("Enhanced option chain analysis system available")
except ImportError:
    # Fall back to the original implementation if the new system is not available
    NEW_SYSTEM_AVAILABLE = False
    logger.warning("Enhanced option chain system not available, falling back to basic implementation")
    import requests
    import json


def fetch_nse_option_chain(index="NIFTY", use_enhanced=True):
    """
    Fetch and analyze option chain data from NSE.
    
    Args:
        index (str): Index to analyze (NIFTY, BANKNIFTY, etc.)
        use_enhanced (bool): Whether to use the enhanced system if available
        
    Returns:
        dict: Option chain analysis results
    """
    # Use the enhanced system if available and requested
    if NEW_SYSTEM_AVAILABLE and use_enhanced:
        return _fetch_with_enhanced_system(index)
    else:
        # Fall back to the basic implementation
        return _fetch_with_basic_system(index)


def _fetch_with_enhanced_system(index):
    """
    Fetch and analyze option chain using the enhanced system.
    
    Args:
        index (str): Index to analyze
        
    Returns:
        dict: Analysis results
    """
    try:
        # Create output directory for reports and charts
        output_dir = os.path.join("option_reports", datetime.now().strftime("%Y%m%d"))
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize the option chain manager
        manager = OptionChainManager(index=index, output_dir=output_dir)
        
        # Fetch the option chain data
        if not manager.fetch_data():
            logger.error(f"Failed to fetch option chain data for {index}")
            return {"error": f"Failed to fetch option chain data for {index}"}
        
        # Get the underlying value
        underlying_value = manager.fetcher.underlying_value
        
        # Analyze the option chain
        analysis = manager.analyze()
        
        # Get trading signals
        signals = manager.get_trading_signals()
        
        # Get position suggestions
        suggestion = manager.get_trade_suggestions()
        
        # Generate visual dashboard
        try:
            dashboard_path = os.path.join(output_dir, f"{index}_dashboard.png")
            manager.visualizer.create_dashboard(save_path=dashboard_path)
        except Exception as e:
            logger.warning(f"Could not generate dashboard: {str(e)}")
            dashboard_path = None
        
        # Format the result
        if suggestion and suggestion.get('action') in ['EXECUTE', 'MONITOR']:
            result = {
                "underlying": underlying_value,
                "option_chain": [],  # We'll replace the raw option chain with analysis
                "pcr": analysis.get('pcr', 0),
                "max_pain": analysis.get('max_pain', 0),
                "signal": suggestion.get('signal', 'WAIT'),
                "confidence": suggestion.get('confidence', 0),
                "entry": suggestion.get('entry', 0),
                "strike": suggestion.get('strike', 0),
                "stop_loss": suggestion.get('stop_loss', 0),
                "target": suggestion.get('target', 0),
                "premium": suggestion.get('premium', 0),
                "lots": suggestion.get('lots', 1),
                "expiry": suggestion.get('expiry', ''),
                "risk_reward": suggestion.get('risk_reward', 0),
                "dashboard_path": dashboard_path,
                "key_levels": analysis.get('key_levels', {}),
                "momentum": analysis.get('momentum', {}),
                "iv_skew": analysis.get('iv_skew', {})
            }
        else:
            result = {
                "underlying": underlying_value,
                "option_chain": [],
                "pcr": analysis.get('pcr', 0),
                "max_pain": analysis.get('max_pain', 0),
                "signal": "WAIT",
                "confidence": 0,
                "reason": "No actionable signals detected"
            }
        
        # Save a complete report for reference
        report_path = os.path.join(output_dir, f"{index}_complete_report.json")
        with open(report_path, 'w') as f:
            json.dump({
                "analysis": analysis,
                "signals": signals,
                "suggestion": suggestion,
                "result": result
            }, f, indent=2)
        
        logger.info(f"Successfully analyzed option chain for {index}")
        return result
        
    except Exception as e:
        logger.error(f"Error in enhanced option chain analysis: {str(e)}")
        return {"error": str(e)}


def _fetch_with_basic_system(index):
    """
    Original implementation for fetching option chain data.
    
    Args:
        index (str): Index to analyze
        
    Returns:
        dict: Basic option chain data
    """
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

        if res.status_code != 200:
            logger.error(f"Failed to fetch option chain: Status {res.status_code}")
            return {"error": f"Failed with status {res.status_code}"}

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

        # Calculate PCR (Put-Call Ratio)
        total_ce_oi = sum(item["ce_oi"] for item in option_data)
        total_pe_oi = sum(item["pe_oi"] for item in option_data)
        pcr = round(total_pe_oi / total_ce_oi, 2) if total_ce_oi > 0 else 0

        # Find strike with max pain (minimum pain for option writers)
        max_pain = _calculate_max_pain(option_data, underlying_value)

        return {
            "underlying": underlying_value,
            "option_chain": option_data,
            "pcr": pcr,
            "max_pain": max_pain
        }

    except Exception as e:
        logger.error(f"Option Chain Fetch Error: {str(e)}")
        return {"error": str(e)}


def _calculate_max_pain(option_data, underlying_value):
    """
    Calculate the max pain point for option writers.
    
    Args:
        option_data (list): Option chain data
        underlying_value (float): Current price of the underlying
        
    Returns:
        float: Max pain strike price
    """
    strikes = [item["strike"] for item in option_data]
    pain_values = []
    
    for strike in strikes:
        pain = 0
        for item in option_data:
            # Calculate pain for call options
            if item["strike"] < strike:
                pain += item["ce_oi"] * max(0, item["strike"] - strike)
            # Calculate pain for put options
            if item["strike"] > strike:
                pain += item["pe_oi"] * max(0, strike - item["strike"])
        
        pain_values.append({"strike": strike, "pain": abs(pain)})
    
    # Find the strike with minimum pain
    min_pain = min(pain_values, key=lambda x: x["pain"])
    return min_pain["strike"]


if __name__ == "__main__":
    # Test the module
    result = fetch_nse_option_chain("NIFTY")
    
    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        print(f"Underlying: {result['underlying']}")
        print(f"PCR: {result['pcr']}")
        print(f"Max Pain: {result['max_pain']}")
        
        if 'signal' in result:
            print(f"Signal: {result['signal']}")
            print(f"Confidence: {result['confidence']}")
            
        if 'dashboard_path' in result:
            print(f"Dashboard saved to: {result['dashboard_path']}")