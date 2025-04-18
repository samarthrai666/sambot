"""
Enhanced Log and Learn Module for SAMBOT trading system.
Logs trade details, analyzes performance, and provides insights for strategy improvement.
"""

import json
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from io import BytesIO
import base64


def log_trade(index, signal, entry, exit_price, stop_loss, target, strike, pnl=0, confidence=0, execution_time=None):
    """
    Log trade details to a file for later analysis
    
    Args:
        index (str): Index name (NIFTY, BANKNIFTY, etc.)
        signal (str): Trade signal (BUY CALL, BUY PUT)
        entry (float): Entry price
        exit_price (float): Exit price (0 if not yet exited)
        stop_loss (float): Stop loss price
        target (float): Target price
        strike (int): Option strike price
        pnl (float): Profit/loss amount
        confidence (float): Signal confidence
        execution_time (str): Trade execution time (ISO format)
        
    Returns:
        dict: Logged trade details
    """
    # Create trade log object
    log = {
        "timestamp": execution_time or datetime.now().isoformat(),
        "index": index,
        "signal": signal,
        "entry": float(entry),
        "exit": float(exit_price) if exit_price else 0,
        "stop_loss": float(stop_loss),
        "target": float(target),
        "strike": int(strike),
        "pnl": float(pnl),
        "confidence": float(confidence),
        "completed": exit_price is not None and exit_price > 0
    }
    
    # File to store trade logs
    log_file = "trade_logs.json"
    
    try:
        # Read existing logs if file exists
        if os.path.exists(log_file):
            with open(log_file, "r") as f:
                existing_logs = json.load(f)
        else:
            existing_logs = []
        
        # Add new log
        existing_logs.append(log)
        
        # Write back to file
        with open(log_file, "w") as f:
            json.dump(existing_logs, f, indent=2)
        
        print(f"✅ Trade logged: {log['signal']} at {log['entry']}")
        
        return log
    
    except Exception as e:
        print(f"❌ Error logging trade: {str(e)}")
        return {"error": str(e)}


def update_trade_exit(trade_id, exit_price, pnl, exit_time=None):
    """
    Update a trade with exit information
    
    Args:
        trade_id (int): Index of the trade in the log file
        exit_price (float): Exit price
        pnl (float): Profit/loss amount
        exit_time (str): Exit time (ISO format)
        
    Returns:
        bool: Success status
    """
    log_file = "trade_logs.json"
    
    try:
        # Read existing logs
        if not os.path.exists(log_file):
            return False
        
        with open(log_file, "r") as f:
            logs = json.load(f)
        
        # Validate trade ID
        if trade_id < 0 or trade_id >= len(logs):
            print(f"❌ Invalid trade ID: {trade_id}")
            return False
        
        # Update trade
        logs[trade_id]["exit"] = float(exit_price)
        logs[trade_id]["pnl"] = float(pnl)
        logs[trade_id]["completed"] = True
        
        if exit_time:
            logs[trade_id]["exit_time"] = exit_time
        else:
            logs[trade_id]["exit_time"] = datetime.now().isoformat()
        
        # Write back to file
        with open(log_file, "w") as f:
            json.dump(logs, f, indent=2)
        
        print(f"✅ Trade {trade_id} updated with exit price {exit_price} and PNL {pnl}")
        
        return True
    
    except Exception as e:
        print(f"❌ Error updating trade: {str(e)}")
        return False


def get_trade_logs(days=None, index=None):
    """
    Get trade logs filtered by criteria
    
    Args:
        days (int): Number of days to look back
        index (str): Filter by index name
        
    Returns:
        list: Filtered trade logs
    """
    log_file = "trade_logs.json"
    
    if not os.path.exists(log_file):
        return []
    
    try:
        with open(log_file, "r") as f:
            logs = json.load(f)
        
        # Filter by days
        if days:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            logs = [log for log in logs if log["timestamp"] >= cutoff_date]
        
        # Filter by index
        if index:
            logs = [log for log in logs if log["index"].upper() == index.upper()]
        
        return logs
    
    except Exception as e:
        print(f"❌ Error retrieving trade logs: {str(e)}")
        return []


def summarize_performance(days=30, index=None):
    """
    Summarize trading performance
    
    Args:
        days (int): Number of days to look back
        index (str): Filter by index name
        
    Returns:
        dict: Performance metrics
    """
    # Get filtered logs
    logs = get_trade_logs(days, index)
    
    if not logs:
        return {
            "total_trades": 0,
            "wins": 0,
            "losses": 0,
            "win_rate": 0,
            "total_pnl": 0,
            "avg_pnl": 0,
            "max_win": 0,
            "max_loss": 0,
            "profit_factor": 0
        }
    
    # Count total trades
    total_trades = len(logs)
    completed_trades = [log for log in logs if log.get("completed", False)]
    
    # Calculate basic metrics
    wins = sum(1 for log in completed_trades if log["pnl"] > 0)
    losses = sum(1 for log in completed_trades if log["pnl"] <= 0)
    
    # Win rate and total PNL
    win_rate = wins / len(completed_trades) * 100 if completed_trades else 0
    total_pnl = sum(log["pnl"] for log in completed_trades)
    avg_pnl = total_pnl / len(completed_trades) if completed_trades else 0
    
    # Max win and loss
    max_win = max([log["pnl"] for log in completed_trades if log["pnl"] > 0], default=0)
    max_loss = min([log["pnl"] for log in completed_trades if log["pnl"] <= 0], default=0)
    
    # Profit factor (gross profit / gross loss)
    gross_profit = sum(log["pnl"] for log in completed_trades if log["pnl"] > 0)
    gross_loss = abs(sum(log["pnl"] for log in completed_trades if log["pnl"] < 0))
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
    
    # Signal performance
    call_trades = [log for log in completed_trades if log["signal"] == "BUY CALL"]
    put_trades = [log for log in completed_trades if log["signal"] == "BUY PUT"]
    
    call_win_rate = sum(1 for log in call_trades if log["pnl"] > 0) / len(call_trades) * 100 if call_trades else 0
    put_win_rate = sum(1 for log in put_trades if log["pnl"] > 0) / len(put_trades) * 100 if put_trades else 0
    
    # Time of day analysis
    try:
        for log in logs:
            if "timestamp" in log:
                dt = datetime.fromisoformat(log["timestamp"])
                log["hour"] = dt.hour
    except:
        # If parsing fails, just continue without time analysis
        pass
    
    # Create summary
    summary = {
        "total_trades": total_trades,
        "completed_trades": len(completed_trades),
        "pending_trades": total_trades - len(completed_trades),
        "wins": wins,
        "losses": losses,
        "win_rate": round(win_rate, 2),
        "total_pnl": round(total_pnl, 2),
        "avg_pnl": round(avg_pnl, 2),
        "max_win": round(max_win, 2),
        "max_loss": round(max_loss, 2),
        "profit_factor": round(profit_factor, 2),
        "call_trades": len(call_trades),
        "put_trades": len(put_trades),
        "call_win_rate": round(call_win_rate, 2),
        "put_win_rate": round(put_win_rate, 2)
    }
    
    return summary


def generate_performance_chart(days=30, index=None):
    """
    Generate performance chart image
    
    Args:
        days (int): Number of days to look back
        index (str): Filter by index name
        
    Returns:
        str: Base64 encoded PNG image
    """
    logs = get_trade_logs(days, index)
    
    if not logs:
        return None
    
    # Convert logs to DataFrame for easier analysis
    df = pd.DataFrame(logs)
    
    # Convert timestamp to datetime
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")
    
    # Calculate cumulative PNL
    df["cumulative_pnl"] = df["pnl"].cumsum()
    
    # Create figure with subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), gridspec_kw={"height_ratios": [3, 1]})
    
    # Plot cumulative PNL
    ax1.plot(df["timestamp"], df["cumulative_pnl"], marker="o", linestyle="-", color="blue")
    ax1.set_title("Cumulative PNL Over Time")
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Cumulative PNL")
    ax1.grid(True, alpha=0.3)
    
    # Add horizontal line at y=0
    ax1.axhline(y=0, color="red", linestyle="--", alpha=0.3)
    
    # Color individual trades (green for profit, red for loss)
    for i, row in df.iterrows():
        color = "green" if row["pnl"] > 0 else "red"
        ax1.scatter(row["timestamp"], row["cumulative_pnl"], color=color, s=30)
    
    # Plot trade distribution
    df["day_of_week"] = df["timestamp"].dt.day_name()
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_counts = df["day_of_week"].value_counts().reindex(day_order).fillna(0)
    
    ax2.bar(day_counts.index, day_counts.values, color="skyblue")
    ax2.set_title("Trade Distribution by Day of Week")
    ax2.set_xlabel("Day of Week")
    ax2.set_ylabel("Number of Trades")
    
    # Add summary stats as text
    summary = summarize_performance(days, index)
    
    stats_text = (
        f"Total Trades: {summary['total_trades']} | "
        f"Win Rate: {summary['win_rate']}% | "
        f"Total PNL: {summary['total_pnl']} | "
        f"Profit Factor: {summary['profit_factor']}"
    )
    
    fig.text(0.5, 0.01, stats_text, ha="center", fontsize=10, bbox={"facecolor": "white", "alpha": 0.5, "pad": 5})
    
    plt.tight_layout()
    
    # Convert plot to PNG image
    buffer = BytesIO()
    plt.savefig(buffer, format="png", dpi=100)
    buffer.seek(0)
    
    # Encode as base64
    image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    plt.close()
    
    return image_base64


def analyze_trading_patterns():
    """
    Analyze patterns in trading performance
    
    Returns:
        dict: Insights about trading patterns
    """
    logs = get_trade_logs()
    
    if not logs:
        return {"error": "No trade logs found"}
    
    # Convert logs to DataFrame
    df = pd.DataFrame(logs)
    
    # Ensure timestamp is datetime
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    
    # Extract time components
    df["hour"] = df["timestamp"].dt.hour
    df["day_of_week"] = df["timestamp"].dt.day_name()
    
    # Analyze win rate by hour
    hour_groups = df.groupby("hour")
    hour_win_rates = {}
    
    for hour, group in hour_groups:
        wins = sum(1 for p in group["pnl"] if p > 0)
        total = len(group)
        win_rate = wins / total if total > 0 else 0
        hour_win_rates[hour] = {
            "win_rate": round(win_rate * 100, 2),
            "trades": total
        }
    
    # Analyze win rate by day of week
    day_groups = df.groupby("day_of_week")
    day_win_rates = {}
    
    for day, group in day_groups:
        wins = sum(1 for p in group["pnl"] if p > 0)
        total = len(group)
        win_rate = wins / total if total > 0 else 0
        day_win_rates[day] = {
            "win_rate": round(win_rate * 100, 2),
            "trades": total
        }
    
    # Analyze confidence correlation with success
    conf_corr = df[["confidence", "pnl"]].corr().iloc[0, 1]
    
    # Find best and worst hours
    best_hour = max(hour_win_rates.items(), key=lambda x: x[1]["win_rate"])
    worst_hour = min(hour_win_rates.items(), key=lambda x: x[1]["win_rate"] if x[1]["trades"] >= 3 else 100)
    
    # Find best and worst days
    best_day = max(day_win_rates.items(), key=lambda x: x[1]["win_rate"])
    worst_day = min(day_win_rates.items(), key=lambda x: x[1]["win_rate"] if x[1]["trades"] >= 3 else 100)
    
    # Find best signal type
    call_trades = df[df["signal"] == "BUY CALL"]
    put_trades = df[df["signal"] == "BUY PUT"]
    
    call_win_rate = sum(1 for p in call_trades["pnl"] if p > 0) / len(call_trades) if len(call_trades) > 0 else 0
    put_win_rate = sum(1 for p in put_trades["pnl"] if p > 0) / len(put_trades) if len(put_trades) > 0 else 0
    
    best_signal = "BUY CALL" if call_win_rate > put_win_rate else "BUY PUT"
    best_signal_rate = round(max(call_win_rate, put_win_rate) * 100, 2)
    
    # Format insights
    insights = {
        "best_trading_hour": {
            "hour": best_hour[0],
            "win_rate": best_hour[1]["win_rate"],
            "trades": best_hour[1]["trades"]
        },
        "worst_trading_hour": {
            "hour": worst_hour[0],
            "win_rate": worst_hour[1]["win_rate"],
            "trades": worst_hour[1]["trades"]
        },
        "best_trading_day": {
            "day": best_day[0],
            "win_rate": best_day[1]["win_rate"],
            "trades": best_day[1]["trades"]
        },
        "worst_trading_day": {
            "day": worst_day[0],
            "win_rate": worst_day[1]["win_rate"],
            "trades": worst_day[1]["trades"]
        },
        "best_signal": {
            "type": best_signal,
            "win_rate": best_signal_rate
        },
        "confidence_correlation": round(conf_corr, 2),
        "hour_win_rates": hour_win_rates,
        "day_win_rates": day_win_rates
    }
    
    return insights


def get_trading_recommendations():
    """
    Get trading recommendations based on historical performance
    
    Returns:
        dict: Trading recommendations
    """
    insights = analyze_trading_patterns()
    
    if "error" in insights:
        return {"error": insights["error"]}
    
    recommendations = []
    
    # Recommendation based on best trading hours
    best_hour = insights["best_trading_hour"]
    if best_hour["trades"] >= 5 and best_hour["win_rate"] > 60:
        recommendations.append(f"Focus trading around {best_hour['hour']}:00 hours with {best_hour['win_rate']}% win rate")
    
    # Recommendation based on worst trading hours
    worst_hour = insights["worst_trading_hour"]
    if worst_hour["trades"] >= 5 and worst_hour["win_rate"] < 40:
        recommendations.append(f"Avoid trading around {worst_hour['hour']}:00 hours with only {worst_hour['win_rate']}% win rate")
    
    # Recommendation based on day of week
    best_day = insights["best_trading_day"]
    if best_day["trades"] >= 3 and best_day["win_rate"] > 60:
        recommendations.append(f"Prioritize trading on {best_day['day']} with {best_day['win_rate']}% win rate")
    
    # Recommendation based on signal type
    best_signal = insights["best_signal"]
    if best_signal["win_rate"] > 60:
        recommendations.append(f"Preference for {best_signal['type']} signals with {best_signal['win_rate']}% win rate")
    
    # Recommendation based on confidence correlation
    conf_corr = insights["confidence_correlation"]
    if conf_corr > 0.3:
        recommendations.append(f"Strong correlation ({conf_corr}) between confidence score and profitability. Focus on high confidence signals")
    elif conf_corr < -0.1:
        recommendations.append(f"Negative correlation ({conf_corr}) between confidence and profitability. Review confidence calculation")
    
    # If no specific recommendations, add general ones
    if not recommendations:
        recommendations = [
            "Insufficient data for specific recommendations",
            "Continue collecting trade data for better analysis",
            "Consider backtesting strategy with longer historical data"
        ]
    
    return {
        "recommendations": recommendations,
        "insights": insights
    }


# If run directly, show summary stats
if __name__ == "__main__":
    import sys
    
    # Check if command line arguments are provided
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "summary":
            # Get days parameter if provided
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            
            # Get summary
            summary = summarize_performance(days)
            print(json.dumps(summary, indent=2))
        
        elif command == "add":
            # Example: python log_and_learn.py add NIFTY "BUY CALL" 22500 22550 22450 22600 22550 500 0.85
            if len(sys.argv) < 10:
                print("Usage: python log_and_learn.py add <index> <signal> <entry> <exit> <stop_loss> <target> <strike> <pnl> <confidence>")
            else:
                index = sys.argv[2]
                signal = sys.argv[3]
                entry = float(sys.argv[4])
                exit_price = float(sys.argv[5])
                stop_loss = float(sys.argv[6])
                target = float(sys.argv[7])
                strike = int(sys.argv[8])
                pnl = float(sys.argv[9])
                confidence = float(sys.argv[10]) if len(sys.argv) > 10 else 0.7
                
                log_trade(index, signal, entry, exit_price, stop_loss, target, strike, pnl, confidence)
        
        elif command == "recommendations":
            # Get trading recommendations
            recommendations = get_trading_recommendations()
            print(json.dumps(recommendations, indent=2))
        
        else:
            print("Unknown command. Usage:")
            print("  python log_and_learn.py summary [days]")
            print("  python log_and_learn.py add <index> <signal> <entry> <exit> <stop_loss> <target> <strike> <pnl> <confidence>")
            print("  python log_and_learn.py recommendations")
    
    else:
        # Default: show 30-day summary
        summary = summarize_performance(30)
        print(json.dumps(summary, indent=2))