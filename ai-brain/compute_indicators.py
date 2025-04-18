"""
Main technical indicators module for SAMBOT trading system.
This module serves as a wrapper for the indicators package.
"""

import pandas as pd
import numpy as np
import os
import sys
import json

# Add current directory to path to ensure imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Import from indicators package
try:
    from indicators import (
        add_technical_indicators,
        get_trend_strength,
        get_indicator_signals
    )
except ImportError:
    print("Warning: Could not import from indicators package. Using fallback implementations.")
    
    def add_technical_indicators(df, include_all=False):
        """Fallback implementation of add_technical_indicators"""
        df = df.copy()
        
        # Basic moving averages
        df['sma_20'] = df['close'].rolling(window=20).mean()
        df['sma_50'] = df['close'].rolling(window=50).mean()
        df['ema_9'] = df['close'].ewm(span=9, adjust=False).mean()
        df['ema_20'] = df['close'].ewm(span=20, adjust=False).mean()
        
        # Basic RSI
        delta = df['close'].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        rs = avg_gain / avg_loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # Basic MACD
        ema_12 = df['close'].ewm(span=12, adjust=False).mean()
        ema_26 = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = ema_12 - ema_26
        df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        
        # Fill NaN values
        df = df.fillna(0)
        
        return df
    
    def get_trend_strength(df):
        """Fallback implementation of get_trend_strength"""
        last = df.iloc[-1]
        
        # Simple trend determination based on MAs
        if 'sma_20' in last and 'sma_50' in last:
            if last['close'] > last['sma_20'] and last['sma_20'] > last['sma_50']:
                return 'UPTREND', 0.8
            elif last['close'] < last['sma_20'] and last['sma_20'] < last['sma_50']:
                return 'DOWNTREND', 0.8
        
        return 'SIDEWAYS', 0.5
    
    def get_indicator_signals(df):
        """Fallback implementation of get_indicator_signals"""
        last = df.iloc[-1]
        trend, strength = get_trend_strength(df)
        
        signal = 'WAIT'
        if trend == 'UPTREND' and last.get('rsi', 50) < 70:
            signal = 'BUY CALL'
        elif trend == 'DOWNTREND' and last.get('rsi', 50) > 30:
            signal = 'BUY PUT'
        
        return {
            'signal': signal,
            'confidence': strength,
            'trend': trend,
            'trend_strength': strength,
            'bullish_signals': [],
            'bearish_signals': [],
            'reasons': f"Simple {trend.lower()} detection"
        }


def process_candle_data(df, include_all_indicators=False):
    """
    Process candle data by adding technical indicators and generating signals
    
    Args:
        df: DataFrame with OHLCV data
        include_all_indicators: Whether to include all available indicators
        
    Returns:
        DataFrame: Original DataFrame with indicators added
    """
    # Add technical indicators
    df_with_indicators = add_technical_indicators(df, include_all=include_all_indicators)
    
    return df_with_indicators


def analyze_market_data(df):
    """
    Analyze market data and generate trading signals
    
    Args:
        df: DataFrame with OHLCV data and indicators
        
    Returns:
        dict: Trading signals and market analysis
    """
    # Generate signals
    signals = get_indicator_signals(df)
    
    # Get trend information
    trend, strength = get_trend_strength(df)
    
    # Get the last row for current values
    last = df.iloc[-1]
    
    # Create result with key indicators
    result = {
        "signal": signals['signal'],
        "confidence": signals['confidence'],
        "trend": trend,
        "trend_strength": strength,
        "reasons": signals['reasons'],
        
        # Add key indicator values
        "rsi": round(float(last.get('rsi', 50)), 2),
        "macd": round(float(last.get('macd', 0)), 2),
        "macd_signal": round(float(last.get('macd_signal', 0)), 2),
        
        # Add bullish and bearish signals
        "bullish_signals": signals['bullish_signals'],
        "bearish_signals": signals['bearish_signals']
    }
    
    # Return the analysis result
    return result


def calculate_entry_exit_levels(df, signal):
    """
    Calculate entry, stop loss, and target levels for a trade
    
    Args:
        df: DataFrame with OHLCV data and indicators
        signal: Trading signal (BUY CALL, BUY PUT, WAIT)
        
    Returns:
        tuple: (entry, stop_loss, target)
    """
    # Get current price from last candle
    current_price = df['close'].iloc[-1]
    
    # Use ATR for stop loss and target if available
    if 'atr' in df.columns:
        atr = df['atr'].iloc[-1]
    else:
        # Approximate ATR if not calculated
        high_low_diff = df['high'].iloc[-5:].max() - df['low'].iloc[-5:].min()
        atr = high_low_diff / 5
    
    # Calculate levels based on signal
    if signal == "BUY CALL":
        entry = current_price
        stop_loss = entry - (atr * 1.5)
        target = entry + (atr * 2.5)  # Risk:Reward ratio of 1:1.67
    elif signal == "BUY PUT":
        entry = current_price
        stop_loss = entry + (atr * 1.5)
        target = entry - (atr * 2.5)  # Risk:Reward ratio of 1:1.67
    else:
        entry = current_price
        stop_loss = 0
        target = 0
    
    return round(entry, 2), round(stop_loss, 2), round(target, 2)


def find_optimal_strike(current_price, signal, index="NIFTY"):
    """
    Find the optimal strike price for options trading
    
    Args:
        current_price: Current price of the underlying
        signal: Trading signal (BUY CALL, BUY PUT, WAIT)
        index: Index name (NIFTY, BANKNIFTY)
        
    Returns:
        int: Optimal strike price
    """
    # Set strike step based on index
    if index == "NIFTY":
        strike_step = 50
    elif index == "BANKNIFTY":
        strike_step = 100
    else:
        strike_step = 50  # Default
    
    # Find ATM strike
    atm_strike = round(current_price / strike_step) * strike_step
    
    # For BUY CALL, choose slightly ITM strike for better delta
    if signal == "BUY CALL":
        return atm_strike - strike_step
    
    # For BUY PUT, choose slightly ITM strike for better delta
    elif signal == "BUY PUT":
        return atm_strike + strike_step
    
    # For WAIT, return ATM strike
    else:
        return atm_strike


def main():
    """
    Main function for standalone execution
    """
    import sys
    
    # Check if CSV file is provided
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
        
        try:
            # Read CSV file
            df = pd.read_csv(csv_file)
            
            # Process data
            df = process_candle_data(df, include_all_indicators=True)
            
            # Analyze data
            result = analyze_market_data(df)
            
            # Calculate entry, stop loss, and target
            entry, stop_loss, target = calculate_entry_exit_levels(df, result['signal'])
            
            # Find optimal strike
            strike = find_optimal_strike(entry, result['signal'])
            
            # Add to result
            result['entry'] = entry
            result['stop_loss'] = stop_loss
            result['target'] = target
            result['strike'] = strike
            
            # Print result
            print(json.dumps(result, indent=2))
            
        except Exception as e:
            print(json.dumps({'error': str(e)}))
    else:
        print("Usage: python compute_indicators.py <csv_file>")


if __name__ == "__main__":
    main()