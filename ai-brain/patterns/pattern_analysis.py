"""
Pattern analysis module for SAMBOT trading system.
Provides functions to detect and analyze candlestick patterns.
"""

import pandas as pd
import numpy as np

# Import pattern detection functions
try:
    from .basic_patterns import (
        is_bullish_engulfing,
        is_bearish_engulfing,
        is_doji,
        is_hammer,
        is_shooting_star,
        is_marubozu,
        is_bullish_harami,
        is_bearish_harami,
        is_long_legged_doji,
        is_dragonfly_doji,
        is_gravestone_doji
    )
    
    from .complex_patterns import (
        is_morning_star,
        is_evening_star,
        is_three_white_soldiers,
        is_three_black_crows,
        is_tweezer_top,
        is_tweezer_bottom,
        is_abandoned_baby,
        is_dark_cloud_cover,
        is_piercing_pattern
    )
    
except ImportError:
    # Fallback implementations when module structure isn't available
    print("Warning: Could not import full pattern modules. Using simplified detection.")
    
    # Basic patterns from detect_patterns.py
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
        lower_wick = min(candle['open'], candle['close']) - candle['low']
        upper_wick = candle['high'] - max(candle['open'], candle['close'])
        return lower_wick > 2 * body and upper_wick < body

    def is_shooting_star(candle):
        body = abs(candle['close'] - candle['open'])
        upper_wick = candle['high'] - max(candle['open'], candle['close'])
        lower_wick = min(candle['open'], candle['close']) - candle['low']
        return upper_wick > 2 * body and lower_wick < body
    
    def is_marubozu(candle):
        body = abs(candle['close'] - candle['open'])
        upper_shadow = candle['high'] - max(candle['open'], candle['close'])
        lower_shadow = min(candle['open'], candle['close']) - candle['low']
        is_maru = upper_shadow < 0.1 * body and lower_shadow < 0.1 * body
        direction = 1 if candle['close'] > candle['open'] else -1
        return is_maru, direction
    
    def is_bullish_harami(c1, c2):
        return (
            c1['close'] < c1['open'] and
            c2['close'] > c2['open'] and
            c2['open'] > c1['close'] and
            c2['close'] < c1['open']
        )
    
    def is_bearish_harami(c1, c2):
        return (
            c1['close'] > c1['open'] and
            c2['close'] < c2['open'] and
            c2['open'] < c1['close'] and
            c2['close'] > c1['open']
        )
    
    # Simplified versions of complex patterns
    def is_morning_star(c1, c2, c3):
        return (
            c1['close'] < c1['open'] and
            abs(c2['close'] - c2['open']) < abs(c1['close'] - c1['open']) * 0.3 and
            c3['close'] > c3['open'] and
            c3['close'] > (c1['open'] + c1['close']) / 2
        )
    
    def is_evening_star(c1, c2, c3):
        return (
            c1['close'] > c1['open'] and
            abs(c2['close'] - c2['open']) < abs(c1['close'] - c1['open']) * 0.3 and
            c3['close'] < c3['open'] and
            c3['close'] < (c1['open'] + c1['close']) / 2
        )
    
    def is_three_white_soldiers(c1, c2, c3):
        return (
            c1['close'] > c1['open'] and
            c2['close'] > c2['open'] and
            c3['close'] > c3['open'] and
            c2['open'] > c1['open'] and
            c3['open'] > c2['open'] and
            c2['close'] > c1['close'] and
            c3['close'] > c2['close']
        )
    
    def is_three_black_crows(c1, c2, c3):
        return (
            c1['close'] < c1['open'] and
            c2['close'] < c2['open'] and
            c3['close'] < c3['open'] and
            c2['open'] < c1['open'] and
            c3['open'] < c2['open'] and
            c2['close'] < c1['close'] and
            c3['close'] < c2['close']
        )
    
    def is_tweezer_top(c1, c2):
        return (
            c1['close'] > c1['open'] and
            c2['close'] < c2['open'] and
            abs(c1['high'] - c2['high']) < 0.2 * (c1['high'] - c1['low'])
        )
    
    def is_tweezer_bottom(c1, c2):
        return (
            c1['close'] < c1['open'] and
            c2['close'] > c2['open'] and
            abs(c1['low'] - c2['low']) < 0.2 * (c1['high'] - c1['low'])
        )
    
    # Simplified placeholders for other complex patterns
    def is_abandoned_baby(c1, c2, c3):
        return False, False
    
    def is_dark_cloud_cover(c1, c2):
        return False
    
    def is_piercing_pattern(c1, c2):
        return False


def detect_candlestick_patterns(df):
    """
    Detect all candlestick patterns in a DataFrame
    
    Args:
        df: DataFrame with OHLC data
        
    Returns:
        DataFrame with pattern columns added
    """
    # Create a copy to avoid modifying the original dataframe
    df = df.copy()
    
    # Initialize pattern columns
    pattern_columns = [
        'bullish_engulfing', 'bearish_engulfing',
        'doji', 'hammer', 'shooting_star',
        'morning_star', 'evening_star',
        'bullish_harami', 'bearish_harami',
        'marubozu', 'marubozu_direction',
        'three_white_soldiers', 'three_black_crows',
        'tweezer_top', 'tweezer_bottom'
    ]
    
    for col in pattern_columns:
        df[col] = 0
    
    # We need at least 3 candles for some patterns
    if len(df) < 3:
        return df
    
    # Process each candle
    for i in range(len(df)):
        # Single candle patterns
        if i >= 0:
            df.loc[i, 'doji'] = int(is_doji(df.iloc[i]))
            df.loc[i, 'hammer'] = int(is_hammer(df.iloc[i]))
            df.loc[i, 'shooting_star'] = int(is_shooting_star(df.iloc[i]))
            
            is_maru, direction = is_marubozu(df.iloc[i])
            df.loc[i, 'marubozu'] = int(is_maru)
            df.loc[i, 'marubozu_direction'] = direction
        
        # Two candle patterns
        if i >= 1:
            df.loc[i, 'bullish_engulfing'] = int(is_bullish_engulfing(df.iloc[i-1], df.iloc[i]))
            df.loc[i, 'bearish_engulfing'] = int(is_bearish_engulfing(df.iloc[i-1], df.iloc[i]))
            df.loc[i, 'bullish_harami'] = int(is_bullish_harami(df.iloc[i-1], df.iloc[i]))
            df.loc[i, 'bearish_harami'] = int(is_bearish_harami(df.iloc[i-1], df.iloc[i]))
            df.loc[i, 'tweezer_top'] = int(is_tweezer_top(df.iloc[i-1], df.iloc[i]))
            df.loc[i, 'tweezer_bottom'] = int(is_tweezer_bottom(df.iloc[i-1], df.iloc[i]))
        
        # Three candle patterns
        if i >= 2:
            df.loc[i, 'morning_star'] = int(is_morning_star(df.iloc[i-2], df.iloc[i-1], df.iloc[i]))
            df.loc[i, 'evening_star'] = int(is_evening_star(df.iloc[i-2], df.iloc[i-1], df.iloc[i]))
            df.loc[i, 'three_white_soldiers'] = int(is_three_white_soldiers(df.iloc[i-2], df.iloc[i-1], df.iloc[i]))
            df.loc[i, 'three_black_crows'] = int(is_three_black_crows(df.iloc[i-2], df.iloc[i-1], df.iloc[i]))
    
    return df


def get_candlestick_signals(df):
    """
    Get trading signals based on detected candlestick patterns
    
    Args:
        df: DataFrame with patterns detected
        
    Returns:
        dict: Dictionary with bullish and bearish signals
    """
    # Get the last row
    last_row = df.iloc[-1]
    
    # Identify bullish patterns
    bullish_patterns = []
    if last_row['bullish_engulfing'] == 1:
        bullish_patterns.append('Bullish Engulfing')
    if last_row['hammer'] == 1:
        bullish_patterns.append('Hammer')
    if last_row['morning_star'] == 1:
        bullish_patterns.append('Morning Star')
    if last_row['bullish_harami'] == 1:
        bullish_patterns.append('Bullish Harami')
    if last_row['three_white_soldiers'] == 1:
        bullish_patterns.append('Three White Soldiers')
    if last_row['tweezer_bottom'] == 1:
        bullish_patterns.append('Tweezer Bottom')
    if last_row['marubozu'] == 1 and last_row['marubozu_direction'] == 1:
        bullish_patterns.append('Bullish Marubozu')
    
    # Identify bearish patterns
    bearish_patterns = []
    if last_row['bearish_engulfing'] == 1:
        bearish_patterns.append('Bearish Engulfing')
    if last_row['shooting_star'] == 1:
        bearish_patterns.append('Shooting Star')
    if last_row['evening_star'] == 1:
        bearish_patterns.append('Evening Star')
    if last_row['bearish_harami'] == 1:
        bearish_patterns.append('Bearish Harami')
    if last_row['three_black_crows'] == 1:
        bearish_patterns.append('Three Black Crows')
    if last_row['tweezer_top'] == 1:
        bearish_patterns.append('Tweezer Top')
    if last_row['marubozu'] == 1 and last_row['marubozu_direction'] == -1:
        bearish_patterns.append('Bearish Marubozu')
    
    # Doji is neutral but important
    neutral_patterns = []
    if last_row['doji'] == 1:
        neutral_patterns.append('Doji')
    
    return {
        'bullish_patterns': bullish_patterns,
        'bearish_patterns': bearish_patterns,
        'neutral_patterns': neutral_patterns,
        'all_patterns': bullish_patterns + bearish_patterns + neutral_patterns
    }


def get_pattern_strength(pattern_signals):
    """
    Calculate strength of pattern signals
    
    Args:
        pattern_signals: Dictionary with pattern signals
        
    Returns:
        tuple: (direction, strength)
            direction: 1 for bullish, -1 for bearish, 0 for neutral
            strength: 0-1 score indicating strength of the signal
    """
    # Pattern weights (subjective importance)
    pattern_weights = {
        'Bullish Engulfing': 0.7,
        'Bearish Engulfing': 0.7,
        'Hammer': 0.6,
        'Shooting Star': 0.6,
        'Morning Star': 0.8,
        'Evening Star': 0.8,
        'Bullish Harami': 0.5,
        'Bearish Harami': 0.5,
        'Three White Soldiers': 0.9,
        'Three Black Crows': 0.9,
        'Tweezer Bottom': 0.6,
        'Tweezer Top': 0.6,
        'Bullish Marubozu': 0.7,
        'Bearish Marubozu': 0.7,
        'Doji': 0.3  # Neutral pattern
    }
    
    # Count weighted patterns
    bullish_strength = sum(pattern_weights.get(p, 0.5) for p in pattern_signals['bullish_patterns'])
    bearish_strength = sum(pattern_weights.get(p, 0.5) for p in pattern_signals['bearish_patterns'])
    
    # Normalize strength to 0-1
    max_strength = max(bullish_strength, bearish_strength)
    if max_strength == 0:
        return 0, 0
    
    normalized_strength = max_strength / (len(pattern_signals['all_patterns']) * 0.9 or 1)  # 0.9 is max weight
    normalized_strength = min(normalized_strength, 1.0)  # Cap at 1.0
    
    # Determine direction
    if bullish_strength > bearish_strength:
        return 1, normalized_strength
    elif bearish_strength > bullish_strength:
        return -1, normalized_strength
    else:
        return 0, normalized_strength


def filter_patterns_by_trend(df, patterns, trend):
    """
    Filter candlestick patterns based on the current market trend
    
    Args:
        df: DataFrame with OHLC data and indicators
        patterns: Dictionary with detected patterns
        trend: Current market trend ('UPTREND', 'DOWNTREND', 'SIDEWAYS')
        
    Returns:
        dict: Filtered patterns
    """
    # Copy the patterns dictionary
    filtered_patterns = {
        'bullish_patterns': [],
        'bearish_patterns': [],
        'neutral_patterns': patterns['neutral_patterns'],
        'all_patterns': []
    }
    
    # In an uptrend, bearish reversal patterns are more significant
    if trend == 'UPTREND':
        # High-priority bearish patterns in uptrend (potential reversals)
        high_priority_bearish = [
            'Bearish Engulfing',
            'Evening Star',
            'Shooting Star',
            'Tweezer Top',
            'Three Black Crows',
            'Dark Cloud Cover'
        ]
        
        # Filter bearish patterns to keep only high-priority ones
        filtered_patterns['bearish_patterns'] = [p for p in patterns['bearish_patterns'] 
                                             if p in high_priority_bearish]
        
        # Keep continuation bullish patterns
        continuation_bullish = [
            'Three White Soldiers',
            'Bullish Marubozu'
        ]
        
        filtered_patterns['bullish_patterns'] = [p for p in patterns['bullish_patterns'] 
                                             if p in continuation_bullish]
    
    # In a downtrend, bullish reversal patterns are more significant
    elif trend == 'DOWNTREND':
        # High-priority bullish patterns in downtrend (potential reversals)
        high_priority_bullish = [
            'Bullish Engulfing',
            'Morning Star',
            'Hammer',
            'Tweezer Bottom',
            'Three White Soldiers',
            'Piercing Pattern'
        ]
        
        # Filter bullish patterns to keep only high-priority ones
        filtered_patterns['bullish_patterns'] = [p for p in patterns['bullish_patterns'] 
                                             if p in high_priority_bullish]
        
        # Keep continuation bearish patterns
        continuation_bearish = [
            'Three Black Crows',
            'Bearish Marubozu'
        ]
        
        filtered_patterns['bearish_patterns'] = [p for p in patterns['bearish_patterns'] 
                                             if p in continuation_bearish]
    
    # In sideways markets, all patterns are potentially significant
    else:
        filtered_patterns['bullish_patterns'] = patterns['bullish_patterns']
        filtered_patterns['bearish_patterns'] = patterns['bearish_patterns']
    
    # Update all_patterns
    filtered_patterns['all_patterns'] = (
        filtered_patterns['bullish_patterns'] + 
        filtered_patterns['bearish_patterns'] + 
        filtered_patterns['neutral_patterns']
    )
    
    return filtered_patterns


def pattern_to_signal(df, use_trend_filter=True):
    """
    Convert pattern detection to a trading signal
    
    Args:
        df: DataFrame with OHLC data and indicators
        use_trend_filter: Whether to filter patterns by market trend
        
    Returns:
        dict: Trading signal with confidence and reasoning
    """
    # Detect patterns
    df_with_patterns = detect_candlestick_patterns(df)
    
    # Get pattern signals
    pattern_signals = get_candlestick_signals(df_with_patterns)
    
    # Get trend if available
    trend = 'SIDEWAYS'
    if 'trend' in df.columns:
        trend = df['trend'].iloc[-1]
    
    # Filter patterns by trend if requested
    if use_trend_filter:
        filtered_patterns = filter_patterns_by_trend(df, pattern_signals, trend)
    else:
        filtered_patterns = pattern_signals
    
    # Get pattern strength
    direction, strength = get_pattern_strength(filtered_patterns)
    
    # Determine signal
    signal = 'WAIT'
    if direction > 0:
        signal = 'BUY CALL'
    elif direction < 0:
        signal = 'BUY PUT'
    
    # Generate reason text
    reason = ''
    if filtered_patterns['all_patterns']:
        patterns_text = ', '.join(filtered_patterns['all_patterns'][:3])
        reason = f"Based on detected patterns: {patterns_text} in a {trend.lower()} market"
    else:
        reason = f"No significant patterns detected in {trend.lower()} market"
    
    # Return signal with details
    return {
        'signal': signal,
        'confidence': round(strength, 2),
        'patterns_detected': filtered_patterns['all_patterns'],
        'bullish_patterns': filtered_patterns['bullish_patterns'],
        'bearish_patterns': filtered_patterns['bearish_patterns'],
        'trend': trend,
        'reason': reason
    }