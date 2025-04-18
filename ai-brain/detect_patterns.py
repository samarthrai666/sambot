"""
Main candlestick pattern detection module for SAMBOT trading system.
This module serves as a wrapper for the patterns package.
"""

import pandas as pd
import numpy as np
import json
import sys
import os

# Add current directory to path to ensure imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Import from patterns package
try:
    from patterns import (
        detect_candlestick_patterns,
        get_candlestick_signals,
        get_pattern_strength,
        pattern_to_signal
    )
    PATTERNS_PACKAGE_AVAILABLE = True
except ImportError:
    print("Warning: Could not import from patterns package. Using original implementation.")
    PATTERNS_PACKAGE_AVAILABLE = False
    
    # Original functions from detect_patterns.py
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


def detect_candlestick_patterns_legacy(df):
    """
    Original pattern detection function (legacy)
    
    Args:
        df: DataFrame with OHLC data
        
    Returns:
        DataFrame with pattern columns
    """
    # Make sure df is a copy
    df = df.copy()
    
    # Initialize pattern columns
    df['bullish_engulfing'] = 0
    df['bearish_engulfing'] = 0
    df['doji'] = 0
    df['hammer'] = 0
    df['shooting_star'] = 0
    
    for i in range(1, len(df)):
        # Check for two-candle patterns
        df.loc[i, 'bullish_engulfing'] = int(is_bullish_engulfing(df.iloc[i-1], df.iloc[i]))
        df.loc[i, 'bearish_engulfing'] = int(is_bearish_engulfing(df.iloc[i-1], df.iloc[i]))
        
        # Check for single-candle patterns
        df.loc[i, 'doji'] = int(is_doji(df.iloc[i]))
        df.loc[i, 'hammer'] = int(is_hammer(df.iloc[i]))
        df.loc[i, 'shooting_star'] = int(is_shooting_star(df.iloc[i]))
    
    return df


def get_pattern_signals_legacy(df):
    """
    Original function to get trading signals from patterns (legacy)
    
    Args:
        df: DataFrame with patterns
        
    Returns:
        dict: Pattern signals
    """
    # Get the last row
    last_row = df.iloc[-1]
    
    # Initialize pattern lists
    patterns_detected = []
    
    # Check for bullish patterns
    if last_row['bullish_engulfing'] == 1:
        patterns_detected.append('Bullish Engulfing')
    if last_row['hammer'] == 1:
        patterns_detected.append('Hammer')
    
    # Check for bearish patterns
    if last_row['bearish_engulfing'] == 1:
        patterns_detected.append('Bearish Engulfing')
    if last_row['shooting_star'] == 1:
        patterns_detected.append('Shooting Star')
    
    # Check for neutral patterns
    if last_row['doji'] == 1:
        patterns_detected.append('Doji')
    
    return {
        'patterns_detected': patterns_detected,
        'has_bullish': last_row['bullish_engulfing'] == 1 or last_row['hammer'] == 1,
        'has_bearish': last_row['bearish_engulfing'] == 1 or last_row['shooting_star'] == 1
    }


def analyze_patterns(df):
    """
    Main function to analyze patterns in price data
    
    Args:
        df: DataFrame with OHLC data
        
    Returns:
        dict: Analysis results with signals and pattern info
    """
    if PATTERNS_PACKAGE_AVAILABLE:
        # Use the enhanced package implementation
        return pattern_to_signal(df)
    else:
        # Use legacy implementation
        df_with_patterns = detect_candlestick_patterns_legacy(df)
        pattern_signals = get_pattern_signals_legacy(df_with_patterns)
        
        # Determine signal based on detected patterns
        signal = 'WAIT'
        confidence = 0.5
        
        if pattern_signals['has_bullish'] and not pattern_signals['has_bearish']:
            signal = 'BUY CALL'
            confidence = 0.7
        elif pattern_signals['has_bearish'] and not pattern_signals['has_bullish']:
            signal = 'BUY PUT'
            confidence = 0.7
        
        # Create reason text
        reason = ''
        if pattern_signals['patterns_detected']:
            patterns_text = ', '.join(pattern_signals['patterns_detected'])
            reason = f"Based on detected patterns: {patterns_text}"
        else:
            reason = "No significant patterns detected"
        
        return {
            'signal': signal,
            'confidence': confidence,
            'patterns_detected': pattern_signals['patterns_detected'],
            'reason': reason
        }


def main():
    """
    Main function for standalone execution
    """
    import sys
    
    # Usage with candle data from command line
    if len(sys.argv) > 8:
        try:
            # Parse candle data from arguments
            c1 = {
                'open': float(sys.argv[1]),
                'high': float(sys.argv[2]),
                'low': float(sys.argv[3]),
                'close': float(sys.argv[4])
            }
            
            c2 = {
                'open': float(sys.argv[5]),
                'high': float(sys.argv[6]),
                'low': float(sys.argv[7]),
                'close': float(sys.argv[8])
            }
            
            # Create test dataframe
            df = pd.DataFrame([c1, c2])
            
            # Analyze patterns
            result = analyze_patterns(df)
            
            # Print result as JSON
            print(json.dumps(result, indent=2))
            
        except Exception as e:
            print(json.dumps({'error': str(e)}))
    
    # Usage with CSV file
    elif len(sys.argv) > 1:
        try:
            # Read CSV file
            df = pd.read_csv(sys.argv[1])
            
            # Analyze patterns
            result = analyze_patterns(df)
            
            # Print result as JSON
            print(json.dumps(result, indent=2))
            
        except Exception as e:
            print(json.dumps({'error': str(e)}))
    
    else:
        print("Usage: python detect_patterns.py <csv_file>")
        print("   or: python detect_patterns.py open1 high1 low1 close1 open2 high2 low2 close2")


if __name__ == "__main__":
    main()