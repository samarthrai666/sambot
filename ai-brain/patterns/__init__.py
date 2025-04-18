"""
Candlestick pattern detection package for SAMBOT.
Import all functions from submodules for easy access.
"""

from .basic_patterns import (
    is_bullish_engulfing,
    is_bearish_engulfing,
    is_doji,
    is_hammer,
    is_shooting_star,
    is_marubozu
)

from .complex_patterns import (
    is_morning_star,
    is_evening_star,
    is_three_white_soldiers,
    is_three_black_crows,
    is_tweezer_top,
    is_tweezer_bottom,
    is_bullish_harami,
    is_bearish_harami
)

from .pattern_analysis import (
    detect_candlestick_patterns,
    get_candlestick_signals,
    get_pattern_strength,
    filter_patterns_by_trend
)

__all__ = [
    # Basic patterns
    'is_bullish_engulfing',
    'is_bearish_engulfing',
    'is_doji',
    'is_hammer',
    'is_shooting_star',
    'is_marubozu',
    
    # Complex patterns
    'is_morning_star',
    'is_evening_star',
    'is_three_white_soldiers',
    'is_three_black_crows',
    'is_tweezer_top',
    'is_tweezer_bottom',
    'is_bullish_harami',
    'is_bearish_harami',
    
    # Analysis functions
    'detect_candlestick_patterns',
    'get_candlestick_signals',
    'get_pattern_strength',
    'filter_patterns_by_trend'
]