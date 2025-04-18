"""
Volatility technical indicators module for SAMBOT trading system.
Includes Bollinger Bands, ATR, and other volatility-based indicators.
"""

import numpy as np
import pandas as pd

try:
    import talib
    TALIB_AVAILABLE = True
except ImportError:
    TALIB_AVAILABLE = False


def add_bollinger_bands(df, period=20, std_dev=2):
    """
    Add Bollinger Bands indicator
    
    Args:
        df: DataFrame with OHLCV data
        period: Moving average period
        std_dev: Number of standard deviations
        
    Returns:
        DataFrame with Bollinger Bands added
    """
    try:
        if TALIB_AVAILABLE:
            # Use talib for accuracy if available
            df['bb_upper'], df['bb_middle'], df['bb_lower'] = talib.BBANDS(
                df['close'].values,
                timeperiod=period,
                nbdevup=std_dev,
                nbdevdn=std_dev
            )
        else:
            # Fallback to pandas implementation
            df['bb_middle'] = df['close'].rolling(window=period).mean()
            std = df['close'].rolling(window=period).std()
            df['bb_upper'] = df['bb_middle'] + (std * std_dev)
            df['bb_lower'] = df['bb_middle'] - (std * std_dev)
        
        # Add Bollinger Band width and %B
        df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
        df['bb_pct_b'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
        
        # Add Bollinger Band conditions
        df['bb_above_upper'] = df['close'] > df['bb_upper']
        df['bb_below_lower'] = df['close'] < df['bb_lower']
        df['bb_squeeze'] = df['bb_width'] < df['bb_width'].rolling(window=50).quantile(0.2)
    
    except Exception as e:
        print(f"Error calculating Bollinger Bands: {str(e)}")
        # Add empty Bollinger Bands columns to avoid errors
        df['bb_upper'] = df['close'] * 1.1
        df['bb_middle'] = df['close']
        df['bb_lower'] = df['close'] * 0.9
        df['bb_width'] = 0.2
        df['bb_pct_b'] = 0.5
        df['bb_above_upper'] = False
        df['bb_below_lower'] = False
        df['bb_squeeze'] = False
    
    return df


def add_atr(df, period=14):
    """
    Add Average True Range (ATR) indicator
    
    Args:
        df: DataFrame with OHLCV data
        period: ATR period
        
    Returns:
        DataFrame with ATR added
    """
    try:
        if TALIB_AVAILABLE:
            # Use talib for accuracy if available
            df['atr'] = talib.ATR(df['high'].values, df['low'].values, df['close'].values, timeperiod=period)
        else:
            # Calculate ATR manually
            # True Range
            df['tr1'] = df['high'] - df['low']
            df['tr2'] = abs(df['high'] - df['close'].shift())
            df['tr3'] = abs(df['low'] - df['close'].shift())
            df['tr'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)
            
            # Average True Range
            df['atr'] = df['tr'].rolling(period).mean()
            
            # Clean up
            df = df.drop(['tr1', 'tr2', 'tr3', 'tr'], axis=1)
        
        # Add ATR percent of price
        df['atr_percent'] = (df['atr'] / df['close']) * 100
        
        # Add volatility classification
        # Classify volatility based on ATR%
        df['volatility'] = pd.cut(
            df['atr_percent'],
            bins=[0, 0.5, 1.0, 1.5, 10],
            labels=['Low', 'Normal', 'High', 'Extreme']
        )
    
    except Exception as e:
        print(f"Error calculating ATR: {str(e)}")
        # Add empty ATR columns to avoid errors
        df['atr'] = (df['high'] - df['low']).rolling(period).mean()  # Simple approximation
        df['atr_percent'] = df['atr'] / df['close'] * 100
        df['volatility'] = 'Normal'
    
    return df


def add_keltner_channels(df, period=20, atr_multiplier=2):
    """
    Add Keltner Channels indicator
    
    Args:
        df: DataFrame with OHLCV data
        period: Moving average period
        atr_multiplier: Multiplier for ATR
        
    Returns:
        DataFrame with Keltner Channels added
    """
    try:
        # Calculate ATR if not already done
        if 'atr' not in df.columns:
            df = add_atr(df, period)
        
        # Calculate middle line (EMA of typical price)
        df['keltner_middle'] = df['close'].ewm(span=period, adjust=False).mean()
        
        # Calculate upper and lower bands
        df['keltner_upper'] = df['keltner_middle'] + (df['atr'] * atr_multiplier)
        df['keltner_lower'] = df['keltner_middle'] - (df['atr'] * atr_multiplier)
        
        # Add conditions
        df['keltner_above_upper'] = df['close'] > df['keltner_upper']
        df['keltner_below_lower'] = df['close'] < df['keltner_lower']
    
    except Exception as e:
        print(f"Error calculating Keltner Channels: {str(e)}")
        # Add empty Keltner Channels columns to avoid errors
        df['keltner_middle'] = df['close']
        df['keltner_upper'] = df['close'] * 1.1
        df['keltner_lower'] = df['close'] * 0.9
        df['keltner_above_upper'] = False
        df['keltner_below_lower'] = False
    
    return df


def add_donchian_channels(df, period=20):
    """
    Add Donchian Channels indicator
    
    Args:
        df: DataFrame with OHLCV data
        period: Look-back period
        
    Returns:
        DataFrame with Donchian Channels added
    """
    try:
        # Calculate upper and lower bands
        df['donchian_upper'] = df['high'].rolling(window=period).max()
        df['donchian_lower'] = df['low'].rolling(window=period).min()
        df['donchian_middle'] = (df['donchian_upper'] + df['donchian_lower']) / 2
        
        # Add conditions
        df['donchian_breakout_up'] = df['close'] > df['donchian_upper'].shift()
        df['donchian_breakout_down'] = df['close'] < df['donchian_lower'].shift()
    
    except Exception as e:
        print(f"Error calculating Donchian Channels: {str(e)}")
        # Add empty Donchian Channels columns to avoid errors
        df['donchian_upper'] = df['high'].rolling(window=3).max()
        df['donchian_lower'] = df['low'].rolling(window=3).min()
        df['donchian_middle'] = (df['donchian_upper'] + df['donchian_lower']) / 2
        df['donchian_breakout_up'] = False
        df['donchian_breakout_down'] = False
    
    return df


def add_volatility_ratio(df, short_period=5, long_period=20):
    """
    Add Volatility Ratio indicator to identify volatility expansion/contraction
    
    Args:
        df: DataFrame with OHLCV data
        short_period: Short look-back period
        long_period: Long look-back period
        
    Returns:
        DataFrame with Volatility Ratio added
    """
    try:
        # Calculate short-term ATR
        tr1 = df['high'] - df['low']
        tr2 = abs(df['high'] - df['close'].shift())
        tr3 = abs(df['low'] - df['close'].shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        short_atr = tr.rolling(window=short_period).mean()
        long_atr = tr.rolling(window=long_period).mean()
        
        # Calculate volatility ratio
        df['volatility_ratio'] = short_atr / long_atr
        
        # Add volatility conditions
        df['volatility_expansion'] = df['volatility_ratio'] > 1.2
        df['volatility_contraction'] = df['volatility_ratio'] < 0.8
    
    except Exception as e:
        print(f"Error calculating Volatility Ratio: {str(e)}")
        # Add empty Volatility Ratio columns to avoid errors
        df['volatility_ratio'] = 1.0
        df['volatility_expansion'] = False
        df['volatility_contraction'] = False
    
    return df


def add_historical_volatility(df, period=20, annualization=252):
    """
    Add Historical Volatility (standard deviation of daily returns)
    
    Args:
        df: DataFrame with OHLCV data
        period: Look-back period
        annualization: Number of trading days in a year
        
    Returns:
        DataFrame with Historical Volatility added
    """
    try:
        # Calculate daily log returns
        df['daily_return'] = np.log(df['close'] / df['close'].shift(1))
        
        # Calculate historical volatility
        df['hist_volatility'] = df['daily_return'].rolling(window=period).std() * np.sqrt(annualization) * 100
        
        # Add volatility bands
        mean_vol = df['hist_volatility'].mean()
        std_vol = df['hist_volatility'].std()
        
        df['volatility_high'] = df['hist_volatility'] > (mean_vol + std_vol)
        df['volatility_low'] = df['hist_volatility'] < (mean_vol - std_vol)
        
        # Clean up
        df = df.drop(['daily_return'], axis=1)
    
    except Exception as e:
        print(f"Error calculating Historical Volatility: {str(e)}")
        # Add empty Historical Volatility columns to avoid errors
        df['hist_volatility'] = 20  # Common market volatility value
        df['volatility_high'] = False
        df['volatility_low'] = False
    
    return df


def add_bollinger_bandwidth(df, period=20, std_dev=2):
    """
    Add Bollinger Bandwidth (a pure volatility indicator)
    
    Args:
        df: DataFrame with OHLCV data
        period: Moving average period
        std_dev: Number of standard deviations
        
    Returns:
        DataFrame with Bollinger Bandwidth added
    """
    try:
        # Calculate Bollinger Bands if not already done
        if 'bb_upper' not in df.columns:
            df = add_bollinger_bands(df, period, std_dev)
        
        # Calculate Bollinger Bandwidth
        df['bb_bandwidth'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
        
        # Calculate Bandwidth Percentile (0-100%)
        df['bb_bandwidth_percentile'] = df['bb_bandwidth'].rolling(window=252).apply(
            lambda x: pd.Series(x).rank(pct=True).iloc[-1] * 100,
            raw=True
        )
        
        # Add Bollinger Squeeze condition (low bandwidth)
        df['bb_squeeze'] = df['bb_bandwidth'] < df['bb_bandwidth'].rolling(window=50).quantile(0.2)
    
    except Exception as e:
        print(f"Error calculating Bollinger Bandwidth: {str(e)}")
        # Add empty Bollinger Bandwidth columns to avoid errors
        df['bb_bandwidth'] = 0.05
        df['bb_bandwidth_percentile'] = 50
        df['bb_squeeze'] = False
    
    return df