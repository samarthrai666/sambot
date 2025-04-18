"""
Basic candlestick patterns for SAMBOT.
Contains single and two-candle pattern detection functions.
"""

import numpy as np


def is_bullish_engulfing(c1, c2):
    """
    Detect bullish engulfing pattern
    
    Args:
        c1: Previous candle data with OHLC
        c2: Current candle data with OHLC
        
    Returns:
        bool: True if pattern is detected
    """
    return (
        c1['close'] < c1['open'] and  # Previous candle is bearish
        c2['open'] < c1['close'] and  # Current opens below previous close
        c2['close'] > c1['open'] and  # Current closes above previous open
        c2['close'] > c2['open']      # Current candle is bullish
    )


def is_bearish_engulfing(c1, c2):
    """
    Detect bearish engulfing pattern
    
    Args:
        c1: Previous candle data with OHLC
        c2: Current candle data with OHLC
        
    Returns:
        bool: True if pattern is detected
    """
    return (
        c1['close'] > c1['open'] and  # Previous candle is bullish
        c2['open'] > c1['close'] and  # Current opens above previous close
        c2['close'] < c1['open'] and  # Current closes below previous open
        c2['close'] < c2['open']      # Current candle is bearish
    )


def is_doji(candle, threshold=0.1):
    """
    Detect doji pattern
    
    Args:
        candle: Candle data with OHLC
        threshold: Maximum ratio of body to range to be considered a doji
        
    Returns:
        bool: True if pattern is detected
    """
    body = abs(candle['close'] - candle['open'])
    range_ = candle['high'] - candle['low']
    
    # Doji has a very small body compared to the range
    return range_ > 0 and body / range_ < threshold


def is_hammer(candle, shadow_multiplier=2):
    """
    Detect hammer pattern
    
    Args:
        candle: Candle data with OHLC
        shadow_multiplier: How many times bigger the lower shadow should be compared to the body
        
    Returns:
        bool: True if pattern is detected
    """
    body = abs(candle['close'] - candle['open'])
    if body == 0:
        return False
    
    # Calculate lower and upper shadows
    lower_shadow = min(candle['open'], candle['close']) - candle['low']
    upper_shadow = candle['high'] - max(candle['open'], candle['close'])
    
    # Hammer has a small body, long lower shadow, and minimal upper shadow
    return (
        lower_shadow > shadow_multiplier * body and
        upper_shadow < body and
        body > 0  # Ensure there is some body
    )


def is_shooting_star(candle, shadow_multiplier=2):
    """
    Detect shooting star pattern
    
    Args:
        candle: Candle data with OHLC
        shadow_multiplier: How many times bigger the upper shadow should be compared to the body
        
    Returns:
        bool: True if pattern is detected
    """
    body = abs(candle['close'] - candle['open'])
    if body == 0:
        return False
    
    # Calculate upper and lower shadows
    upper_shadow = candle['high'] - max(candle['open'], candle['close'])
    lower_shadow = min(candle['open'], candle['close']) - candle['low']
    
    # Shooting star has a small body, long upper shadow, and minimal lower shadow
    return (
        upper_shadow > shadow_multiplier * body and
        lower_shadow < body and
        body > 0  # Ensure there is some body
    )


def is_marubozu(candle, threshold=0.1):
    """
    Detect marubozu pattern (candle with no or very small shadows)
    
    Args:
        candle: Candle data with OHLC
        threshold: Maximum ratio of shadow to body to be considered a marubozu
        
    Returns:
        tuple: (is_marubozu, direction) where direction is 1 for bullish, -1 for bearish
    """
    body = abs(candle['close'] - candle['open'])
    if body == 0:
        return False, 0
    
    # Calculate upper and lower shadows
    upper_shadow = candle['high'] - max(candle['open'], candle['close'])
    lower_shadow = min(candle['open'], candle['close']) - candle['low']
    
    # Calculate shadow ratios
    upper_ratio = upper_shadow / body
    lower_ratio = lower_shadow / body
    
    # Marubozu has very small shadows compared to body
    is_marubozu = upper_ratio <= threshold and lower_ratio <= threshold
    
    # Determine direction
    direction = 1 if candle['close'] > candle['open'] else -1
    
    return is_marubozu, direction


def is_bullish_harami(c1, c2):
    """
    Detect bullish harami pattern
    
    Args:
        c1: Previous candle data with OHLC
        c2: Current candle data with OHLC
        
    Returns:
        bool: True if pattern is detected
    """
    return (
        c1['close'] < c1['open'] and                # Previous candle is bearish
        c2['close'] > c2['open'] and                # Current candle is bullish
        c2['open'] > c1['close'] and                # Current body is inside previous body
        c2['close'] < c1['open'] and                # Current body is inside previous body
        abs(c2['close'] - c2['open']) < abs(c1['close'] - c1['open'])  # Current body is smaller
    )


def is_bearish_harami(c1, c2):
    """
    Detect bearish harami pattern
    
    Args:
        c1: Previous candle data with OHLC
        c2: Current candle data with OHLC
        
    Returns:
        bool: True if pattern is detected
    """
    return (
        c1['close'] > c1['open'] and                # Previous candle is bullish
        c2['close'] < c2['open'] and                # Current candle is bearish
        c2['open'] < c1['close'] and                # Current body is inside previous body
        c2['close'] > c1['open'] and                # Current body is inside previous body
        abs(c2['close'] - c2['open']) < abs(c1['close'] - c1['open'])  # Current body is smaller
    )


def is_long_legged_doji(candle, threshold=0.1, leg_multiplier=3):
    """
    Detect long-legged doji pattern
    
    Args:
        candle: Candle data with OHLC
        threshold: Maximum ratio of body to range to be considered a doji
        leg_multiplier: How many times bigger the shadows should be compared to the body
        
    Returns:
        bool: True if pattern is detected
    """
    body = abs(candle['close'] - candle['open'])
    range_ = candle['high'] - candle['low']
    
    if body == 0 or range_ == 0:
        return False
    
    # Calculate upper and lower shadows
    upper_shadow = candle['high'] - max(candle['open'], candle['close'])
    lower_shadow = min(candle['open'], candle['close']) - candle['low']
    
    # Long-legged doji has a small body and long shadows on both sides
    return (
        body / range_ < threshold and
        upper_shadow > body * leg_multiplier and
        lower_shadow > body * leg_multiplier
    )


def is_dragonfly_doji(candle, threshold=0.1, shadow_multiplier=5):
    """
    Detect dragonfly doji pattern (doji with long lower shadow)
    
    Args:
        candle: Candle data with OHLC
        threshold: Maximum ratio of body to range to be considered a doji
        shadow_multiplier: How many times bigger the lower shadow should be compared to the body
        
    Returns:
        bool: True if pattern is detected
    """
    body = abs(candle['close'] - candle['open'])
    range_ = candle['high'] - candle['low']
    
    if body == 0 or range_ == 0:
        return False
    
    # Calculate upper and lower shadows
    upper_shadow = candle['high'] - max(candle['open'], candle['close'])
    lower_shadow = min(candle['open'], candle['close']) - candle['low']
    
    # Dragonfly doji has a small body, minimal upper shadow, and long lower shadow
    return (
        body / range_ < threshold and
        upper_shadow < body and
        lower_shadow > body * shadow_multiplier
    )


def is_gravestone_doji(candle, threshold=0.1, shadow_multiplier=5):
    """
    Detect gravestone doji pattern (doji with long upper shadow)
    
    Args:
        candle: Candle data with OHLC
        threshold: Maximum ratio of body to range to be considered a doji
        shadow_multiplier: How many times bigger the upper shadow should be compared to the body
        
    Returns:
        bool: True if pattern is detected
    """
    body = abs(candle['close'] - candle['open'])
    range_ = candle['high'] - candle['low']
    
    if body == 0 or range_ == 0:
        return False
    
    # Calculate upper and lower shadows
    upper_shadow = candle['high'] - max(candle['open'], candle['close'])
    lower_shadow = min(candle['open'], candle['close']) - candle['low']
    
    # Gravestone doji has a small body, minimal lower shadow, and long upper shadow
    return (
        body / range_ < threshold and
        lower_shadow < body and
        upper_shadow > body * shadow_multiplier
    )