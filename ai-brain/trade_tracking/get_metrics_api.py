#!/usr/bin/env python3
"""
Get Metrics API Helper

This script provides a command-line interface for retrieving performance metrics.
It's designed to be called from Node.js.
"""

import sys
import json
from trade_logger import TradeLogger
from performance_tracker import PerformanceTracker


def main():
    """Process options and return performance metrics."""
    # Check arguments
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Invalid arguments. Expected options JSON."}))
        sys.exit(1)
        
    try:
        # Parse options
        options = json.loads(sys.argv[1])
        
        # Initialize logger and tracker
        logger = TradeLogger()
        tracker = PerformanceTracker(logger)
        
        # Extract filter options
        start_date = options.get('startDate')
        end_date = options.get('endDate')
        index = options.get('index')
        
        # Calculate metrics
        metrics = tracker.calculate_metrics(
            start_date=start_date,
            end_date=end_date,
            index=index
        )
        
        # Get pattern effectiveness if requested
        pattern_analysis = None
        if options.get('includePatterns', False):
            pattern_analysis = tracker.analyze_pattern_effectiveness(
                trades=logger.get_trades_by_date_range(start_date, end_date) if start_date else None
            )
            
        # Get psychological analysis if requested
        psych_analysis = None
        if options.get('includePsychology', False):
            psych_analysis = tracker.analyze_trade_psychology(
                trades=logger.get_trades_by_date_range(start_date, end_date) if start_date else None
            )
            
        # Compile result
        result = {
            "metrics": metrics,
            "filters": {
                "start_date": start_date,
                "end_date": end_date,
                "index": index
            }
        }
        
        if pattern_analysis:
            result["pattern_analysis"] = pattern_analysis
            
        if psych_analysis:
            result["psychological_analysis"] = psych_analysis
        
        # Return success
        print(json.dumps(result))
        
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()