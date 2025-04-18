import json
from datetime import datetime

def log_trade(index, signal, entry, exit_price, stop_loss, target, strike, pnl, confidence):
    log = {
        "timestamp": datetime.now().isoformat(),
        "index": index,
        "signal": signal,
        "entry": entry,
        "exit": exit_price,
        "stop_loss": stop_loss,
        "target": target,
        "strike": strike,
        "pnl": pnl,
        "confidence": confidence
    }

    with open("trade_logs.json", "a") as f:
        f.write(json.dumps(log) + "\n")

    return log


def summarize_performance():
    logs = []
    with open("trade_logs.json", "r") as f:
        for line in f:
            logs.append(json.loads(line))

    total_trades = len(logs)
    wins = sum(1 for l in logs if l["pnl"] > 0)
    losses = total_trades - wins
    net_pnl = sum(l["pnl"] for l in logs)

    return {
        "total_trades": total_trades,
        "wins": wins,
        "losses": losses,
        "win_rate": round((wins / total_trades) * 100, 2) if total_trades > 0 else 0,
        "net_pnl": net_pnl
    }
