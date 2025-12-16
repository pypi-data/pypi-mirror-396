"""
AudioPod SDK Exceptions
"""

from typing import Optional


class AudioPodError(Exception):
    """Base exception for AudioPod SDK."""

    def __init__(self, message: str = "An error occurred"):
        self.message = message
        super().__init__(self.message)


class AuthenticationError(AudioPodError):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message)


class APIError(AudioPodError):
    """Raised when an API request fails."""

    def __init__(self, message: str = "API request failed", status_code: Optional[int] = None):
        self.status_code = status_code
        super().__init__(message)


class RateLimitError(AudioPodError):
    """Raised when rate limit is exceeded."""

    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message)


class InsufficientBalanceError(AudioPodError):
    """Raised when wallet balance is insufficient."""

    def __init__(
        self,
        message: str = "Insufficient wallet balance",
        required_cents: Optional[int] = None,
        available_cents: Optional[int] = None,
    ):
        self.required_cents = required_cents
        self.available_cents = available_cents
        super().__init__(message)
