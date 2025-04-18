"""
ML Prediction Module for SAMBOT trading system.
Combines technical indicators, candlestick patterns, and ML model
to generate trading signals with confidence scores.
"""

import pandas as pd
import numpy as np
import joblib
import json
import sys
import os
from datetime import datetime

# Add current directory to path to ensure imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Import indicator and pattern modules if available
try:
    from compute_indicators import add_technical_indicators, get_indicator_signals
    from detect_patterns import analyze_patterns
    MODULES_AVAILABLE = True
except ImportError:
    print("Warning: Could not import indicator or pattern modules. Using simplified analysis.")
    MODULES_AVAILABLE = False


def load_model(model_path="sambot_model.joblib"):
    """
    Load the trained ML model
    
    Args:
        model_path: Path to the trained model
        
    Returns:
        Trained model or None if loading fails
    """
    try:
        model = joblib.load(model_path)
        return model
    except Exception as e:
        print(f"Warning: Failed to load model from {model_path}. Error: {str(e)}")
        return None


def prepare_features(df):
    """
    Prepare features for ML prediction
    
    Args:
        df: DataFrame with OHLCV data
        
    Returns:
        DataFrame with features for ML model
    """
    # Create a copy to avoid modifying the original
    df_features = df.copy()
    
    # Add technical indicators
    if MODULES_AVAILABLE:
        df_features = add_technical_indicators(df_features, include_all=True)
    else:
        # Simple implementations if modules aren't available
        # Moving averages
        df_features['sma_20'] = df_features['close'].rolling(window=20).mean()
        df_features['sma_50'] = df_features['close'].rolling(window=50).mean()
        
        # RSI
        delta = df_features['close'].diff()
        gain = delta.copy()
        loss = delta.copy()
        gain[gain < 0] = 0
        loss[loss > 0] = 0
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = -loss.rolling(window=14).mean()
        rs = avg_gain / avg_loss
        df_features['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
        ema_12 = df_features['close'].ewm(span=12, adjust=False).mean()
        ema_26 = df_features['close'].ewm(span=26, adjust=False).mean()
        df_features['macd'] = ema_12 - ema_26
        df_features['macd_signal'] = df_features['macd'].ewm(span=9, adjust=False).mean()
    
    # Add candlestick patterns
    if MODULES_AVAILABLE:
        pattern_result = analyze_patterns(df_features)
        df_features['bullish_pattern'] = int(pattern_result['signal'] == 'BUY CALL')
        df_features['bearish_pattern'] = int(pattern_result['signal'] == 'BUY PUT')
    else:
        # Simple check for bullish/bearish candles
        df_features['bullish_pattern'] = np.where(df_features['close'] > df_features['open'], 1, 0)
        df_features['bearish_pattern'] = np.where(df_features['close'] < df_features['open'], 1, 0)
    
    # Fill NaN values
    df_features = df_features.fillna(0)
    
    return df_features


def predict_with_model(df_features, model):
    """
    Generate predictions using the ML model
    
    Args:
        df_features: DataFrame with features
        model: Trained ML model
        
    Returns:
        tuple: (signal, confidence)
    """
    # If model is not available, return default prediction
    if model is None:
        # Use basic logic based on indicators
        last_row = df_features.iloc[-1]
        
        if 'rsi' in last_row and 'macd' in last_row and 'macd_signal' in last_row:
            rsi = last_row['rsi']
            macd_cross = last_row['macd'] > last_row['macd_signal']
            
            if rsi < 30 and macd_cross:
                return "BUY CALL", 0.7
            elif rsi > 70 and not macd_cross:
                return "BUY PUT", 0.7
        
        return "WAIT", 0.5
    
    # Select features that the model was trained on
    try:
        # Common features for Indian market analysis
        feature_cols = [
            "open", "high", "low", "close",
            "bullish_pattern", "bearish_pattern",
            "rsi", "macd", "macd_signal"
        ]
        
        # Add volume indicators if available
        if 'volume' in df_features.columns:
            feature_cols.append("volume")
        
        # Add additional features if available
        for col in ["vwap", "supertrend_direction", "atr"]:
            if col in df_features.columns:
                feature_cols.append(col)
        
        # Get the last row for prediction
        X = df_features[feature_cols].iloc[-1:].values
        
        # Make prediction
        prediction = model.predict(X)[0]
        
        # Get confidence from prediction probabilities if available
        if hasattr(model, 'predict_proba'):
            probabilities = model.predict_proba(X)[0]
            confidence = max(probabilities)
        else:
            confidence = 0.7  # Default confidence
        
        # Map prediction to signal
        signal_map = {
            1: "BUY CALL",
            0: "WAIT",
            -1: "BUY PUT"
        }
        
        signal = signal_map.get(prediction, "WAIT")
        
        return signal, confidence
    
    except Exception as e:
        print(f"Error in ML prediction: {str(e)}")
        return "WAIT", 0.5


def combine_with_indicators(ml_signal, ml_confidence, df):
    """
    Combine ML signal with technical indicator signals
    
    Args:
        ml_signal: Signal from ML model
        ml_confidence: Confidence from ML model
        df: DataFrame with features
        
    Returns:
        tuple: (final_signal, final_confidence)
    """
    # Get signals from indicators
    if MODULES_AVAILABLE:
        indicator_result = get_indicator_signals(df)
        indicator_signal = indicator_result['signal']
        indicator_confidence = indicator_result['confidence']
    else:
        # Simple indicator-based signal
        last_row = df.iloc[-1]
        indicator_signal = "WAIT"
        indicator_confidence = 0.5
        
        if 'rsi' in last_row:
            if last_row['rsi'] < 30:
                indicator_signal = "BUY CALL"
                indicator_confidence = 0.7
            elif last_row['rsi'] > 70:
                indicator_signal = "BUY PUT"
                indicator_confidence = 0.7
    
    # Get signals from patterns
    if MODULES_AVAILABLE:
        pattern_result = analyze_patterns(df)
        pattern_signal = pattern_result['signal']
        pattern_confidence = pattern_result['confidence']
    else:
        # Default pattern signal
        pattern_signal = "WAIT"
        pattern_confidence = 0.5
    
    # Define weights for each signal source
    weights = {
        'ml': 0.5,
        'indicator': 0.3,
        'pattern': 0.2
    }
    
    # Calculate weighted score for each signal type
    signal_scores = {
        'BUY CALL': 0,
        'WAIT': 0,
        'BUY PUT': 0
    }
    
    # Add scores from each source
    signal_scores[ml_signal] += weights['ml'] * ml_confidence
    signal_scores[indicator_signal] += weights['indicator'] * indicator_confidence
    signal_scores[pattern_signal] += weights['pattern'] * pattern_confidence
    
    # Find highest scoring signal
    final_signal = max(signal_scores, key=signal_scores.get)
    final_confidence = signal_scores[final_signal]
    
    # Boost confidence if all sources agree
    if ml_signal == indicator_signal == pattern_signal and ml_signal != "WAIT":
        final_confidence = min(final_confidence + 0.1, 0.95)
    
    return final_signal, final_confidence


def calculate_entry_exit_levels(df, signal):
    """
    Calculate entry, stop loss, and target levels
    
    Args:
        df: DataFrame with OHLCV and indicators
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


def predict_signal(df, model_path="sambot_model.joblib", index="NIFTY"):
    """
    Main function to predict signal from OHLCV data
    
    Args:
        df: DataFrame with OHLCV data
        model_path: Path to the trained model
        index: Index name
        
    Returns:
        dict: Prediction results with signal, confidence, etc.
    """
    try:
        # Load ML model
        model = load_model(model_path)
        
        # Prepare features
        df_features = prepare_features(df)
        
        # Get prediction from ML model
        ml_signal, ml_confidence = predict_with_model(df_features, model)
        
        # Combine with indicator and pattern signals
        final_signal, final_confidence = combine_with_indicators(ml_signal, ml_confidence, df_features)
        
        # Calculate entry, stop loss, and target levels
        entry, stop_loss, target = calculate_entry_exit_levels(df_features, final_signal)
        
        # Find optimal strike price
        strike = find_optimal_strike(entry, final_signal, index)
        
        # Get detected patterns
        if MODULES_AVAILABLE:
            pattern_result = analyze_patterns(df)
            patterns_detected = pattern_result.get('patterns_detected', [])
            trend = pattern_result.get('trend', 'UNKNOWN')
        else:
            patterns_detected = []
            trend = "UNKNOWN"
        
        # Generate confidence reason
        if patterns_detected:
            pattern_text = ", ".join(patterns_detected[:2])
            confidence_reason = f"Based on {pattern_text} in a {trend.lower()} market"
        else:
            confidence_reason = f"Based on technical indicators in a {trend.lower()} market"
        
        # Prepare result
        result = {
            "signal": final_signal,
            "confidence": round(final_confidence, 2),
            "ml_signal": ml_signal,
            "ml_confidence": round(ml_confidence, 2),
            "entry": entry,
            "stop_loss": stop_loss,
            "target": target,
            "strike": strike,
            "patterns_detected": patterns_detected,
            "trend": trend,
            "confidence_reason": confidence_reason,
            "index": index,
            "timestamp": datetime.now().isoformat()
        }
        
        return result
        
    except Exception as e:
        print(f"Error in prediction: {str(e)}")
        
        # Return error result
        return {
            "signal": "ERROR",
            "confidence": 0,
            "error": str(e),
            "patterns_detected": [],
            "trend": "UNKNOWN",
            "confidence_reason": f"Error in prediction: {str(e)}"
        }


def main():
    """
    Main function for standalone execution
    """
    # Check if command line arguments are provided
    if len(sys.argv) > 8:
        try:
            # Create test data from command line arguments
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
            
            # Create test DataFrame
            df = pd.DataFrame([c1, c2])
            
            # Add volume (mock data)
            df['volume'] = [100000, 120000]
            
            # Set index if provided
            index = sys.argv[9] if len(sys.argv) > 9 else "NIFTY"
            
            # Get prediction
            result = predict_signal(df, index=index)
            
            # Print result as JSON
            print(json.dumps(result, indent=2))
            
        except Exception as e:
            print(json.dumps({"error": str(e)}))
            
    elif len(sys.argv) > 1:
        try:
            # Read CSV file
            df = pd.read_csv(sys.argv[1])
            
            # Get prediction
            result = predict_signal(df)
            
            # Print result as JSON
            print(json.dumps(result, indent=2))
            
        except Exception as e:
            print(json.dumps({"error": str(e)}))
    
    else:
        print("Usage: python predict_ml_signal.py open1 high1 low1 close1 open2 high2 low2 close2 [index]")
        print("   or: python predict_ml_signal.py <csv_file>")


if __name__ == "__main__":
    main()