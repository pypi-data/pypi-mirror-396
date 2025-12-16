"""
VizFlow - TB-scale data analysis and visualization library.

Usage:
    import vizflow as vf
"""

__version__ = "0.3.0"

from .config import Config
from .market import CN, CRYPTO, Market, Session
from .ops import aggregate, bin, parse_time
