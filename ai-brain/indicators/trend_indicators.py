"""
Trend technical indicators module for SAMBOT trading system.
Includes ADX, Ichimoku Cloud, Supertrend, and other trend-based indicators.
"""

import numpy as np
import pandas as pd

try:
    import talib
    TALIB_AVAILABLE = True
except ImportError:
    TALIB_AVAILABLE = False


def add_adx(df, period=14):
    """
    Add Average Directional Index (ADX) indicator
    
    Args:
        df: DataFrame with OHLCV data
        period: ADX period
        
    Returns:
        DataFrame with ADX added
    """
    try:
        if TALIB_AVAILABLE:
            # Use talib for accuracy if available
            df['adx'] = talib.ADX(df['high'].values, df['low'].values, df['close'].values, timeperiod=period)
            df['plus_di'] = talib.PLUS_DI(df['high'].values, df['low'].values, df['close'].values, timeperiod=period)
            df['minus_di'] = talib.MINUS_DI(df['high'].values, df['low'].values, df['close'].values, timeperiod=period)
        else:
            # Fallback to simplified ADX calculation (true calculation is complex)
            # First, calculate +DM, -DM, and TR
            high_diff = df['high'].diff()
            low_diff = df['low'].diff()
            
            plus_dm = high_diff.copy()
            plus_dm[plus_dm < 0] = 0
            plus_dm[(high_diff < 0) | (high_diff < low_diff)] = 0
            
            minus_dm = low_diff.abs().copy()
            minus_dm[minus_dm < 0] = 0
            minus_dm[(low_diff > 0) | (high_diff > low_diff.abs())] = 0
            
            # Calculate True Range
            tr1 = df['high'] - df['low']
            tr2 = (df['high'] - df['close'].shift(1)).abs()
            tr3 = (df['low'] - df['close'].shift(1)).abs()
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            
            # Smooth with EMA
            plus_di = 100 * (plus_dm.ewm(alpha=1/period, adjust=False).mean() / tr.ewm(alpha=1/period, adjust=False).mean())
            minus_di = 100 * (minus_dm.ewm(alpha=1/period, adjust=False).mean() / tr.ewm(alpha=1/period, adjust=False).mean())
            
            # Calculate DX and ADX
            dx = 100 * ((plus_di - minus_di).abs() / (plus_di + minus_di))
            df['adx'] = dx.ewm(alpha=1/period, adjust=False).mean()
            df['plus_di'] = plus_di
            df['minus_di'] = minus_di
        
        # Add ADX trend strength
        df['adx_trend_strength'] = pd.cut(
            df['adx'],
            bins=[0, 20, 40, 60, 100],
            labels=['Weak', 'Moderate', 'Strong', 'Very Strong']
        )
        
        # Add DI crossover signal
        df['di_cross'] = np.where(df['plus_di'] > df['minus_di'], 1, -1)
    
    except Exception as e:
        print(f"Error calculating ADX: {str(e)}")
        # Add empty ADX columns to avoid errors
        df['adx'] = 25  # Neutral value
        df['plus_di'] = 20
        df['minus_di'] = 20
        df['di_cross'] = 0
    
    return df


def add_supertrend(df, period=10, multiplier=3):
    """
    Add Supertrend indicator
    
    Args:
        df: DataFrame with OHLCV data
        period: ATR period
        multiplier: Factor for ATR
        
    Returns:
        DataFrame with Supertrend added
    """
    try:
        # Calculate ATR if not already done
        if 'atr' not in df.columns:
            # Calculate True Range
            tr1 = df['high'] - df['low']
            tr2 = (df['high'] - df['close'].shift(1)).abs()
            tr3 = (df['low'] - df['close'].shift(1)).abs()
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            
            # Average True Range
            df['atr'] = tr.rolling(period).mean()
        
        # Calculate basic upper and lower bands
        df['basic_upper'] = ((df['high'] + df['low']) / 2) + (multiplier * df['atr'])
        df['basic_lower'] = ((df['high'] + df['low']) / 2) - (multiplier * df['atr'])
        
        # Initialize Supertrend columns
        df['supertrend'] = 0.0
        df['supertrend_direction'] = 0
        
        # Calculate Supertrend for first row
        if len(df) > 0:
            df.loc[df.index[0], 'supertrend'] = df.loc[df.index[0], 'basic_lower']
            df.loc[df.index[0], 'supertrend_direction'] = 1
        
        # Calculate Supertrend for remaining rows
        for i in range(1, len(df)):
            curr_close = df.loc[df.index[i], 'close']
            prev_supertrend = df.loc[df.index[i-1], 'supertrend']
            curr_basic_upper = df.loc[df.index[i], 'basic_upper']
            curr_basic_lower = df.loc[df.index[i], 'basic_lower']
            prev_direction = df.loc[df.index[i-1], 'supertrend_direction']
            
            if prev_supertrend <= curr_basic_upper and prev_direction == 1:
                df.loc[df.index[i], 'supertrend'] = curr_basic_lower
                df.loc[df.index[i], 'supertrend_direction'] = 1
            elif prev_supertrend >= curr_basic_lower and prev_direction == -1:
                df.loc[df.index[i], 'supertrend'] = curr_basic_upper
                df.loc[df.index[i], 'supertrend_direction'] = -1
            elif curr_close <= prev_supertrend and prev_direction == 1:
                df.loc[df.index[i], 'supertrend'] = curr_basic_upper
                df.loc[df.index[i], 'supertrend_direction'] = -1
            elif curr_close >= prev_supertrend and prev_direction == -1:
                df.loc[df.index[i], 'supertrend'] = curr_basic_lower
                df.loc[df.index[i], 'supertrend_direction'] = 1
        
        # Clean up temporary columns
        df = df.drop(['basic_upper', 'basic_lower'], axis=1)
    
    except Exception as e:
        print(f"Error calculating Supertrend: {str(e)}")
        # Add empty Supertrend columns to avoid errors
        df['supertrend'] = df['close']
        df['supertrend_direction'] = 0
    
    return df


def add_ichimoku(df):
    """
    Add Ichimoku Cloud indicator
    
    Args:
        df: DataFrame with OHLCV data
        
    Returns:
        DataFrame with Ichimoku Cloud added
    """
    try:
        # Calculate Tenkan-sen (Conversion Line)
        high_9 = df['high'].rolling(window=9).max()
        low_9 = df['low'].rolling(window=9).min()
        df['tenkan_sen'] = (high_9 + low_9) / 2
        
        # Calculate Kijun-sen (Base Line)
        high_26 = df['high'].rolling(window=26).max()
        low_26 = df['low'].rolling(window=26).min()
        df['kijun_sen'] = (high_26 + low_26) / 2
        
        # Calculate Senkou Span A (Leading Span A)
        df['senkou_span_a'] = ((df['tenkan_sen'] + df['kijun_sen']) / 2).shift(26)
        
        # Calculate Senkou Span B (Leading Span B)
        high_52 = df['high'].rolling(window=52).max()
        low_52 = df['low'].rolling(window=52).min()
        df['senkou_span_b'] = ((high_52 + low_52) / 2).shift(26)
        
        # Calculate Chikou Span (Lagging Span)
        df['chikou_span'] = df['close'].shift(-26)
        
        # Add cloud direction
        df['cloud_direction'] = np.where(df['senkou_span_a'] > df['senkou_span_b'], 1, -1)
        
        # Add price relative to cloud
        df['price_above_cloud'] = df['close'] > df['senkou_span_a']
        df['price_below_cloud'] = df['close'] < df['senkou_span_b']
        df['price_in_cloud'] = ~(df['price_above_cloud'] | df['price_below_cloud'])
    
    except Exception as e:
        print(f"Error calculating Ichimoku: {str(e)}")
        # Add empty Ichimoku columns to avoid errors
        df['tenkan_sen'] = df['close']
        df['kijun_sen'] = df['close']
        df['senkou_span_a'] = df['close']
        df['senkou_span_b'] = df['close']
        df['chikou_span'] = df['close']
        df['cloud_direction'] = 0
        df['price_above_cloud'] = False
        df['price_below_cloud'] = False
        df['price_in_cloud'] = True
    
    return df


def add_parabolic_sar(df, acceleration=0.02, maximum=0.2):
    """
    Add Parabolic SAR indicator
    
    Args:
        df: DataFrame with OHLCV data
        acceleration: Start acceleration factor
        maximum: Maximum acceleration factor
        
    Returns:
        DataFrame with Parabolic SAR added
    """
    try:
        if TALIB_AVAILABLE:
            # Use talib for accuracy if available
            df['psar'] = talib.SAR(df['high'].values, df['low'].values, acceleration, maximum)
        else:
            # Parabolic SAR calculation is complex
            # This is a placeholder for fallback logic
            df['psar'] = df['close']
        
        # Add price vs. PSAR relationship
        df['psar_signal'] = np.where(df['close'] > df['psar'], 1, -1)
    
    except Exception as e:
        print(f"Error calculating Parabolic SAR: {str(e)}")
        # Add empty PSAR columns to avoid errors
        df['psar'] = df['close']
        df['psar_signal'] = 0
    
    return df


def add_aroon(df, period=25):
    """
    Add Aroon indicators
    
    Args:
        df: DataFrame with OHLCV data
        period: Aroon period
        
    Returns:
        DataFrame with Aroon indicators added
    """
    try:
        if TALIB_AVAILABLE:
            # Use talib for accuracy if available
            df['aroon_up'], df['aroon_down'] = talib.AROON(df['high'].values, df['low'].values, timeperiod=period)
        else:
            # Calculate days since highest high in the period
            df['aroon_up'] = df['high'].rolling(period + 1).apply(
                lambda x: float(period - x.argmax()) / period * 100,
                raw=True
            )
            
            # Calculate days since lowest low in the period
            df['aroon_down'] = df['low'].rolling(period + 1).apply(
                lambda x: float(period - x.argmin()) / period * 100,
                raw=True
            )
        
        # Calculate Aroon Oscillator
        df['aroon_osc'] = df['aroon_up'] - df['aroon_down']
        
        # Add Aroon signals
        df['aroon_bull'] = (df['aroon_up'] > 70) & (df['aroon_down'] < 30)
        df['aroon_bear'] = (df['aroon_down'] > 70) & (df['aroon_up'] < 30)
    
    except Exception as e:
        print(f"Error calculating Aroon: {str(e)}")
        # Add empty Aroon columns to avoid errors
        df['aroon_up'] = 50
        df['aroon_down'] = 50
        df['aroon_osc'] = 0
        df['aroon_bull'] = False
        df['aroon_bear'] = False
    
    return df


def add_dmi_atr(df, period=14):
    """
    Add Directional Movement Index (DMI) and Average True Range (ATR)
    
    Args:
        df: DataFrame with OHLCV data
        period: DMI period
        
    Returns:
        DataFrame with DMI and ATR added
    """
    # This is a separate implementation focusing on DMI and ATR together
    try:
        # Calculate True Range
        df['tr1'] = df['high'] - df['low']
        df['tr2'] = abs(df['high'] - df['close'].shift())
        df['tr3'] = abs(df['low'] - df['close'].shift())
        df['tr'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)
        
        # Calculate ATR
        df['atr'] = df['tr'].rolling(window=period).mean()
        
        # Calculate +DM and -DM
        df['up_move'] = df['high'] - df['high'].shift()
        df['down_move'] = df['low'].shift() - df['low']
        
        df['plus_dm'] = np.where(
            (df['up_move'] > df['down_move']) & (df['up_move'] > 0),
            df['up_move'],
            0
        )
        
        df['minus_dm'] = np.where(
            (df['down_move'] > df['up_move']) & (df['down_move'] > 0),
            df['down_move'],
            0
        )
        
        # Calculate smoothed +DM and -DM
        df['plus_dm_smooth'] = df['plus_dm'].rolling(window=period).mean()
        df['minus_dm_smooth'] = df['minus_dm'].rolling(window=period).mean()
        
        # Calculate +DI and -DI
        df['plus_di'] = 100 * df['plus_dm_smooth'] / df['atr']
        df['minus_di'] = 100 * df['minus_dm_smooth'] / df['atr']
        
        # Calculate DX
        df['dx'] = 100 * abs(df['plus_di'] - df['minus_di']) / (df['plus_di'] + df['minus_di'])
        
        # Calculate ADX
        df['adx'] = df['dx'].rolling(window=period).mean()
        
        # Clean up intermediate columns
        df = df.drop(['tr1', 'tr2', 'tr3', 'tr', 'up_move', 'down_move', 'plus_dm', 'minus_dm', 
                     'plus_dm_smooth', 'minus_dm_smooth', 'dx'], axis=1)
        
    except Exception as e:
        print(f"Error calculating DMI/ATR: {str(e)}")
        # Add empty columns to avoid errors
        df['atr'] = df['high'] - df['low']  # Simple approximation
        df['plus_di'] = 25
        df['minus_di'] = 25
        df['adx'] = 25
    
    return df