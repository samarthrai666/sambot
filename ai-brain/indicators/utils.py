"""
Utility functions for technical indicators in SAMBOT trading system.
Includes trend analysis, signal generation, and other helper functions.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def get_trend_strength(df):
    """
    Get overall trend strength based on multiple indicators
    
    Args:
        df: DataFrame with technical indicators
        
    Returns:
        tuple: (trend, strength)
            trend: 'UPTREND', 'DOWNTREND', or 'SIDEWAYS'
            strength: 0-1 score indicating strength of the trend
    """
    # Get the last row for current values
    last = df.iloc[-1]
    
    # Initialize scores
    bullish_points = 0
    bearish_points = 0
    max_points = 0
    
    # 1. Moving Average relationship
    if 'price_to_sma_20' in last and 'price_to_sma_50' in last:
        max_points += 3
        if last['close'] > last['sma_20'] and last['sma_20'] > last['sma_50']:
            bullish_points += 3  # Strong uptrend
        elif last['close'] > last['sma_20'] and last['sma_20'] < last['sma_50']:
            bullish_points += 1  # Potential reversal up
        elif last['close'] < last['sma_20'] and last['sma_20'] < last['sma_50']:
            bearish_points += 3  # Strong downtrend
        elif last['close'] < last['sma_20'] and last['sma_20'] > last['sma_50']:
            bearish_points += 1  # Potential reversal down
    
    # 2. RSI
    if 'rsi' in last:
        max_points += 2
        if last['rsi'] > 60:
            bullish_points += 2
        elif last['rsi'] < 40:
            bearish_points += 2
        elif last['rsi'] > 50:
            bullish_points += 1
        elif last['rsi'] < 50:
            bearish_points += 1
    
    # 3. MACD
    if 'macd' in last and 'macd_signal' in last:
        max_points += 2
        if last['macd'] > last['macd_signal'] and last['macd'] > 0:
            bullish_points += 2
        elif last['macd'] > last['macd_signal'] and last['macd'] < 0:
            bullish_points += 1
        elif last['macd'] < last['macd_signal'] and last['macd'] < 0:
            bearish_points += 2
        elif last['macd'] < last['macd_signal'] and last['macd'] > 0:
            bearish_points += 1
    
    # 4. Bollinger Bands
    if 'bb_pct_b' in last:
        max_points += 2
        if last['bb_pct_b'] > 0.8:
            bullish_points += 2
        elif last['bb_pct_b'] < 0.2:
            bearish_points += 2
        elif last['bb_pct_b'] > 0.5:
            bullish_points += 1
        elif last['bb_pct_b'] < 0.5:
            bearish_points += 1
    
    # 5. Supertrend
    if 'supertrend_direction' in last:
        max_points += 3
        if last['supertrend_direction'] == 1:
            bullish_points += 3
        else:
            bearish_points += 3
    
    # 6. Price relative to VWAP
    if 'price_to_vwap' in last:
        max_points += 1
        if last['price_to_vwap'] > 1:
            bullish_points += 1
        else:
            bearish_points += 1
    
    # 7. ADX (trend strength)
    if 'adx' in last and 'plus_di' in last and 'minus_di' in last:
        max_points += 2
        if last['adx'] > 25:  # Strong trend
            if last['plus_di'] > last['minus_di']:
                bullish_points += 2
            else:
                bearish_points += 2
    
    # 8. Volume-based indicators (For Indian markets)
    if 'relative_volume' in last and 'volume_spike' in last:
        max_points += 2
        if last['volume_spike']:
            # High volume with price direction
            if last['close'] > last['open']:
                bullish_points += 2
            else:
                bearish_points += 2
    
    # 9. Delivery percentage (Indian market specific)
    if 'high_delivery' in last:
        max_points += 2
        if last['high_delivery']:
            # High delivery with price direction
            if last['close'] > last['open']:
                bullish_points += 2
            else:
                bearish_points += 2
    
    # Calculate final trend
    if max_points == 0:
        return 'SIDEWAYS', 0.5
    
    if bullish_points > bearish_points:
        trend = 'UPTREND'
        strength = min(bullish_points / max_points, 1.0)
    elif bearish_points > bullish_points:
        trend = 'DOWNTREND'
        strength = min(bearish_points / max_points, 1.0)
    else:
        trend = 'SIDEWAYS'
        strength = 0.5
    
    return trend, strength


def get_indicator_signals(df):
    """
    Get trading signals based on technical indicators
    
    Args:
        df: DataFrame with indicators
        
    Returns:
        dict: Dictionary with signal details
    """
    # Get the last row for current values
    last = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else last
    
    # Get trend strength
    trend, strength = get_trend_strength(df)
    
    # Initialize signals
    bullish_signals = []
    bearish_signals = []
    
    # Check MA crossovers
    if 'ema_9' in last and 'ema_20' in last:
        if prev['ema_9'] <= prev['ema_20'] and last['ema_9'] > last['ema_20']:
            bullish_signals.append('EMA 9-20 Bullish Crossover')
        elif prev['ema_9'] >= prev['ema_20'] and last['ema_9'] < last['ema_20']:
            bearish_signals.append('EMA 9-20 Bearish Crossover')
    
    # Check RSI conditions
    if 'rsi' in last:
        if last['rsi'] < 30:
            bullish_signals.append('RSI Oversold')
        elif last['rsi'] > 70:
            bearish_signals.append('RSI Overbought')
    
    # Check MACD crossovers
    if 'macd' in last and 'macd_signal' in last:
        if prev['macd'] <= prev['macd_signal'] and last['macd'] > last['macd_signal']:
            bullish_signals.append('MACD Bullish Crossover')
        elif prev['macd'] >= prev['macd_signal'] and last['macd'] < last['macd_signal']:
            bearish_signals.append('MACD Bearish Crossover')
    
    # Check Bollinger Band conditions
    if 'bb_lower' in last and 'bb_upper' in last:
        if last['close'] < last['bb_lower']:
            bullish_signals.append('Price Below Lower Bollinger Band')
        elif last['close'] > last['bb_upper']:
            bearish_signals.append('Price Above Upper Bollinger Band')
    
    # Check Supertrend
    if 'supertrend_direction' in last:
        if prev['supertrend_direction'] == -1 and last['supertrend_direction'] == 1:
            bullish_signals.append('Supertrend Bullish Flip')
        elif prev['supertrend_direction'] == 1 and last['supertrend_direction'] == -1:
            bearish_signals.append('Supertrend Bearish Flip')
    
    # Check VWAP relationship
    if 'vwap' in last:
        if prev['close'] < prev['vwap'] and last['close'] > last['vwap']:
            bullish_signals.append('Price Crossed Above VWAP')
        elif prev['close'] > prev['vwap'] and last['close'] < last['vwap']:
            bearish_signals.append('Price Crossed Below VWAP')
    
    # Check volume signals (Indian market specific)
    if 'volume_spike' in last and 'ultra_high_volume' in last:
        if last['volume_spike']:
            if last['close'] > last['open']:
                bullish_signals.append('Bullish Volume Spike')
            else:
                bearish_signals.append('Bearish Volume Spike')
        
        if last['ultra_high_volume'] and last['close'] > last['open']:
            bullish_signals.append('Ultra-High Volume Bullish')
    
    # Check delivery percentage (Indian market specific)
    if 'high_delivery' in last and 'delivery_trend_up' in last:
        if last['high_delivery'] and last['close'] > last['open']:
            bullish_signals.append('High Delivery Bullish')
        elif last['high_delivery'] and last['close'] < last['open']:
            bearish_signals.append('High Delivery Bearish')
    
    # Prepare final signal
    if len(bullish_signals) > len(bearish_signals) and trend == 'UPTREND':
        signal = 'BUY CALL'
        confidence = min(0.5 + (len(bullish_signals) / 10) + strength, 0.95)
    elif len(bearish_signals) > len(bullish_signals) and trend == 'DOWNTREND':
        signal = 'BUY PUT'
        confidence = min(0.5 + (len(bearish_signals) / 10) + strength, 0.95)
    else:
        signal = 'WAIT'
        confidence = 0.5
    
    # Format reasons
    reasons = []
    if bullish_signals and signal == 'BUY CALL':
        reasons.extend(bullish_signals[:3])  # Include top 3 bullish signals
    elif bearish_signals and signal == 'BUY PUT':
        reasons.extend(bearish_signals[:3])  # Include top 3 bearish signals
    else:
        reasons.append(f"Mixed signals in {trend.lower()} market")
    
    reason_text = ", ".join(reasons)
    
    return {
        'signal': signal,
        'confidence': round(confidence, 2),
        'trend': trend,
        'trend_strength': round(strength, 2),
        'bullish_signals': bullish_signals,
        'bearish_signals': bearish_signals,
        'reasons': reason_text
    }


def calculate_target_stoploss(df, signal, atr_multiplier=1.5, rr_ratio=1.5):
    """
    Calculate target and stop loss levels based on ATR
    
    Args:
        df: DataFrame with OHLCV and indicators
        signal: Trading signal (BUY CALL, BUY PUT, WAIT)
        atr_multiplier: Multiplier for ATR to determine stop loss
        rr_ratio: Risk-Reward ratio for target calculation
        
    Returns:
        tuple: (entry, stop_loss, target)
    """
    # Get current price
    current_price = df['close'].iloc[-1]
    
    # Use ATR for stop loss and target if available
    if 'atr' in df.columns:
        atr = df['atr'].iloc[-1]
    else:
        # Approximate ATR as average of recent high-low ranges
        atr = (df['high'] - df['low']).iloc[-5:].mean()
    
    # Calculate levels based on signal
    if signal == "BUY CALL":
        entry = current_price
        stop_loss = entry - (atr * atr_multiplier)
        target = entry + (atr * atr_multiplier * rr_ratio)
    elif signal == "BUY PUT":
        entry = current_price
        stop_loss = entry + (atr * atr_multiplier)
        target = entry - (atr * atr_multiplier * rr_ratio)
    else:
        entry = current_price
        stop_loss = 0
        target = 0
    
    return round(entry, 2), round(stop_loss, 2), round(target, 2)


def get_expiry_strike(df, signal, index="NIFTY"):
    """
    Calculate optimal strike and expiry for options trading
    
    Args:
        df: DataFrame with OHLCV and indicators
        signal: Trading signal (BUY CALL, BUY PUT, WAIT)
        index: Index name (NIFTY, BANKNIFTY, etc.)
        
    Returns:
        dict: Optimal strike and expiry info
    """
    # Get the current price
    current_price = df['close'].iloc[-1]
    
    # Get strike step based on the index (Indian market specific)
    if index == "NIFTY":
        strike_step = 50
    elif index == "BANKNIFTY":
        strike_step = 100
    elif index == "FINNIFTY":
        strike_step = 50
    else:
        strike_step = 50  # Default
    
    # Find ATM strike
    atm_strike = round(current_price / strike_step) * strike_step
    
    # Determine optimal strike based on signal
    if signal == "BUY CALL":
        # For calls, prefer slightly ITM for better delta
        optimal_strike = atm_strike - strike_step
    elif signal == "BUY PUT":
        # For puts, prefer slightly ITM for better delta
        optimal_strike = atm_strike + strike_step
    else:
        optimal_strike = atm_strike
    
    # NSE weekly expiry is Thursday
    today = datetime.now().date()
    days_to_thursday = (3 - today.weekday()) % 7
    
    # If today is Thursday afternoon, use next week
    if today.weekday() == 3 and datetime.now().hour >= 15:
        days_to_thursday += 7
    
    # Next expiry date
    next_expiry = today + timedelta(days=days_to_thursday)
    
    return {
        'strike': optimal_strike,
        'type': 'CE' if signal == 'BUY CALL' else 'PE',
        'expiry': next_expiry.strftime('%d-%b-%Y'),
        'atm_strike': atm_strike,
        'current_price': current_price
    }


def generate_decision_table(df, window=5):
    """
    Generate a decision table with signals from multiple timeframes
    
    Args:
        df: DataFrame with OHLCV data
        window: Number of recent periods to analyze
        
    Returns:
        pd.DataFrame: Decision table with signals
    """
    # Create a decision table
    decision_table = pd.DataFrame()
    
    # Get recent window of data
    recent_df = df.iloc[-window:].copy()
    
    # Add date/time information
    decision_table['timestamp'] = recent_df['timestamp'] if 'timestamp' in recent_df.columns else recent_df.index
    
    # Add price data
    decision_table['open'] = recent_df['open']
    decision_table['high'] = recent_df['high']
    decision_table['low'] = recent_df['low']
    decision_table['close'] = recent_df['close']
    decision_table['volume'] = recent_df['volume']
    
    # Add key indicators
    if 'rsi' in recent_df.columns:
        decision_table['rsi'] = recent_df['rsi'].round(2)
    
    if 'macd' in recent_df.columns and 'macd_signal' in recent_df.columns:
        decision_table['macd'] = recent_df['macd'].round(2)
        decision_table['macd_signal'] = recent_df['macd_signal'].round(2)
        decision_table['macd_hist'] = (recent_df['macd'] - recent_df['macd_signal']).round(2)
    
    if 'supertrend' in recent_df.columns:
        decision_table['supertrend'] = recent_df['supertrend'].round(2)
        decision_table['trend_direction'] = recent_df['supertrend_direction']
    
    # Add VWAP
    if 'vwap' in recent_df.columns:
        decision_table['vwap'] = recent_df['vwap'].round(2)
        decision_table['price_to_vwap'] = (recent_df['close'] / recent_df['vwap']).round(4)
    
    # Add simple signals
    decision_table['rsi_signal'] = np.where(
        recent_df['rsi'] > 70, 'Overbought', 
        np.where(recent_df['rsi'] < 30, 'Oversold', 'Neutral')
    ) if 'rsi' in recent_df.columns else 'N/A'
    
    decision_table['macd_signal'] = np.where(
        recent_df['macd'] > recent_df['macd_signal'], 'Bullish', 'Bearish'
    ) if 'macd' in recent_df.columns and 'macd_signal' in recent_df.columns else 'N/A'
    
    # Add overall signal based on the last row
    last_signals = get_indicator_signals(df)
    decision_table['overall_signal'] = [last_signals['signal']] * len(decision_table)
    decision_table['confidence'] = [last_signals['confidence']] * len(decision_table)
    
    return decision_table


def detect_divergences(df, periods=14):
    """
    Detect price-indicator divergences (bullish and bearish)
    
    Args:
        df: DataFrame with OHLCV and indicators
        periods: Number of periods to look back for divergence
        
    Returns:
        dict: Divergence detection results
    """
    try:
        # Prepare result
        divergences = {
            'rsi_bullish_div': False,
            'rsi_bearish_div': False,
            'macd_bullish_div': False,
            'macd_bearish_div': False,
            'obv_bullish_div': False,
            'obv_bearish_div': False,
            'details': []
        }
        
        # Get recent window of data for analysis
        window = min(periods, len(df) - 1)
        recent_df = df.iloc[-window:].copy()
        
        # Find recent swing lows and highs in price
        price_swing_low = recent_df['close'].rolling(5, center=True).min()
        price_swing_high = recent_df['close'].rolling(5, center=True).max()
        
        # Bullish divergence: Price makes lower low but indicator makes higher low
        # Bearish divergence: Price makes higher high but indicator makes lower high
        
        # Check RSI divergence
        if 'rsi' in recent_df.columns:
            rsi = recent_df['rsi']
            
            # Find swing lows/highs in RSI
            rsi_swing_low = rsi.rolling(5, center=True).min()
            rsi_swing_high = rsi.rolling(5, center=True).max()
            
            # Check for bullish divergence (price low, RSI higher low)
            if price_swing_low.iloc[-1] == recent_df['close'].iloc[-1]:  # Current price is a swing low
                if rsi.iloc[-1] > rsi_swing_low.iloc[-5:-1].min():  # RSI is not making a new low
                    divergences['rsi_bullish_div'] = True
                    divergences['details'].append("Bullish RSI Divergence: Price made new low but RSI didn't")
            
            # Check for bearish divergence (price high, RSI lower high)
            if price_swing_high.iloc[-1] == recent_df['close'].iloc[-1]:  # Current price is a swing high
                if rsi.iloc[-1] < rsi_swing_high.iloc[-5:-1].max():  # RSI is not making a new high
                    divergences['rsi_bearish_div'] = True
                    divergences['details'].append("Bearish RSI Divergence: Price made new high but RSI didn't")
        
        # Check MACD divergence 
        if 'macd' in recent_df.columns:
            macd = recent_df['macd']
            
            # Find swing lows/highs in MACD
            macd_swing_low = macd.rolling(5, center=True).min()
            macd_swing_high = macd.rolling(5, center=True).max()
            
            # Check for bullish divergence
            if price_swing_low.iloc[-1] == recent_df['close'].iloc[-1]:
                if macd.iloc[-1] > macd_swing_low.iloc[-5:-1].min():
                    divergences['macd_bullish_div'] = True
                    divergences['details'].append("Bullish MACD Divergence: Price made new low but MACD didn't")
            
            # Check for bearish divergence
            if price_swing_high.iloc[-1] == recent_df['close'].iloc[-1]:
                if macd.iloc[-1] < macd_swing_high.iloc[-5:-1].max():
                    divergences['macd_bearish_div'] = True
                    divergences['details'].append("Bearish MACD Divergence: Price made new high but MACD didn't")
        
        # Check OBV divergence
        if 'obv' in recent_df.columns:
            obv = recent_df['obv']
            
            # Find swing lows/highs in OBV
            obv_swing_low = obv.rolling(5, center=True).min()
            obv_swing_high = obv.rolling(5, center=True).max()
            
            # Check for bullish divergence
            if price_swing_low.iloc[-1] == recent_df['close'].iloc[-1]:
                if obv.iloc[-1] > obv_swing_low.iloc[-5:-1].min():
                    divergences['obv_bullish_div'] = True
                    divergences['details'].append("Bullish OBV Divergence: Price made new low but OBV didn't")
            
            # Check for bearish divergence
            if price_swing_high.iloc[-1] == recent_df['close'].iloc[-1]:
                if obv.iloc[-1] < obv_swing_high.iloc[-5:-1].max():
                    divergences['obv_bearish_div'] = True
                    divergences['details'].append("Bearish OBV Divergence: Price made new high but OBV didn't")
        
        return divergences
    
    except Exception as e:
        print(f"Error detecting divergences: {str(e)}")
        return {
            'rsi_bullish_div': False,
            'rsi_bearish_div': False,
            'macd_bullish_div': False,
            'macd_bearish_div': False,
            'obv_bullish_div': False,
            'obv_bearish_div': False,
            'details': [f"Error: {str(e)}"]
        }


def calculate_risk_reward_profile(df, signal, stop_loss, target, risk_capital=10000, lot_size=50):
    """
    Calculate risk-reward profile for a trade
    
    Args:
        df: DataFrame with OHLCV data
        signal: Trading signal (BUY CALL, BUY PUT)
        stop_loss: Stop loss price
        target: Target price
        risk_capital: Amount willing to risk (INR)
        lot_size: Lot size for the instrument
        
    Returns:
        dict: Risk-reward profile details
    """
    try:
        # Get current price
        current_price = df['close'].iloc[-1]
        
        # Calculate risk per point
        if signal == "BUY CALL":
            risk_per_point = current_price - stop_loss
            reward_per_point = target - current_price
        elif signal == "BUY PUT":
            risk_per_point = stop_loss - current_price
            reward_per_point = current_price - target
        else:
            return {
                "risk_reward_ratio": 0,
                "max_risk_inr": 0,
                "max_reward_inr": 0,
                "suggested_lots": 0,
                "capital_required": 0
            }
        
        # Calculate risk-reward ratio
        risk_reward_ratio = reward_per_point / risk_per_point if risk_per_point > 0 else 0
        
        # Calculate maximum risk and reward in INR
        max_risk_per_lot = risk_per_point * lot_size
        max_reward_per_lot = reward_per_point * lot_size
        
        # Calculate number of lots based on risk capital
        suggested_lots = int(risk_capital / max_risk_per_lot) if max_risk_per_lot > 0 else 0
        suggested_lots = max(1, suggested_lots)  # At least 1 lot
        
        # Calculate total capital required
        margin_per_lot = current_price * lot_size * 0.2  # Assuming 20% margin requirement
        capital_required = margin_per_lot * suggested_lots
        
        return {
            "risk_reward_ratio": round(risk_reward_ratio, 2),
            "max_risk_inr": round(max_risk_per_lot * suggested_lots, 2),
            "max_reward_inr": round(max_reward_per_lot * suggested_lots, 2),
            "suggested_lots": suggested_lots,
            "capital_required": round(capital_required, 2)
        }
    
    except Exception as e:
        print(f"Error calculating risk-reward profile: {str(e)}")
        return {
            "risk_reward_ratio": 0,
            "max_risk_inr": 0,
            "max_reward_inr": 0,
            "suggested_lots": 0,
            "capital_required": 0,
            "error": str(e)
        }