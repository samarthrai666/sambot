"""
Technical indicators module for SAMBOT trading system.
This package contains various technical indicators used for market analysis.
"""

from .basic_indicators import add_moving_averages
from .momentum_indicators import add_rsi, add_macd, add_stochastic
from .trend_indicators import add_adx, add_ichimoku, add_supertrend
from .volatility_indicators import add_bollinger_bands, add_atr
from .volume_indicators import add_vwap, add_obv
from .utils import get_trend_strength, get_indicator_signals

def add_technical_indicators(df, include_all=False):
    """
    Add common technical indicators to a dataframe with OHLCV data
    
    Args:
        df: DataFrame with 'open', 'high', 'low', 'close', 'volume' columns
        include_all: Whether to include all indicators or just core ones
        
    Returns:
        DataFrame with indicators added
    """
    # Make a copy to avoid modifying the original
    df = df.copy()
    
    # Ensure the dataframe is sorted by timestamp
    if 'timestamp' in df.columns:
        df = df.sort_values('timestamp')
    
    # Core indicators
    add_moving_averages(df)
    add_rsi(df)
    add_macd(df)
    add_bollinger_bands(df)
    add_vwap(df)
    
    # Additional indicators
    if include_all:
        add_stochastic(df)
        add_adx(df)
        add_atr(df)
        add_supertrend(df)
        add_ichimoku(df)
        add_obv(df)
    
    # Fill NaN values for calculations at the beginning of the series
    df = df.fillna(0)
    
    return df

__all__ = [
    'add_technical_indicators',
    'add_moving_averages',
    'add_rsi',
    'add_macd',
    'add_stochastic',
    'add_bollinger_bands',
    'add_atr',
    'add_vwap',
    'add_obv',
    'add_adx',
    'add_ichimoku',
    'add_supertrend',
    'get_trend_strength',
    'get_indicator_signals'
]