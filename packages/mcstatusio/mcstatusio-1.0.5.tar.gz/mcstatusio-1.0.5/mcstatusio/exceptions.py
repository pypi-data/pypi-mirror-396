"""
Custom exceptions for the mcstatusio package.
"""

class McstatusioError(Exception):
    """Base exception for mcstatusio."""
    pass


class McstatusioTimeoutError(McstatusioError):
    """Raised when a request times out."""
    pass


class McstatusioConnectionError(McstatusioError):
    """Raised when a connection fails."""
    pass


class McstatusioHTTPError(McstatusioError):
    """Raised when an HTTP error occurs."""
    pass
