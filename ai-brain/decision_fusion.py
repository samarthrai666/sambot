def should_take_trade(signal, confidence, rsi, macd, atr, risk_reward, strategy_mode):
    if signal == "WAIT":
        return False

    if confidence < 0.7:
        return False

    if strategy_mode == "scalping" and atr < 10:
        return False  # No volatility

    if strategy_mode == "swing" and risk_reward < 2:
        return False  # Bad RRR

    if rsi < 35 and signal == "BUY PUT":
        return True
    if rsi > 65 and signal == "BUY CALL":
        return True

    return False


def determine_lot_size(balance, risk_per_trade, entry, stop_loss):
    risk_amount = balance * risk_per_trade
    risk_per_lot = abs(entry - stop_loss) * 15  # 15 is lot size for NIFTY
    lots = int(risk_amount / risk_per_lot)
    return max(lots, 1)


def choose_expiry_strategy(strategy_mode):
    if strategy_mode == "scalping":
        return "nearest_weekly"
    if strategy_mode == "swing":
        return "monthly"
    return "weekly"
