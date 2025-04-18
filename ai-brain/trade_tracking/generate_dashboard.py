#!/usr/bin/env python3
"""
Dashboard Generation Script

This script generates performance dashboards and analytics for the Sambot frontend.
"""

import os
import json
import sys
import argparse
from datetime import datetime
from trade_logger import TradeLogger
from performance_tracker import PerformanceTracker


def main():
    """
    Generate performance dashboards and metrics.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Generate performance dashboard')
    parser.add_argument('--index', help='Filter by index (e.g., NIFTY, BANKNIFTY)')
    parser.add_argument('--start', help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end', help='End date (YYYY-MM-DD)')
    parser.add_argument('--output-dir', default='sambot-frontend/public/images',
                      help='Output directory for dashboard images')
    args = parser.parse_args()
    
    # Ensure output directory exists
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Initialize logger and tracker
    logger = TradeLogger()
    tracker = PerformanceTracker(logger)
    
    # Generate timestamp for filenames
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    
    # Base filename
    base_filename = f"{args.index}_" if args.index else ""
    base_filename += timestamp
    
    # Generate dashboard image
    dashboard_path = os.path.join(args.output_dir, f"dashboard_{base_filename}.png")
    tracker.plot_metrics_dashboard(save_path=dashboard_path)
    
    # Calculate metrics with any filters
    metrics = tracker.calculate_metrics(
        start_date=args.start,
        end_date=args.end,
        index=args.index
    )
    
    # Analyze pattern effectiveness with the same filters
    pattern_analysis = tracker.analyze_pattern_effectiveness(
        trades=logger.get_trades_by_date_range(args.start, args.end) if args.start else None
    )
    
    # Analyze psychological factors with the same filters
    psych_analysis = tracker.analyze_trade_psychology(
        trades=logger.get_trades_by_date_range(args.start, args.end) if args.start else None
    )
    
    # Get recent performance for quick view
    recent_performance = None
    if not args.start and not args.end:
        # Calculate last 7 days performance if no date range specified
        from datetime import datetime, timedelta
        last_week = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        today = datetime.now().strftime("%Y-%m-%d")
        recent_performance = tracker.calculate_metrics(
            start_date=last_week,
            end_date=today,
            index=args.index
        )
    
    # Combine all data
    dashboard_data = {
        "metrics": metrics,
        "pattern_analysis": pattern_analysis,
        "psychological_analysis": psych_analysis,
        "recent_performance": recent_performance,
        "dashboard_image": f"/images/dashboard_{base_filename}.png",
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "filters": {
            "index": args.index,
            "start_date": args.start,
            "end_date": args.end
        }
    }
    
    # Save full results to JSON file
    json_path = os.path.join(args.output_dir, f"performance_{base_filename}.json")
    with open(json_path, 'w') as f:
        json.dump(dashboard_data, f, indent=2)
    
    # Output JSON for the Node.js process to capture
    print(json.dumps({
        "status": "success",
        "dashboard_image": f"/images/dashboard_{base_filename}.png",
        "performance_data": f"/images/performance_{base_filename}.json",
        "summary": {
            "total_trades": metrics.get("basic_metrics", {}).get("total_trades", 0),
            "win_rate": metrics.get("basic_metrics", {}).get("win_rate", 0),
            "total_pnl": metrics.get("basic_metrics", {}).get("total_pnl", 0),
            "max_drawdown": metrics.get("advanced_metrics", {}).get("max_drawdown", 0)
        }
    }))


if __name__ == "__main__":
    main()