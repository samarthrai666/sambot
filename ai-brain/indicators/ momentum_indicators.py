"""
Momentum technical indicators module for SAMBOT trading system.
Includes RSI, MACD, Stochastic, and other momentum-based indicators.
"""

import numpy as np
import pandas as pd

try:
    import talib
    TALIB_AVAILABLE = True
except ImportError:
    TALIB_AVAILABLE = False


def add_rsi(df, period=14):
    """
    Add Relative Strength Index (RSI) indicator
    
    Args:
        df: DataFrame with OHLCV data
        period: RSI period
        
    Returns:
        DataFrame with RSI added
    """
    try:
        if TALIB_AVAILABLE:
            # Use talib for accuracy if available
            df['rsi'] = talib.RSI(df['close'].values, timeperiod=period)
        else:
            # Fallback to pandas implementation
            delta = df['close'].diff()
            gain = delta.clip(lower=0)
            loss = -delta.clip(upper=0)
            
            # Calculate average gain and loss
            avg_gain = gain.rolling(window=period).mean()
            avg_loss = loss.rolling(window=period).mean()
            
            # Calculate RS and RSI
            rs = avg_gain / avg_loss
            df['rsi'] = 100 - (100 / (1 + rs))
        
        # Add RSI conditions
        df['rsi_overbought'] = df['rsi'] > 70
        df['rsi_oversold'] = df['rsi'] < 30
    
    except Exception as e:
        print(f"Error calculating RSI: {str(e)}")
        # Add empty RSI columns to avoid errors
        df['rsi'] = 50  # Neutral value
        df['rsi_overbought'] = False
        df['rsi_oversold'] = False
    
    return df


def add_macd(df, fast=12, slow=26, signal=9):
    """
    Add Moving Average Convergence Divergence (MACD) indicator
    
    Args:
        df: DataFrame with OHLCV data
        fast: Fast EMA period
        slow: Slow EMA period
        signal: Signal EMA period
        
    Returns:
        DataFrame with MACD added
    """
    try:
        if TALIB_AVAILABLE:
            # Use talib for accuracy if available
            macd, macdsignal, macdhist = talib.MACD(
                df['close'].values, 
                fastperiod=fast, 
                slowperiod=slow, 
                signalperiod=signal
            )
            df['macd'] = macd
            df['macd_signal'] = macdsignal
            df['macd_hist'] = macdhist
        else:
            # Fallback to pandas implementation
            ema_fast = df['close'].ewm(span=fast, adjust=False).mean()
            ema_slow = df['close'].ewm(span=slow, adjust=False).mean()
            df['macd'] = ema_fast - ema_slow
            df['macd_signal'] = df['macd'].ewm(span=signal, adjust=False).mean()
            df['macd_hist'] = df['macd'] - df['macd_signal']
        
        # Add MACD crossover signal
        df['macd_cross'] = np.where(df['macd'] > df['macd_signal'], 1, -1)
    
    except Exception as e:
        print(f"Error calculating MACD: {str(e)}")
        # Add empty MACD columns to avoid errors
        df['macd'] = 0
        df['macd_signal'] = 0
        df['macd_hist'] = 0
        df['macd_cross'] = 0
    
    return df


def add_stochastic(df, k_period=14, d_period=3, slowing=3):
    """
    Add Stochastic Oscillator indicator
    
    Args:
        df: DataFrame with OHLCV data
        k_period: %K period
        d_period: %D period
        slowing: Slowing period
        
    Returns:
        DataFrame with Stochastic added
    """
    try:
        if TALIB_AVAILABLE:
            # Use talib for accuracy if available
            df['stoch_k'], df['stoch_d'] = talib.STOCH(
                df['high'].values,
                df['low'].values,
                df['close'].values,
                fastk_period=k_period,
                slowk_period=slowing,
                slowk_matype=0,
                slowd_period=d_period,
                slowd_matype=0
            )
        else:
            # Fallback to pandas implementation
            # Calculate %K
            low_min = df['low'].rolling(window=k_period).min()
            high_max = df['high'].rolling(window=k_period).max()
            df['stoch_k'] = 100 * ((df['close'] - low_min) / (high_max - low_min))
            
            # Apply slowing if specified
            if slowing > 1:
                df['stoch_k'] = df['stoch_k'].rolling(window=slowing).mean()
            
            # Calculate %D
            df['stoch_d'] = df['stoch_k'].rolling(window=d_period).mean()
        
        # Add Stochastic conditions
        df['stoch_overbought'] = df['stoch_k'] > 80
        df['stoch_oversold'] = df['stoch_k'] < 20
        df['stoch_cross'] = np.where(df['stoch_k'] > df['stoch_d'], 1, -1)
    
    except Exception as e:
        print(f"Error calculating Stochastic: {str(e)}")
        # Add empty Stochastic columns to avoid errors
        df['stoch_k'] = 50  # Neutral value
        df['stoch_d'] = 50  # Neutral value
        df['stoch_overbought'] = False
        df['stoch_oversold'] = False
        df['stoch_cross'] = 0
    
    return df


def add_cci(df, period=20):
    """
    Add Commodity Channel Index (CCI) indicator
    
    Args:
        df: DataFrame with OHLCV data
        period: CCI period
        
    Returns:
        DataFrame with CCI added
    """
    try:
        if TALIB_AVAILABLE:
            # Use talib for accuracy if available
            df['cci'] = talib.CCI(
                df['high'].values,
                df['low'].values,
                df['close'].values,
                timeperiod=period
            )
        else:
            # Fallback to pandas implementation
            # Calculate typical price
            df['tp'] = (df['high'] + df['low'] + df['close']) / 3
            
            # Calculate SMA of typical price
            sma_tp = df['tp'].rolling(window=period).mean()
            
            # Calculate Mean Deviation
            mean_dev = df['tp'].rolling(window=period).apply(lambda x: np.mean(np.abs(x - np.mean(x))))
            
            # Calculate CCI
            df['cci'] = (df['tp'] - sma_tp) / (0.015 * mean_dev)
            
            # Clean up
            df = df.drop(['tp'], axis=1)
        
        # Add CCI conditions
        df['cci_overbought'] = df['cci'] > 100
        df['cci_oversold'] = df['cci'] < -100
    
    except Exception as e:
        print(f"Error calculating CCI: {str(e)}")
        # Add empty CCI columns to avoid errors
        df['cci'] = 0
        df['cci_overbought'] = False
        df['cci_oversold'] = False
    
    return df


def add_williams_r(df, period=14):
    """
    Add Williams %R indicator
    
    Args:
        df: DataFrame with OHLCV data
        period: Look-back period
        
    Returns:
        DataFrame with Williams %R added
    """
    try:
        if TALIB_AVAILABLE:
            # Use talib for accuracy if available
            df['williams_r'] = talib.WILLR(
                df['high'].values,
                df['low'].values,
                df['close'].values,
                timeperiod=period
            )
        else:
            # Fallback to pandas implementation
            # Calculate highest high and lowest low
            highest_high = df['high'].rolling(window=period).max()
            lowest_low = df['low'].rolling(window=period).min()
            
            # Calculate Williams %R
            df['williams_r'] = -100 * (highest_high - df['close']) / (highest_high - lowest_low)
        
        # Add Williams %R conditions
        df['williams_r_overbought'] = df['williams_r'] > -20
        df['williams_r_oversold'] = df['williams_r'] < -80
    
    except Exception as e:
        print(f"Error calculating Williams %R: {str(e)}")
        # Add empty Williams %R columns to avoid errors
        df['williams_r'] = -50  # Neutral value
        df['williams_r_overbought'] = False
        df['williams_r_oversold'] = False
    
    return df


def add_momentum(df, period=14):
    """
    Add Momentum indicator
    
    Args:
        df: DataFrame with OHLCV data
        period: Look-back period
        
    Returns:
        DataFrame with Momentum added
    """
    try:
        # Calculate momentum
        df['momentum'] = df['close'] / df['close'].shift(period) * 100
        
        # Add momentum conditions
        df['momentum_up'] = df['momentum'] > 100
        df['momentum_down'] = df['momentum'] < 100
    
    except Exception as e:
        print(f"Error calculating Momentum: {str(e)}")
        # Add empty Momentum columns to avoid errors
        df['momentum'] = 100  # Neutral value
        df['momentum_up'] = False
        df['momentum_down'] = False
    
    return df