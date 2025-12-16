"""
AudioPod API Client

Clean, minimal API inspired by OpenAI's SDK design.
"""

import os
from typing import Optional, Dict, Any, BinaryIO
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .exceptions import (
    AuthenticationError,
    APIError,
    RateLimitError,
    InsufficientBalanceError,
)
from .resources.transcription import Transcription
from .resources.voice import Voice
from .resources.music import Music
from .resources.stems import StemExtraction
from .resources.denoiser import Denoiser
from .resources.speaker import Speaker
from .resources.wallet import Wallet

VERSION = "2.1.0"
DEFAULT_BASE_URL = "https://api.audiopod.ai"
DEFAULT_TIMEOUT = 60


class AudioPod:
    """
    AudioPod API Client.

    Args:
        api_key: Your AudioPod API key (starts with 'ap_').
                 If not provided, reads from AUDIOPOD_API_KEY env var.
        base_url: Base URL for the API (default: https://api.audiopod.ai)
        timeout: Request timeout in seconds (default: 60)
        max_retries: Maximum retries for failed requests (default: 3)

    Example:
        >>> from audiopod import AudioPod
        >>> client = AudioPod(api_key="ap_...")
        >>> result = client.transcription.transcribe(url="https://...")
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = 3,
    ):
        self.api_key = api_key or os.getenv("AUDIOPOD_API_KEY")

        if not self.api_key:
            raise AuthenticationError(
                "API key is required. Pass api_key or set AUDIOPOD_API_KEY environment variable."
            )

        if not self.api_key.startswith("ap_"):
            raise AuthenticationError(
                "Invalid API key format. AudioPod API keys start with 'ap_'"
            )

        self.base_url = base_url or DEFAULT_BASE_URL
        self.timeout = timeout

        # Configure session with retries
        self._session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "DELETE"],
            backoff_factor=1,
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self._session.mount("http://", adapter)
        self._session.mount("https://", adapter)

        # Initialize services
        self.transcription = Transcription(self)
        self.voice = Voice(self)
        self.music = Music(self)
        self.stems = StemExtraction(self)
        self.denoiser = Denoiser(self)
        self.speaker = Speaker(self)
        self.wallet = Wallet(self)

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
            "User-Agent": f"audiopod-python/{VERSION}",
            "Accept": "application/json",
        }

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        try:
            response.raise_for_status()
            if response.status_code == 204:
                return {}
            return response.json()
        except requests.exceptions.HTTPError:
            status = response.status_code
            try:
                data = response.json()
                message = data.get("detail") or data.get("message") or str(data)
            except Exception:
                message = response.text or f"HTTP {status}"

            if status == 401:
                raise AuthenticationError(message)
            elif status == 402:
                try:
                    data = response.json()
                    raise InsufficientBalanceError(
                        message,
                        required_cents=data.get("required_cents"),
                        available_cents=data.get("available_cents"),
                    )
                except (ValueError, KeyError):
                    raise InsufficientBalanceError(message)
            elif status == 429:
                raise RateLimitError(message)
            else:
                raise APIError(message, status_code=status)

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a GET request."""
        url = urljoin(self.base_url, endpoint)
        headers = self._get_headers()
        response = self._session.get(
            url, headers=headers, params=params, timeout=self.timeout
        )
        return self._handle_response(response)

    def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make a POST request."""
        url = urljoin(self.base_url, endpoint)
        headers = self._get_headers()
        response = self._session.post(
            url, headers=headers, data=data, json=json_data, timeout=self.timeout
        )
        return self._handle_response(response)

    def delete(self, endpoint: str) -> Dict[str, Any]:
        """Make a DELETE request."""
        url = urljoin(self.base_url, endpoint)
        headers = self._get_headers()
        response = self._session.delete(url, headers=headers, timeout=self.timeout)
        return self._handle_response(response)

    def upload(
        self,
        endpoint: str,
        file_path: str,
        field_name: str = "file",
        additional_fields: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Upload a file."""
        url = urljoin(self.base_url, endpoint)
        headers = self._get_headers()
        headers.pop("Content-Type", None)  # Let requests set multipart boundary

        with open(file_path, "rb") as f:
            files = {field_name: f}
            data = {}
            if additional_fields:
                for key, value in additional_fields.items():
                    if value is not None:
                        data[key] = str(value) if not isinstance(value, str) else value

            response = self._session.post(
                url, headers=headers, files=files, data=data, timeout=self.timeout
            )

        return self._handle_response(response)

    def close(self):
        """Close the client session."""
        self._session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
