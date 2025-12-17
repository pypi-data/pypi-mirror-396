"""
QBDQuery - A Python package for querying QuickBooks Desktop data.
"""

from .client import QuickBooksClient
from .exceptions import QBDQueryError, QBDConnectionError, QBDSessionError

__version__ = "0.1.0"
__all__ = ["QuickBooksClient", "QBDQueryError", "QBDConnectionError", "QBDSessionError"]
