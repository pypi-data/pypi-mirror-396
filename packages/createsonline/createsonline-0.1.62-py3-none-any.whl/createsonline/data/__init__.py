"""
CREATESONLINE Internal Data Structures Module

Pure Python data manipulation library with zero external dependencies.
Lightweight replacement for Pandas with AI-native features.
"""

from .dataframe import CreatesonlineDataFrame
from .series import CreatesonlineSeries
from .io import read_csv, read_json, to_csv, to_json

__all__ = [
    'CreatesonlineDataFrame',
    'CreatesonlineSeries',
    'read_csv',
    'read_json', 
    'to_csv',
    'to_json'
]

# Convenience aliases
DataFrame = CreatesonlineDataFrame
Series = CreatesonlineSeries