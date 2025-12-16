"""
Voice Service - Voice Cloning & Text-to-Speech
"""

import time
from typing import Optional, List, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import AudioPod

POLL_INTERVAL = 2  # seconds
DEFAULT_TIMEOUT = 300  # 5 minutes


class Voice:
    """Voice cloning and text-to-speech service."""

    def __init__(self, client: "AudioPod"):
        self._client = client

    def list(self) -> List[Dict[str, Any]]:
        """List all available voices."""
        return self._client.get("/api/v1/voice/voices")

    def get(self, voice_id: int) -> Dict[str, Any]:
        """Get a voice by ID."""
        return self._client.get(f"/api/v1/voice/voices/{voice_id}")

    def create(
        self,
        name: str,
        audio_file: str,
        *,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a new voice clone.

        Args:
            name: Name for the voice
            audio_file: Path to audio sample file
            description: Optional description

        Returns:
            Created voice object

        Example:
            >>> voice = client.voice.create(
            ...     name="My Voice",
            ...     audio_file="./sample.mp3",
            ... )
        """
        return self._client.upload(
            "/api/v1/voice/voices",
            audio_file,
            field_name="audio_file",
            additional_fields={"name": name, "description": description},
        )

    def delete(self, voice_id: int) -> None:
        """Delete a voice."""
        self._client.delete(f"/api/v1/voice/voices/{voice_id}")

    def speak(
        self,
        text: str,
        voice_id: int,
        *,
        speed: float = 1.0,
    ) -> Dict[str, Any]:
        """
        Generate speech from text.

        Args:
            text: Text to convert to speech
            voice_id: Voice ID to use
            speed: Speech speed (0.5 to 2.0)

        Returns:
            TTS job object
        """
        return self._client.post(
            "/api/v1/voice/tts/generate",
            json_data={
                "text": text,
                "voice_id": voice_id,
                "speed": speed,
            },
        )

    def get_job(self, job_id: int) -> Dict[str, Any]:
        """Get TTS job status."""
        return self._client.get(f"/api/v1/voice/tts/status/{job_id}")

    def wait_for_completion(
        self, job_id: int, timeout: int = DEFAULT_TIMEOUT
    ) -> Dict[str, Any]:
        """Wait for TTS job to complete."""
        start_time = time.time()

        while time.time() - start_time < timeout:
            job = self.get_job(job_id)
            status = job.get("status", "")

            if status == "COMPLETED":
                return job
            if status == "FAILED":
                raise RuntimeError(
                    f"TTS generation failed: {job.get('error_message', 'Unknown error')}"
                )

            time.sleep(POLL_INTERVAL)

        raise TimeoutError(f"TTS generation timed out after {timeout}s")

    def generate(
        self,
        text: str,
        voice_id: int,
        *,
        speed: float = 1.0,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> Dict[str, Any]:
        """
        Generate speech and wait for completion.

        Example:
            >>> result = client.voice.generate(
            ...     text="Hello, world!",
            ...     voice_id=123,
            ... )
            >>> print(result["output_url"])
        """
        job = self.speak(text, voice_id, speed=speed)
        return self.wait_for_completion(job["id"], timeout=timeout)




