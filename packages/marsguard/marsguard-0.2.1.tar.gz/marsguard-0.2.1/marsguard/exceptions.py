"""MARSGuard SDK exception hierarchy with logging."""

from __future__ import annotations
import logging

# Configure a logger for this module
logger = logging.getLogger("marsguard.exceptions")

class MarsGuardError(Exception):
    """Base exception for the MARSGuard SDK."""
    def __init__(self, message: str = ""):
        super().__init__(message)
        if message:
            logger.error(f"MarsGuardError: {message}")

class MarsGuardValidationError(MarsGuardError):
    """Raised when input validation fails."""
    def __init__(self, message: str = ""):
        super().__init__(message)
        logger.error(f"MarsGuardValidationError: {message}")

class MarsGuardAPIError(MarsGuardError):
    """Raised for API errors (non-2xx responses)."""
    def __init__(self, status_code: int, message: str, response_text: str = ""):
        full_message = f"API error {status_code}: {message}"
        super().__init__(full_message)
        self.status_code = status_code
        self.response_text = response_text
        logger.error(f"MarsGuardAPIError: {full_message}\nResponse text: {response_text}")

class MarsGuardNetworkError(MarsGuardError):
    """Raised for network/connection errors."""
    def __init__(self, message: str = ""):
        super().__init__(message)
        logger.error(f"MarsGuardNetworkError: {message}")

__all__ = [
    "MarsGuardError",
    "MarsGuardValidationError",
    "MarsGuardAPIError",
    "MarsGuardNetworkError",
]
