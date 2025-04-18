"""
Basic technical indicators module for SAMBOT trading system.
Includes simple moving averages, exponential moving averages, and related calculations.
"""

import numpy as np
import pandas as pd


def add_moving_averages(df):
    """
    Add various moving averages to the dataframe
    
    Args:
        df: DataFrame with OHLCV data
        
    Returns:
        DataFrame with moving averages added
    """
    # Simple Moving Averages
    df['sma_9'] = df['close'].rolling(window=9).mean()
    df['sma_20'] = df['close'].rolling(window=20).mean()
    df['sma_50'] = df['close'].rolling(window=50).mean()
    df['sma_200'] = df['close'].rolling(window=200).mean()
    
    # Exponential Moving Averages
    df['ema_9'] = df['close'].ewm(span=9, adjust=False).mean()
    df['ema_20'] = df['close'].ewm(span=20, adjust=False).mean()
    df['ema_50'] = df['close'].ewm(span=50, adjust=False).mean()
    df['ema_200'] = df['close'].ewm(span=200, adjust=False).mean()
    
    # Moving Average Crossover signals
    df['ma_cross_9_20'] = np.where(df['ema_9'] > df['ema_20'], 1, -1)
    
    # Price relative to moving averages
    df['price_to_sma_20'] = df['close'] / df['sma_20']
    df['price_to_sma_50'] = df['close'] / df['sma_50']
    
    return df


def add_hull_moving_average(df, period=9):
    """
    Add Hull Moving Average (HMA) to the dataframe.
    HMA is a faster and smoother moving average
    
    Args:
        df: DataFrame with OHLCV data
        period: HMA period
        
    Returns:
        DataFrame with HMA added
    """
    # Calculate the HMA
    half_period = int(period / 2)
    sqrt_period = int(np.sqrt(period))
    
    # Step 1: Calculate the WMA with period/2
    df['wma_half'] = df['close'].rolling(window=half_period).apply(
        lambda x: np.sum(x * np.arange(1, half_period + 1)) / np.sum(np.arange(1, half_period + 1))
    )
    
    # Step 2: Calculate the WMA with period
    df['wma_full'] = df['close'].rolling(window=period).apply(
        lambda x: np.sum(x * np.arange(1, period + 1)) / np.sum(np.arange(1, period + 1))
    )
    
    # Step 3: Calculate 2 * WMA(half period) - WMA(full period)
    df['hma_raw'] = 2 * df['wma_half'] - df['wma_full']
    
    # Step 4: Calculate WMA of hma_raw with sqrt(period)
    df[f'hma_{period}'] = df['hma_raw'].rolling(window=sqrt_period).apply(
        lambda x: np.sum(x * np.arange(1, sqrt_period + 1)) / np.sum(np.arange(1, sqrt_period + 1))
    )
    
    # Clean up intermediate columns
    df = df.drop(['wma_half', 'wma_full', 'hma_raw'], axis=1)
    
    return df


def add_keltner_channel(df, period=20, atr_multiplier=2):
    """
    Add Keltner Channel to the dataframe
    
    Args:
        df: DataFrame with OHLCV data
        period: EMA period for middle line
        atr_multiplier: Multiplier for ATR
        
    Returns:
        DataFrame with Keltner Channel added
    """
    # Calculate middle line (EMA)
    df['kc_middle'] = df['close'].ewm(span=period, adjust=False).mean()
    
    # Calculate ATR if not already present
    if 'atr' not in df.columns:
        # True Range
        df['tr1'] = df['high'] - df['low']
        df['tr2'] = abs(df['high'] - df['close'].shift())
        df['tr3'] = abs(df['low'] - df['close'].shift())
        df['tr'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)
        
        # Average True Range
        df['atr'] = df['tr'].rolling(window=period).mean()
        
        # Clean up intermediate columns
        df = df.drop(['tr1', 'tr2', 'tr3', 'tr'], axis=1)
    
    # Calculate upper and lower bands
    df['kc_upper'] = df['kc_middle'] + (df['atr'] * atr_multiplier)
    df['kc_lower'] = df['kc_middle'] - (df['atr'] * atr_multiplier)
    
    return df


def add_pivots(df, method='traditional'):
    """
    Add pivot points to the dataframe (for intraday timeframes)
    
    Args:
        df: DataFrame with OHLCV data
        method: Pivot calculation method ('traditional', 'fibonacci', 'camarilla')
        
    Returns:
        DataFrame with pivot points added
    """
    # Get previous day's OHLC
    prev_high = df['high'].shift(1)
    prev_low = df['low'].shift(1)
    prev_close = df['close'].shift(1)
    
    # Calculate traditional pivot points
    df['pivot'] = (prev_high + prev_low + prev_close) / 3
    
    if method == 'traditional':
        df['r1'] = (2 * df['pivot']) - prev_low
        df['s1'] = (2 * df['pivot']) - prev_high
        df['r2'] = df['pivot'] + (prev_high - prev_low)
        df['s2'] = df['pivot'] - (prev_high - prev_low)
        df['r3'] = df['pivot'] + 2 * (prev_high - prev_low)
        df['s3'] = df['pivot'] - 2 * (prev_high - prev_low)
    
    elif method == 'fibonacci':
        df['r1'] = df['pivot'] + 0.382 * (prev_high - prev_low)
        df['s1'] = df['pivot'] - 0.382 * (prev_high - prev_low)
        df['r2'] = df['pivot'] + 0.618 * (prev_high - prev_low)
        df['s2'] = df['pivot'] - 0.618 * (prev_high - prev_low)
        df['r3'] = df['pivot'] + 1.0 * (prev_high - prev_low)
        df['s3'] = df['pivot'] - 1.0 * (prev_high - prev_low)
    
    elif method == 'camarilla':
        df['r1'] = prev_close + 1.1 * (prev_high - prev_low) / 12
        df['s1'] = prev_close - 1.1 * (prev_high - prev_low) / 12
        df['r2'] = prev_close + 1.1 * (prev_high - prev_low) / 6
        df['s2'] = prev_close - 1.1 * (prev_high - prev_low) / 6
        df['r3'] = prev_close + 1.1 * (prev_high - prev_low) / 4
        df['s3'] = prev_close - 1.1 * (prev_high - prev_low) / 4
    
    return df