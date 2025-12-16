from fastyr.core.contracts.constants import ErrorCodes

class FastyrException(Exception):
    """Base exception for all application errors."""
    def __init__(self, message:str, code:ErrorCodes):
        self.message = message
        self.code = code
        super().__init__(message)

class AuthenticationError(FastyrException):
    """Raised when authentication fails."""
    def __init__(self, message: str):
        super().__init__(message, ErrorCodes.UNAUTHORIZED)

class ValidationError(FastyrException):
    """Raised when input validation fails."""
    def __init__(self, message: str):
        super().__init__(message, ErrorCodes.INVALID_INPUT)

class ProviderError(Exception):
    def __init__(self, message: str, code: str = None):
        super().__init__(message)
        self.message = message
        self.code = code