"""Custom exceptions for QBDQuery."""


class QBDQueryError(Exception):
    """Base exception for QBDQuery errors."""
    pass


class QBDConnectionError(QBDQueryError):
    """Raised when connection to QuickBooks fails."""
    pass


class QBDSessionError(QBDQueryError):
    """Raised when QuickBooks session operations fail."""
    pass
