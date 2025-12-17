"""
lomi. SDK Exceptions
AUTO-GENERATED - Do not edit manually
"""


class LomiError(Exception):
    """Base exception for lomi. SDK"""
    def __init__(self, message: str, status_code: int = None, body: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.body = body


class LomiAuthError(LomiError):
    """Authentication error"""
    pass


class LomiNotFoundError(LomiError):
    """Resource not found error"""
    pass


class LomiRateLimitError(LomiError):
    """Rate limit exceeded error"""
    pass
