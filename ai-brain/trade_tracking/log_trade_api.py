#!/usr/bin/env python3
"""
Log Trade API Helper

This script provides a command-line interface for logging trades.
It's designed to be called from Node.js.
"""

import sys
import json
from trade_logger import TradeLogger


def main():
    """Process trade data and log it."""
    # Check arguments
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Invalid arguments. Expected trade data JSON."}))
        sys.exit(1)
        
    try:
        # Parse trade data
        trade_data = json.loads(sys.argv[1])
        
        # Initialize logger
        logger = TradeLogger()
        
        # Log the trade
        trade_id = logger.log_trade(trade_data)
        
        # Get the full trade record
        trade = logger.get_trade(trade_id)
        
        # Return success
        print(json.dumps({
            "status": "success",
            "trade_id": trade_id,
            "trade": trade
        }))
        
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()