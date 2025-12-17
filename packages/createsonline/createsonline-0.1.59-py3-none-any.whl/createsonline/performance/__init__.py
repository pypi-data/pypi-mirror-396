# createsonline/performance/__init__.py
"""
CREATESONLINE Performance Module

Ultra-high performance optimizations
"""

__all__ = [
    'create_optimized_app',
    'PerformanceOptimizer',
    'CacheManager',
    'ResponseCompression',
    'ConnectionPool'
]

from .core import create_optimized_app, PerformanceOptimizer
from .cache import CacheManager
from .compression import ResponseCompression
from .connection_pool import ConnectionPool