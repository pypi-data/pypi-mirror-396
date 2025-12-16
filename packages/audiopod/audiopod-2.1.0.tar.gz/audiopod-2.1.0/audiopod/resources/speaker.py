"""
Speaker Service - Speaker Diarization & Separation
"""

import time
from typing import Optional, List, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import AudioPod

POLL_INTERVAL = 3  # seconds
DEFAULT_TIMEOUT = 600  # 10 minutes


class Speaker:
    """Speaker diarization and separation service."""

    def __init__(self, client: "AudioPod"):
        self._client = client

    def diarize(
        self,
        *,
        file: Optional[str] = None,
        url: Optional[str] = None,
        num_speakers: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Create a speaker diarization job.

        Args:
            file: Path to audio file
            url: URL of audio/video
            num_speakers: Number of speakers (hint for better accuracy)

        Returns:
            Speaker job object

        Example:
            >>> job = client.speaker.diarize(
            ...     file="./meeting.mp3",
            ...     num_speakers=3,
            ... )
        """
        if file:
            return self._client.upload(
                "/api/v1/speaker/diarize",
                file,
                field_name="file",
                additional_fields={"num_speakers": num_speakers},
            )

        if url:
            return self._client.post(
                "/api/v1/speaker/diarize",
                json_data={"url": url, "num_speakers": num_speakers},
            )

        raise ValueError("Either file or url must be provided")

    def get(self, job_id: int) -> Dict[str, Any]:
        """Get a speaker job by ID."""
        return self._client.get(f"/api/v1/speaker/jobs/{job_id}")

    def list(
        self,
        *,
        skip: int = 0,
        limit: int = 50,
        status: Optional[str] = None,
        job_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List speaker jobs."""
        return self._client.get(
            "/api/v1/speaker/jobs",
            params={
                "skip": skip,
                "limit": limit,
                "status": status,
                "job_type": job_type,
            },
        )

    def delete(self, job_id: int) -> None:
        """Delete a speaker job."""
        self._client.delete(f"/api/v1/speaker/jobs/{job_id}")

    def wait_for_completion(
        self, job_id: int, timeout: int = DEFAULT_TIMEOUT
    ) -> Dict[str, Any]:
        """Wait for speaker job to complete."""
        start_time = time.time()

        while time.time() - start_time < timeout:
            job = self.get(job_id)
            status = job.get("status", "")

            if status == "COMPLETED":
                return job
            if status == "FAILED":
                raise RuntimeError(
                    f"Speaker processing failed: {job.get('error_message', 'Unknown error')}"
                )

            time.sleep(POLL_INTERVAL)

        raise TimeoutError(f"Speaker processing timed out after {timeout}s")

    def identify(
        self,
        *,
        file: Optional[str] = None,
        url: Optional[str] = None,
        num_speakers: Optional[int] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> Dict[str, Any]:
        """
        Diarize audio and wait for completion.

        Example:
            >>> result = client.speaker.identify(
            ...     file="./meeting.mp3",
            ...     num_speakers=3,
            ... )
            >>> print(result["segments"])
        """
        job = self.diarize(file=file, url=url, num_speakers=num_speakers)
        return self.wait_for_completion(job["id"], timeout=timeout)




