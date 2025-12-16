"""
AudioPod SDK for Python
Professional Audio Processing powered by AI

Example:
    from audiopod import AudioPod

    client = AudioPod(api_key="ap_...")

    # Transcribe audio
    job = client.transcription.create(url="https://...")
    result = client.transcription.wait_for_completion(job.id)
"""

__version__ = "2.1.0"

from .client import AudioPod
from .exceptions import (
    AudioPodError,
    AuthenticationError,
    APIError,
    RateLimitError,
    InsufficientBalanceError,
)

__all__ = [
    "AudioPod",
    "AudioPodError",
    "AuthenticationError",
    "APIError",
    "RateLimitError",
    "InsufficientBalanceError",
    "__version__",
]
