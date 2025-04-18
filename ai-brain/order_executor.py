"""
Enhanced Order Executor Module for SAMBOT trading system.
Handles order execution through Fyers API with comprehensive error handling and logging.
"""

import os
import json
import time
import logging
from datetime import datetime, timedelta
import requests

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("order_logs.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("OrderExecutor")

# Load environment variables for API credentials
API_KEY = os.environ.get("FYERS_API_KEY", "")
API_SECRET = os.environ.get("FYERS_API_SECRET", "")
CLIENT_ID = os.environ.get("FYERS_CLIENT_ID", "")
ENABLE_REAL_TRADING = os.environ.get("ENABLE_REAL_TRADING", "false").lower() == "true"

# Constants
LOT_SIZE = {
    "NIFTY": 50,
    "BANKNIFTY": 25,
    "FINNIFTY": 40,
    "SENSEX": 10,
    "MIDCPNIFTY": 75
}

DEFAULT_LOT_SIZE = 50  # Default to NIFTY lot size


from trade_tracking.trade_logger import TradeLogger

# Initialize the logger 
trade_logger = TradeLogger()


def get_access_token():
    """
    Get or refresh Fyers API access token
    
    Returns:
        str: Access token
    """
    # Check if we have a cached token
    token_file = "fyers_token.json"
    
    try:
        if os.path.exists(token_file):
            with open(token_file, "r") as f:
                token_data = json.load(f)
                
            # Check if token is still valid (less than 1 day old)
            expiry_time = datetime.fromisoformat(token_data.get("expiry", ""))
            if expiry_time > datetime.now():
                logger.info("Using cached Fyers access token")
                return token_data.get("access_token", "")
    except Exception as e:
        logger.error(f"Error reading cached token: {str(e)}")
    
    # Token doesn't exist or is expired, get a new one
    if not API_KEY or not API_SECRET:
        logger.error("Missing Fyers API credentials in environment variables")
        return ""
    
    try:
        # In a real implementation, this would use the Fyers API flow:
        # 1. Generate auth code
        # 2. Exchange auth code for access token
        # For example:
        """
        session = requests.Session()
        response = session.post(
            "https://api.fyers.in/api/v2/token",
            json={
                "client_id": API_KEY,
                "secret_key": API_SECRET,
                "grant_type": "authorization_code",
                "code": auth_code
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            access_token = data.get("access_token", "")
            
            # Cache the token
            with open(token_file, "w") as f:
                json.dump({
                    "access_token": access_token,
                    "expiry": (datetime.now() + timedelta(days=1)).isoformat()
                }, f)
                
            return access_token
        """
        
        # For development, return a mock token
        mock_token = "mock_fyers_token_" + datetime.now().strftime("%Y%m%d")
        
        # Cache the mock token
        with open(token_file, "w") as f:
            json.dump({
                "access_token": mock_token,
                "expiry": (datetime.now() + timedelta(days=1)).isoformat()
            }, f)
        
        logger.info("Generated mock Fyers access token for development")
        return mock_token
    
    except Exception as e:
        logger.error(f"Failed to get Fyers access token: {str(e)}")
        return ""




def place_order(index, strike, direction, lots, expiry):
    # ... your existing code ...
    
    # After successfully placing the order, log it
    trade_data = {
        "index": index,
        "signal": direction,
        "entry_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "entry_price": price,  # Current price when entered
        "quantity": lots * 15,
        "strike": strike,
        "expiry": expiry,
        "status": "OPEN",
        "stop_loss": stop_loss,
        "target": target
    }
    
    # Add psychology data if you have it
    if "psychology" in context:
        trade_data["psychology"] = context["psychology"]
        
    # Add detected patterns if you have them
    if "patterns_detected" in context:
        trade_data["patterns_detected"] = context["patterns_detected"]
        
    # Log the trade
    trade_id = trade_logger.log_trade(trade_data)
    
    # Include trade_id in the response
    response = {...}  # Your existing response
    response["trade_id"] = trade_id
    
    return response

    def update_trade(trade_id, exit_price=None, status="CLOSED"):
    """
    Update a trade when it's closed or modified.
    """
    update_data = {}
    
    if exit_price is not None:
        update_data["exit_price"] = exit_price
        update_data["exit_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    update_data["status"] = status
    
    # Update the trade
    success = trade_logger.update_trade(trade_id, update_data)
    
    return success

    # When closing a position or updating status:
def update_trade_status(trade_id, exit_price, status="CLOSED"):
    # Update trade with exit information
    trade_logger.update_trade(trade_id, {
        "exit_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "exit_price": exit_price,
        "status": status
    })


def get_expiry_dates(index="NIFTY"):
    """
    Get available expiry dates for an index
    
    Args:
        index (str): Index name
        
    Returns:
        list: List of available expiry dates
    """
    # In production, fetch actual expiry dates from exchange
    # For development, return some mock expiry dates
    
    # Current date
    today = datetime.now()
    
    # Find the next Thursday (weekly expiry for NIFTY)
    days_until_thursday = (3 - today.weekday()) % 7
    next_thursday = today + timedelta(days=days_until_thursday)
    
    # Find the last Thursday of the month (monthly expiry)
    next_month = today.replace(day=28) + timedelta(days=4)
    last_day = next_month - timedelta(days=next_month.day)
    days_to_subtract = (last_day.weekday() - 3) % 7
    monthly_expiry = last_day - timedelta(days=days_to_subtract)
    
    # Format expiry dates in YYMMDD format (as used by NSE)
    weekly_expiry = next_thursday.strftime("%y%m%d")
    monthly_expiry_str = monthly_expiry.strftime("%y%m%d")
    
    return [weekly_expiry, monthly_expiry_str]


def get_symbol(index, strike, option_type, expiry=None):
    """
    Generate symbol for options contract
    
    Args:
        index (str): Index name (e.g., NIFTY, BANKNIFTY)
        strike (int): Strike price
        option_type (str): Option type (CE for Call, PE for Put)
        expiry (str): Expiry date (if None, nearest expiry is used)
        
    Returns:
        str: Symbol in exchange format
    """
    if not expiry:
        expiry = get_expiry_dates(index)[0]  # Get nearest expiry
    
    # Different exchanges have different symbol formats
    # For NSE FNO, the format is generally like: NIFTY2305111700CE
    # symbol = f"{index.upper()}{expiry}{strike}{option_type.upper()}"
    
    # For Fyers, the format is typically: NSE:NIFTY23D2115500CE
    symbol = f"NSE:{index.upper()}{expiry}{strike}{option_type.upper()}"
    
    return symbol


def place_order(index, strike, direction, lots=1, expiry=None, order_type="MARKET", price=0):
    """
    Place an options order
    
    Args:
        index (str): Index name (NIFTY, BANKNIFTY, etc.)
        strike (int): Strike price
        direction (str): Trade direction (BUY CALL, BUY PUT, etc.)
        lots (int): Number of lots
        expiry (str): Expiry date (if None, nearest expiry is used)
        order_type (str): Order type (MARKET, LIMIT)
        price (float): Limit price (used if order_type is LIMIT)
        
    Returns:
        dict: Order response
    """
    # Parse direction into side and option type
    if direction == "BUY CALL":
        side = "BUY"
        option_type = "CE"
    elif direction == "BUY PUT":
        side = "BUY"
        option_type = "PE"
    elif direction == "SELL CALL":
        side = "SELL"
        option_type = "CE"
    elif direction == "SELL PUT":
        side = "SELL"
        option_type = "PE"
    else:
        logger.error(f"Invalid direction: {direction}")
        return {"error": f"Invalid direction: {direction}"}
    
    # Get lot size for the index
    lot_size = LOT_SIZE.get(index.upper(), DEFAULT_LOT_SIZE)
    quantity = lots * lot_size
    
    # Get symbol
    symbol = get_symbol(index, strike, option_type, expiry)
    
    # Prepare order payload
    order_payload = {
        "symbol": symbol,
        "qty": quantity,
        "type": 2 if order_type == "MARKET" else 1,  # 1=Limit, 2=Market
        "side": 1 if side == "BUY" else -1,
        "productType": "INTRADAY",
        "validity": "DAY",
        "disclosedQty": 0,
        "offlineOrder": False
    }
    
    # Add limit price if order type is LIMIT
    if order_type == "LIMIT" and price > 0:
        order_payload["limitPrice"] = price
    
    # Log the order details
    logger.info(f"Placing order: {json.dumps(order_payload)}")
    
    # If real trading is disabled, return mock response
    if not ENABLE_REAL_TRADING:
        logger.info("Real trading disabled. Returning mock order response.")
        return {
            "s": "ok",
            "orderNumber": f"mockorder_{int(time.time())}",
            "message": "Order placed successfully (MOCK)"
        }
    
    # Get access token
    access_token = get_access_token()
    if not access_token:
        return {"error": "Failed to get access token"}
    
    # Place the order
    try:
        response = requests.post(
            "https://api.fyers.in/api/v2/orders",
            json=order_payload,
            headers={"Authorization": f"{API_KEY}:{access_token}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Order placed successfully: {data}")
            return data
        else:
            error_msg = f"Order placement failed: {response.text}"
            logger.error(error_msg)
            return {"error": error_msg}
    
    except Exception as e:
        error_msg = f"Exception placing order: {str(e)}"
        logger.error(error_msg)
        return {"error": error_msg}


def check_order_status(order_id):
    """
    Check the status of an order
    
    Args:
        order_id (str): Order ID to check
        
    Returns:
        dict: Order status
    """
    # If real trading is disabled, return mock response
    if not ENABLE_REAL_TRADING or order_id.startswith("mockorder_"):
        logger.info(f"Checking mock order status for {order_id}")
        return {
            "s": "ok",
            "orderNumber": order_id,
            "status": "FILLED",
            "filledQty": "1",
            "message": "Order filled (MOCK)"
        }
    
    # Get access token
    access_token = get_access_token()
    if not access_token:
        return {"error": "Failed to get access token"}
    
    # Check order status
    try:
        response = requests.get(
            f"https://api.fyers.in/api/v2/orders?id={order_id}",
            headers={"Authorization": f"{API_KEY}:{access_token}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Order status: {data}")
            return data
        else:
            error_msg = f"Order status check failed: {response.text}"
            logger.error(error_msg)
            return {"error": error_msg}
    
    except Exception as e:
        error_msg = f"Exception checking order status: {str(e)}"
        logger.error(error_msg)
        return {"error": error_msg}


def execute_strategy(signal, confidence, entry, stop_loss, target, index="NIFTY", lots=1):
    """
    Execute a complete trading strategy based on signal
    
    Args:
        signal (str): Trading signal (BUY CALL, BUY PUT, WAIT)
        confidence (float): Signal confidence
        entry (float): Entry price
        stop_loss (float): Stop loss price
        target (float): Target price
        index (str): Index name
        lots (int): Number of lots
        
    Returns:
        dict: Strategy execution result
    """
    # Don't execute trades with WAIT signal or low confidence
    if signal == "WAIT" or confidence < 0.7:
        logger.info(f"Not executing trade: {signal}, confidence: {confidence}")
        return {
            "executed": False,
            "reason": "Signal is WAIT or confidence too low",
            "signal": signal,
            "confidence": confidence
        }
    
    # Get strike price based on entry price
    if signal == "BUY CALL":
        # For calls, use slightly OTM strike for better risk/reward
        strike = int(round(entry / 100)) * 100 + 100
    else:  # BUY PUT
        # For puts, use slightly OTM strike for better risk/reward
        strike = int(round(entry / 100)) * 100 - 100
    
    # Place the order
    order_response = place_order(index, strike, signal, lots)
    
    # If order failed, return error
    if "error" in order_response:
        return {
            "executed": False,
            "reason": order_response["error"],
            "signal": signal,
            "strike": strike,
            "lots": lots
        }
    
    # Record the trade details for later reference
    trade_details = {
        "executed": True,
        "order_id": order_response.get("orderNumber", "unknown"),
        "signal": signal,
        "index": index,
        "strike": strike,
        "lots": lots,
        "entry": entry,
        "stop_loss": stop_loss,
        "target": target,
        "timestamp": datetime.now().isoformat()
    }
    
    # Save trade details to a log file
    try:
        trades_file = "executed_trades.json"
        
        # Load existing trades
        existing_trades = []
        if os.path.exists(trades_file):
            with open(trades_file, "r") as f:
                existing_trades = json.load(f)
        
        # Add new trade
        existing_trades.append(trade_details)
        
        # Save trades
        with open(trades_file, "w") as f:
            json.dump(existing_trades, f, indent=2)
    
    except Exception as e:
        logger.error(f"Error saving trade details: {str(e)}")
    
    return trade_details


# If run directly, show example usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 3:
        # Parse command line arguments
        index = sys.argv[1]
        strike = int(sys.argv[2])
        direction = sys.argv[3]
        lots = int(sys.argv[4]) if len(sys.argv) > 4 else 1
        
        # Place the order
        result = place_order(index, strike, direction, lots)
        
        # Output result
        print(json.dumps(result, indent=2))
    else:
        print("Usage: python order_executor.py <index> <strike> <direction> [lots]")
        print("Example: python order_executor.py NIFTY 17500 'BUY CALL' 1")