"""
Complex candlestick patterns for SAMBOT.
Contains multi-candle pattern detection functions.
"""

import numpy as np


def is_morning_star(c1, c2, c3, body_threshold=0.3):
    """
    Detect morning star pattern (bullish reversal)
    
    Args:
        c1: First candle data with OHLC (bearish)
        c2: Second candle data with OHLC (small body)
        c3: Third candle data with OHLC (bullish)
        body_threshold: Maximum ratio of second candle body to first candle body
        
    Returns:
        bool: True if pattern is detected
    """
    # Calculate bodies
    body1 = abs(c1['close'] - c1['open'])
    body2 = abs(c2['close'] - c2['open'])
    body3 = abs(c3['close'] - c3['open'])
    
    # Check if bodies are valid (non-zero)
    if body1 == 0 or body3 == 0:
        return False
    
    # Morning star pattern conditions:
    return (
        c1['close'] < c1['open'] and                 # First candle is bearish
        body2 < body1 * body_threshold and           # Second candle has a small body
        c3['close'] > c3['open'] and                 # Third candle is bullish
        c3['close'] > (c1['open'] + c1['close'])/2   # Third candle closes above middle of first candle
    )


def is_evening_star(c1, c2, c3, body_threshold=0.3):
    """
    Detect evening star pattern (bearish reversal)
    
    Args:
        c1: First candle data with OHLC (bullish)
        c2: Second candle data with OHLC (small body)
        c3: Third candle data with OHLC (bearish)
        body_threshold: Maximum ratio of second candle body to first candle body
        
    Returns:
        bool: True if pattern is detected
    """
    # Calculate bodies
    body1 = abs(c1['close'] - c1['open'])
    body2 = abs(c2['close'] - c2['open'])
    body3 = abs(c3['close'] - c3['open'])
    
    # Check if bodies are valid (non-zero)
    if body1 == 0 or body3 == 0:
        return False
    
    # Evening star pattern conditions:
    return (
        c1['close'] > c1['open'] and                 # First candle is bullish
        body2 < body1 * body_threshold and           # Second candle has a small body
        c3['close'] < c3['open'] and                 # Third candle is bearish
        c3['close'] < (c1['open'] + c1['close'])/2   # Third candle closes below middle of first candle
    )


def is_three_white_soldiers(c1, c2, c3, wick_threshold=0.3):
    """
    Detect three white soldiers pattern (bullish continuation)
    
    Args:
        c1: First candle data with OHLC
        c2: Second candle data with OHLC
        c3: Third candle data with OHLC
        wick_threshold: Maximum ratio of upper wick to body
        
    Returns:
        bool: True if pattern is detected
    """
    # Calculate bodies
    body1 = c1['close'] - c1['open']
    body2 = c2['close'] - c2['open']
    body3 = c3['close'] - c3['open']
    
    # Calculate upper wicks
    upper_wick1 = c1['high'] - c1['close']
    upper_wick2 = c2['high'] - c2['close']
    upper_wick3 = c3['high'] - c3['close']
    
    # Check if bodies are valid (non-zero and positive)
    if body1 <= 0 or body2 <= 0 or body3 <= 0:
        return False
    
    # Three white soldiers pattern conditions:
    return (
        c1['close'] > c1['open'] and      # All three candles are bullish
        c2['close'] > c2['open'] and
        c3['close'] > c3['open'] and
        c2['open'] > c1['open'] and        # Each opens higher than previous
        c3['open'] > c2['open'] and
        c2['close'] > c1['close'] and      # Each closes higher than previous
        c3['close'] > c2['close'] and
        upper_wick1 < body1 * wick_threshold and   # Small upper wicks
        upper_wick2 < body2 * wick_threshold and
        upper_wick3 < body3 * wick_threshold
    )


def is_three_black_crows(c1, c2, c3, wick_threshold=0.3):
    """
    Detect three black crows pattern (bearish continuation)
    
    Args:
        c1: First candle data with OHLC
        c2: Second candle data with OHLC
        c3: Third candle data with OHLC
        wick_threshold: Maximum ratio of lower wick to body
        
    Returns:
        bool: True if pattern is detected
    """
    # Calculate bodies
    body1 = c1['open'] - c1['close']
    body2 = c2['open'] - c2['close']
    body3 = c3['open'] - c3['close']
    
    # Calculate lower wicks
    lower_wick1 = c1['close'] - c1['low']
    lower_wick2 = c2['close'] - c2['low']
    lower_wick3 = c3['close'] - c3['low']
    
    # Check if bodies are valid (non-zero and positive)
    if body1 <= 0 or body2 <= 0 or body3 <= 0:
        return False
    
    # Three black crows pattern conditions:
    return (
        c1['close'] < c1['open'] and      # All three candles are bearish
        c2['close'] < c2['open'] and
        c3['close'] < c3['open'] and
        c2['open'] < c1['open'] and        # Each opens lower than previous
        c3['open'] < c2['open'] and
        c2['close'] < c1['close'] and      # Each closes lower than previous
        c3['close'] < c2['close'] and
        lower_wick1 < body1 * wick_threshold and   # Small lower wicks
        lower_wick2 < body2 * wick_threshold and
        lower_wick3 < body3 * wick_threshold
    )


def is_tweezer_top(c1, c2, threshold=0.2):
    """
    Detect tweezer top pattern (bearish reversal)
    
    Args:
        c1: First candle data with OHLC (bullish)
        c2: Second candle data with OHLC (bearish)
        threshold: Maximum ratio of high price difference to average range
        
    Returns:
        bool: True if pattern is detected
    """
    # Calculate ranges
    range1 = c1['high'] - c1['low']
    range2 = c2['high'] - c2['low']
    avg_range = (range1 + range2) / 2
    
    # Calculate high price difference
    high_diff = abs(c1['high'] - c2['high'])
    
    # Tweezer top pattern conditions:
    return (
        c1['close'] > c1['open'] and      # First candle is bullish
        c2['close'] < c2['open'] and      # Second candle is bearish
        high_diff < avg_range * threshold  # Highs are very close
    )


def is_tweezer_bottom(c1, c2, threshold=0.2):
    """
    Detect tweezer bottom pattern (bullish reversal)
    
    Args:
        c1: First candle data with OHLC (bearish)
        c2: Second candle data with OHLC (bullish)
        threshold: Maximum ratio of low price difference to average range
        
    Returns:
        bool: True if pattern is detected
    """
    # Calculate ranges
    range1 = c1['high'] - c1['low']
    range2 = c2['high'] - c2['low']
    avg_range = (range1 + range2) / 2
    
    # Calculate low price difference
    low_diff = abs(c1['low'] - c2['low'])
    
    # Tweezer bottom pattern conditions:
    return (
        c1['close'] < c1['open'] and      # First candle is bearish
        c2['close'] > c2['open'] and      # Second candle is bullish
        low_diff < avg_range * threshold   # Lows are very close
    )


def is_abandoned_baby(c1, c2, c3, gap_threshold=0.1):
    """
    Detect abandoned baby pattern (reversal)
    
    Args:
        c1: First candle data with OHLC
        c2: Second candle data with OHLC (doji)
        c3: Third candle data with OHLC
        gap_threshold: Minimum gap between candles as ratio of price
        
    Returns:
        tuple: (is_pattern, is_bullish) where is_bullish is True for bullish pattern
    """
    # Calculate bodies
    body1 = abs(c1['close'] - c1['open'])
    body2 = abs(c2['close'] - c2['open'])
    body3 = abs(c3['close'] - c3['open'])
    
    # Calculate ranges
    range1 = c1['high'] - c1['low']
    range3 = c3['high'] - c3['low']
    
    # Check if middle candle is a doji
    is_middle_doji = body2 / (c2['high'] - c2['low']) < 0.1 if (c2['high'] - c2['low']) > 0 else False
    
    # Calculate gaps
    gap1 = min(c2['low'], c2['high']) - max(c1['low'], c1['high'])
    gap2 = min(c3['low'], c3['high']) - max(c2['low'], c2['high'])
    
    # Determine if this is a bullish or bearish abandoned baby
    is_bullish = (c1['close'] < c1['open']) and (c3['close'] > c3['open'])
    is_bearish = (c1['close'] > c1['open']) and (c3['close'] < c3['open'])
    
    # Minimum price to calculate meaningful gaps
    min_price = min(c1['close'], c2['close'], c3['close'])
    
    # Abandoned baby pattern conditions:
    if is_middle_doji and (is_bullish or is_bearish):
        if is_bullish:
            # Bullish abandoned baby has gaps down and up
            has_gaps = (gap1 < -min_price * gap_threshold) and (gap2 > min_price * gap_threshold)
            return has_gaps, True
        else:
            # Bearish abandoned baby has gaps up and down
            has_gaps = (gap1 > min_price * gap_threshold) and (gap2 < -min_price * gap_threshold)
            return has_gaps, False
    
    return False, False


def is_dark_cloud_cover(c1, c2, penetration=0.5):
    """
    Detect dark cloud cover pattern (bearish reversal)
    
    Args:
        c1: First candle data with OHLC (bullish)
        c2: Second candle data with OHLC (bearish)
        penetration: Minimum penetration into the previous candle's body (0.5 = 50%)
        
    Returns:
        bool: True if pattern is detected
    """
    # Calculate first candle's body
    body1 = c1['close'] - c1['open']
    
    # Check if first candle is bullish
    if body1 <= 0:
        return False
    
    # Calculate penetration point
    penetration_point = c1['close'] - (body1 * penetration)
    
    # Dark cloud cover pattern conditions:
    return (
        c1['close'] > c1['open'] and          # First candle is bullish
        c2['close'] < c2['open'] and          # Second candle is bearish
        c2['open'] > c1['high'] and           # Second opens above first high (gap up)
        c2['close'] < penetration_point       # Second closes into first body by specified penetration
    )


def is_piercing_pattern(c1, c2, penetration=0.5):
    """
    Detect piercing pattern (bullish reversal)
    
    Args:
        c1: First candle data with OHLC (bearish)
        c2: Second candle data with OHLC (bullish)
        penetration: Minimum penetration into the previous candle's body (0.5 = 50%)
        
    Returns:
        bool: True if pattern is detected
    """
    # Calculate first candle's body
    body1 = c1['open'] - c1['close']
    
    # Check if first candle is bearish
    if body1 <= 0:
        return False
    
    # Calculate penetration point
    penetration_point = c1['close'] + (body1 * penetration)
    
    # Piercing pattern conditions:
    return (
        c1['close'] < c1['open'] and          # First candle is bearish
        c2['close'] > c2['open'] and          # Second candle is bullish
        c2['open'] < c1['low'] and            # Second opens below first low (gap down)
        c2['close'] > penetration_point       # Second closes into first body by specified penetration
    )