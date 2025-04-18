def is_bullish_engulfing(c1, c2):
    return (
        c1['close'] < c1['open'] and
        c2['open'] < c1['close'] and
        c2['close'] > c1['open'] and
        c2['close'] > c2['open']
    )

def is_bearish_engulfing(c1, c2):
    return (
        c1['close'] > c1['open'] and
        c2['open'] > c1['close'] and
        c2['close'] < c1['open'] and
        c2['close'] < c2['open']
    )

def is_doji(candle):
    body = abs(candle['close'] - candle['open'])
    range_ = candle['high'] - candle['low']
    return range_ > 0 and body / range_ < 0.1

def is_hammer(candle):
    body = abs(candle['close'] - candle['open'])
    lower_wick = candle['open'] - candle['low'] if candle['close'] > candle['open'] else candle['close'] - candle['low']
    upper_wick = candle['high'] - max(candle['open'], candle['close'])
    return lower_wick > 2 * body and upper_wick < body

def is_shooting_star(candle):
    body = abs(candle['close'] - candle['open'])
    upper_wick = candle['high'] - max(candle['open'], candle['close'])
    lower_wick = min(candle['open'], candle['close']) - candle['low']
    return upper_wick > 2 * body and lower_wick < body
