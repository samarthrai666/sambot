"""
Volume technical indicators module for SAMBOT trading system, optimized for Indian stock market.
Includes VWAP, OBV, and other volume-based indicators with specific adjustments for NSE and BSE.
"""

import numpy as np
import pandas as pd
from datetime import datetime, time

try:
    import talib
    TALIB_AVAILABLE = True
except ImportError:
    TALIB_AVAILABLE = False


def add_vwap(df, reset_period=None):
    """
    Add Volume Weighted Average Price (VWAP) indicator
    Indian market specifics: Resets at daily market open (9:15 AM IST)
    
    Args:
        df: DataFrame with OHLCV data
        reset_period: Reset VWAP calculation (None=Intraday, 'D'=Daily, 'W'=Weekly)
        
    Returns:
        DataFrame with VWAP added
    """
    try:
        # Calculate typical price
        df['typical_price'] = (df['high'] + df['low'] + df['close']) / 3
        
        if reset_period and 'timestamp' in df.columns:
            # Convert timestamp to datetime if needed
            if not pd.api.types.is_datetime64_dtype(df['timestamp']):
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Group by the reset period - adjusted for Indian market hours
            if reset_period == 'D':
                # For Indian market, day starts at 9:15 AM
                df['period'] = df['timestamp'].dt.date
            elif reset_period == 'W':
                # Indian market week (Monday to Friday)
                df['period'] = df['timestamp'].dt.isocalendar().week
            else:
                df['period'] = df['timestamp'].dt.strftime(f'%Y-%m-{reset_period}')
            
            # Calculate VWAP for each period
            df['cumulative_tp_vol'] = df.groupby('period').apply(
                lambda x: (x['typical_price'] * x['volume']).cumsum()
            ).reset_index(level=0, drop=True)
            
            df['cumulative_vol'] = df.groupby('period')['volume'].cumsum()
            
            df['vwap'] = df['cumulative_tp_vol'] / df['cumulative_vol']
            
            # Clean up intermediate columns
            df = df.drop(['period', 'cumulative_tp_vol', 'cumulative_vol'], axis=1)
            
        else:
            # For intraday calculation (no reset)
            df['cumulative_tp_vol'] = (df['typical_price'] * df['volume']).cumsum()
            df['cumulative_vol'] = df['volume'].cumsum()
            df['vwap'] = df['cumulative_tp_vol'] / df['cumulative_vol']
            
            # Clean up intermediate columns
            df = df.drop(['cumulative_tp_vol', 'cumulative_vol'], axis=1)
        
        # Add price relative to VWAP
        df['price_to_vwap'] = df['close'] / df['vwap']
        df['price_above_vwap'] = df['close'] > df['vwap']
        
        # Clean up typical price
        df = df.drop(['typical_price'], axis=1)
    
    except Exception as e:
        print(f"Error calculating VWAP: {str(e)}")
        # Add empty VWAP columns to avoid errors
        df['vwap'] = df['close'].copy()
        df['price_to_vwap'] = 1.0
        df['price_above_vwap'] = True
    
    return df


def add_obv(df):
    """
    Add On-Balance Volume (OBV) indicator
    
    Args:
        df: DataFrame with OHLCV data
        
    Returns:
        DataFrame with OBV added
    """
    try:
        if TALIB_AVAILABLE:
            # Use talib for accuracy if available
            df['obv'] = talib.OBV(df['close'].values, df['volume'].values)
        else:
            # Calculate OBV manually
            df['obv'] = 0
            df.loc[0, 'obv'] = df.loc[0, 'volume']
            
            for i in range(1, len(df)):
                if df.loc[i, 'close'] > df.loc[i-1, 'close']:
                    df.loc[i, 'obv'] = df.loc[i-1, 'obv'] + df.loc[i, 'volume']
                elif df.loc[i, 'close'] < df.loc[i-1, 'close']:
                    df.loc[i, 'obv'] = df.loc[i-1, 'obv'] - df.loc[i, 'volume']
                else:
                    df.loc[i, 'obv'] = df.loc[i-1, 'obv']
        
        # Add OBV moving average for divergence detection
        df['obv_ema'] = df['obv'].ewm(span=20, adjust=False).mean()
        
        # Add OBV Divergence
        df['price_uptrend'] = df['close'] > df['close'].shift(1)
        df['obv_uptrend'] = df['obv'] > df['obv'].shift(1)
        
        df['obv_bullish_div'] = (~df['price_uptrend']) & df['obv_uptrend']
        df['obv_bearish_div'] = df['price_uptrend'] & (~df['obv_uptrend'])
        
        # Clean up
        df = df.drop(['price_uptrend', 'obv_uptrend'], axis=1)
    
    except Exception as e:
        print(f"Error calculating OBV: {str(e)}")
        # Add empty OBV columns to avoid errors
        df['obv'] = df['volume'].cumsum()
        df['obv_ema'] = df['obv']
        df['obv_bullish_div'] = False
        df['obv_bearish_div'] = False
    
    return df


def add_volume_profile(df, zones=10):
    """
    Add Volume Profile analysis
    Identifies high-volume price levels that can act as support/resistance
    
    Args:
        df: DataFrame with OHLCV data
        zones: Number of price zones to analyze
        
    Returns:
        DataFrame with Volume Profile analysis added
    """
    try:
        # Determine price range
        price_min = df['low'].min()
        price_max = df['high'].max()
        zone_size = (price_max - price_min) / zones
        
        # Create price zones
        df['price_zone'] = ((df['close'] - price_min) / zone_size).astype(int)
        df['price_zone'] = df['price_zone'].clip(upper=zones-1)  # Ensure within bounds
        
        # Calculate volume per zone
        volume_by_zone = df.groupby('price_zone')['volume'].sum()
        
        # Find high volume zones (potential support/resistance)
        high_vol_zones = volume_by_zone.nlargest(3).index.tolist()
        
        # Calculate zone prices
        zone_prices = [price_min + (z + 0.5) * zone_size for z in high_vol_zones]
        
        # Add columns for closest high-volume zones
        df['vol_profile_sr1'] = zone_prices[0] if len(zone_prices) > 0 else price_min
        df['vol_profile_sr2'] = zone_prices[1] if len(zone_prices) > 1 else price_max
        df['vol_profile_sr3'] = zone_prices[2] if len(zone_prices) > 2 else (price_min + price_max) / 2
        
        # Clean up
        df = df.drop(['price_zone'], axis=1)
    
    except Exception as e:
        print(f"Error calculating Volume Profile: {str(e)}")
        # Add empty Volume Profile columns to avoid errors
        price_mid = (df['high'].max() + df['low'].min()) / 2
        df['vol_profile_sr1'] = price_mid * 0.95
        df['vol_profile_sr2'] = price_mid
        df['vol_profile_sr3'] = price_mid * 1.05
    
    return df


def add_volume_indicators(df):
    """
    Add multiple volume indicators at once
    
    Args:
        df: DataFrame with OHLCV data
        
    Returns:
        DataFrame with multiple volume indicators added
    """
    # Add VWAP - Indian market intraday
    df = add_vwap(df, reset_period='D')
    
    # Add OBV
    df = add_obv(df)
    
    # Add Volume Profile
    df = add_volume_profile(df)
    
    # Add Volume SMA for relative volume
    df['volume_sma_5'] = df['volume'].rolling(window=5).mean()
    df['volume_sma_20'] = df['volume'].rolling(window=20).mean()
    
    # Add Relative Volume (current volume compared to average)
    df['relative_volume'] = df['volume'] / df['volume_sma_20']
    
    # Add Volume Spike detection
    df['volume_spike'] = df['volume'] > (df['volume_sma_20'] * 2)
    
    # Add Ultra-high volume detection (3x average) - important for Indian markets
    df['ultra_high_volume'] = df['volume'] > (df['volume_sma_20'] * 3)
    
    # Add Price-Volume Trend (PVT)
    df['pvt'] = ((df['close'] - df['close'].shift(1)) / df['close'].shift(1)) * df['volume']
    df['pvt'] = df['pvt'].cumsum()
    
    # Add Money Flow Index (MFI) - A volume-weighted RSI
    try:
        if TALIB_AVAILABLE:
            df['mfi'] = talib.MFI(df['high'].values, df['low'].values, df['close'].values, df['volume'].values, timeperiod=14)
        else:
            # Calculate typical price
            typical_price = (df['high'] + df['low'] + df['close']) / 3
            
            # Calculate raw money flow
            raw_money_flow = typical_price * df['volume']
            
            # Get positive and negative money flow
            positive_flow = (typical_price > typical_price.shift(1)) * raw_money_flow
            negative_flow = (typical_price < typical_price.shift(1)) * raw_money_flow
            
            # Calculate 14-period positive and negative flow sum
            positive_flow_sum = positive_flow.rolling(window=14).sum()
            negative_flow_sum = negative_flow.rolling(window=14).sum()
            
            # Calculate money flow ratio and index
            money_flow_ratio = positive_flow_sum / negative_flow_sum
            df['mfi'] = 100 - (100 / (1 + money_flow_ratio))
    except Exception as e:
        print(f"Error calculating MFI: {str(e)}")
        df['mfi'] = 50  # Neutral value
    
    # Add NSE-specific Market Quality Index approximation
    # (Simplified approximation of NSE's MQI which measures market quality)
    df['nse_mqi_approx'] = (df['relative_volume'] * (1 - (df['high'] - df['low']) / df['close'])) * 100
    
    return df


def add_delivery_percentage(df, delivery_pct_values=None):
    """
    Add Delivery Percentage for stocks (specific to Indian markets)
    Highly useful for identifying genuine buying/selling vs intraday speculation
    
    Args:
        df: DataFrame with OHLCV data
        delivery_pct_values: Optional actual delivery % data from NSE
        
    Returns:
        DataFrame with delivery percentage analysis added
    """
    try:
        if delivery_pct_values is not None:
            # Use provided delivery percentage values if available
            if len(delivery_pct_values) == len(df):
                df['delivery_pct'] = delivery_pct_values
            else:
                print("Warning: delivery_pct_values length doesn't match dataframe length")
                df['delivery_pct'] = 50  # Default value
        else:
            # Set a default approximation when actual data is not available
            # In real implementation, this should be fetched from NSE's bhav copy
            df['delivery_pct'] = 50  # Default assumption: 50% delivery
        
        # Add delivery volume
        df['delivery_volume'] = df['volume'] * df['delivery_pct'] / 100
        
        # Add delivery volume classification
        # High delivery % indicates strong conviction (common threshold in Indian markets)
        df['high_delivery'] = df['delivery_pct'] > 60
        df['low_delivery'] = df['delivery_pct'] < 40
        
        # Add delivery trend (whether delivery % is increasing)
        df['delivery_pct_sma5'] = df['delivery_pct'].rolling(window=5).mean()
        df['delivery_trend_up'] = df['delivery_pct'] > df['delivery_pct_sma5']
        
    except Exception as e:
        print(f"Error calculating Delivery Percentage: {str(e)}")
        # Add empty delivery columns to avoid errors
        df['delivery_pct'] = 50
        df['delivery_volume'] = df['volume'] * 0.5
        df['high_delivery'] = False
        df['low_delivery'] = False
        df['delivery_pct_sma5'] = 50
        df['delivery_trend_up'] = False
    
    return df


def is_nse_market_open(timestamp):
    """
    Helper function: Check if NSE market is open at a given timestamp
    
    Args:
        timestamp: datetime object
        
    Returns:
        bool: True if market is open, False otherwise
    """
    # NSE trading hours: 9:15 AM to 3:30 PM IST, Monday to Friday
    if timestamp.weekday() >= 5:  # Saturday and Sunday
        return False
    
    market_open = time(9, 15, 0)  # 9:15 AM
    market_close = time(15, 30, 0)  # 3:30 PM
    
    current_time = timestamp.time()
    return market_open <= current_time <= market_close