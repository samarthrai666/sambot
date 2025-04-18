#!/usr/bin/env python3
"""
Update Trade API Helper

This script provides a command-line interface for updating trades.
It's designed to be called from Node.js.
"""

import sys
import json
from trade_logger import TradeLogger


def main():
    """Process trade update data and apply it."""
    # Check arguments
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Invalid arguments. Expected update data JSON."}))
        sys.exit(1)
        
    try:
        # Parse update data
        update_data = json.loads(sys.argv[1])
        
        # Extract trade ID
        if 'trade_id' not in update_data:
            print(json.dumps({"error": "Missing trade_id in update data"}))
            sys.exit(1)
            
        trade_id = update_data.pop('trade_id')
        
        # Initialize logger
        logger = TradeLogger()
        
        # Update the trade
        success = logger.update_trade(trade_id, update_data)
        
        if not success:
            print(json.dumps({"error": f"Failed to update trade {trade_id}"}))
            sys.exit(1)
            
        # Get the updated trade
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