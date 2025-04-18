"""
Trade Tracking Package

This package provides comprehensive trade logging, performance tracking,
and analytics for algorithmic trading systems.
"""

from .trade_logger import TradeLogger
from .performance_tracker import PerformanceTracker

__all__ = [
    'TradeLogger',
    'PerformanceTracker'
]

# Package information
__version__ = '1.0.0'
__author__ = 'Sambot Team'