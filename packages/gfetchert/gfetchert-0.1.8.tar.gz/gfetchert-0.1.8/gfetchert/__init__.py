"""
__init__.py
-----------
Main package entry for Gfetchert.
"""

from .core import get_rainfall
from .file_ops import fetch_from_file

__all__ = ["get_rainfall", "fetch_from_file"]
