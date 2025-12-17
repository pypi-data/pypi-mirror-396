"""
Stable Hash Splitter
====================
A scikit-learn compatible splitter for deterministic, ID-based train/test splits.
"""

from .splitter import StableHashSplit

__version__ = "0.1.0"
__all__ = ["StableHashSplit"]