class SnirhError(Exception):
    """Base exception for SNIRH package."""
    pass

class SnirhNetworkError(SnirhError):
    """Raised when a network request fails."""
    pass

class SnirhParsingError(SnirhError):
    """Raised when parsing the response fails."""
    pass
