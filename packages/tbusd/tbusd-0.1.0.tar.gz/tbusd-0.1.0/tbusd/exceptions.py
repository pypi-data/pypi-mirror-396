"""TBUSD SDK Exceptions"""


class TBUSDError(Exception):
    """Base exception for TBUSD SDK errors"""
    pass


class RateLimitError(TBUSDError):
    """Raised when daily transaction limit is exceeded"""
    pass


class InsufficientBalanceError(TBUSDError):
    """Raised when wallet has insufficient TBUSD balance"""
    pass


class AuthenticationError(TBUSDError):
    """Raised when API key is invalid or revoked"""
    pass


class RelayerError(TBUSDError):
    """Raised when the relayer service is unavailable"""
    pass
