"""
Transcription Service - Speech-to-Text
"""

import time
from typing import Optional, List, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import AudioPod

POLL_INTERVAL = 3  # seconds
DEFAULT_TIMEOUT = 600  # 10 minutes


class Transcription:
    """Speech-to-text transcription service."""

    def __init__(self, client: "AudioPod"):
        self._client = client

    def create(
        self,
        *,
        url: Optional[str] = None,
        urls: Optional[List[str]] = None,
        language: Optional[str] = None,
        speaker_diarization: bool = False,
        min_speakers: Optional[int] = None,
        max_speakers: Optional[int] = None,
        word_timestamps: bool = True,
    ) -> Dict[str, Any]:
        """
        Create a transcription job from URL(s).

        Args:
            url: Single URL to transcribe
            urls: List of URLs to transcribe
            language: Language code (ISO 639-1). Auto-detected if not specified
            speaker_diarization: Enable speaker diarization
            min_speakers: Minimum number of speakers (hint for diarization)
            max_speakers: Maximum number of speakers (hint for diarization)
            word_timestamps: Enable word-level timestamps

        Returns:
            Job object with id and status

        Example:
            >>> job = client.transcription.create(
            ...     url="https://youtube.com/watch?v=...",
            ...     speaker_diarization=True,
            ... )
        """
        source_urls = urls or ([url] if url else [])
        if not source_urls:
            raise ValueError("At least one URL is required")

        return self._client.post(
            "/api/v1/transcribe/transcribe",
            json_data={
                "source_urls": source_urls,
                "language": language,
                "enable_speaker_diarization": speaker_diarization,
                "min_speakers": min_speakers,
                "max_speakers": max_speakers,
                "enable_word_timestamps": word_timestamps,
            },
        )

    def upload(
        self,
        file_path: str,
        *,
        language: Optional[str] = None,
        speaker_diarization: bool = False,
    ) -> Dict[str, Any]:
        """
        Upload a file for transcription.

        Args:
            file_path: Path to the audio file
            language: Language code (ISO 639-1)
            speaker_diarization: Enable speaker diarization

        Returns:
            Job object with id and status
        """
        return self._client.upload(
            "/api/v1/transcribe/transcribe-upload",
            file_path,
            field_name="files",
            additional_fields={
                "language": language,
                "enable_speaker_diarization": speaker_diarization,
            },
        )

    def get(self, job_id: int) -> Dict[str, Any]:
        """Get a transcription job by ID."""
        return self._client.get(f"/api/v1/transcribe/jobs/{job_id}")

    def list(
        self,
        *,
        skip: int = 0,
        limit: int = 50,
        status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List transcription jobs."""
        return self._client.get(
            "/api/v1/transcribe/jobs",
            params={"offset": skip, "limit": limit, "status": status},
        )

    def delete(self, job_id: int) -> None:
        """Delete a transcription job."""
        self._client.delete(f"/api/v1/transcribe/jobs/{job_id}")

    def get_transcript(
        self, job_id: int, format: str = "json"
    ) -> Any:
        """
        Get transcript content.

        Args:
            job_id: Job ID
            format: Output format ('json', 'txt', 'srt', 'vtt')
        """
        return self._client.get(
            f"/api/v1/transcribe/jobs/{job_id}/transcript",
            params={"format": format},
        )

    def wait_for_completion(
        self, job_id: int, timeout: int = DEFAULT_TIMEOUT
    ) -> Dict[str, Any]:
        """
        Wait for a transcription job to complete.

        Args:
            job_id: Job ID to wait for
            timeout: Maximum time to wait in seconds

        Returns:
            Completed job object

        Raises:
            TimeoutError: If job doesn't complete within timeout
            RuntimeError: If job fails
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            job = self.get(job_id)
            status = job.get("status", "")

            if status == "COMPLETED":
                return job
            if status == "FAILED":
                raise RuntimeError(
                    f"Transcription failed: {job.get('error_message', 'Unknown error')}"
                )
            if status == "CANCELLED":
                raise RuntimeError("Transcription was cancelled")

            time.sleep(POLL_INTERVAL)

        raise TimeoutError(f"Transcription timed out after {timeout}s")

    def transcribe(
        self,
        *,
        url: Optional[str] = None,
        urls: Optional[List[str]] = None,
        language: Optional[str] = None,
        speaker_diarization: bool = False,
        min_speakers: Optional[int] = None,
        max_speakers: Optional[int] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> Dict[str, Any]:
        """
        Create and wait for transcription to complete.

        This is a convenience method that combines create() and wait_for_completion().

        Example:
            >>> result = client.transcription.transcribe(
            ...     url="https://youtube.com/watch?v=...",
            ...     speaker_diarization=True,
            ... )
            >>> print(result["detected_language"])
        """
        job = self.create(
            url=url,
            urls=urls,
            language=language,
            speaker_diarization=speaker_diarization,
            min_speakers=min_speakers,
            max_speakers=max_speakers,
        )
        job_id = job.get("id") or job.get("job_id")
        return self.wait_for_completion(job_id, timeout=timeout)




