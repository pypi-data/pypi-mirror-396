"""
Denoiser Service - Audio Noise Reduction
"""

import time
from typing import Optional, List, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import AudioPod

POLL_INTERVAL = 3  # seconds
DEFAULT_TIMEOUT = 600  # 10 minutes


class Denoiser:
    """Audio noise reduction service."""

    def __init__(self, client: "AudioPod"):
        self._client = client

    def create(
        self,
        *,
        file: Optional[str] = None,
        url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a denoise job.

        Args:
            file: Path to audio file
            url: URL of audio/video

        Returns:
            Denoise job object

        Example:
            >>> job = client.denoiser.create(file="./noisy-audio.mp3")
        """
        if file:
            return self._client.upload(
                "/api/v1/denoiser/denoise",
                file,
                field_name="file",
            )

        if url:
            return self._client.post(
                "/api/v1/denoiser/denoise",
                json_data={"url": url},
            )

        raise ValueError("Either file or url must be provided")

    def get(self, job_id: int) -> Dict[str, Any]:
        """Get a denoise job by ID."""
        return self._client.get(f"/api/v1/denoiser/jobs/{job_id}")

    def list(
        self,
        *,
        skip: int = 0,
        limit: int = 50,
        status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List denoise jobs."""
        return self._client.get(
            "/api/v1/denoiser/jobs",
            params={"skip": skip, "limit": limit, "status": status},
        )

    def delete(self, job_id: int) -> None:
        """Delete a denoise job."""
        self._client.delete(f"/api/v1/denoiser/jobs/{job_id}")

    def wait_for_completion(
        self, job_id: int, timeout: int = DEFAULT_TIMEOUT
    ) -> Dict[str, Any]:
        """Wait for denoising to complete."""
        start_time = time.time()

        while time.time() - start_time < timeout:
            job = self.get(job_id)
            status = job.get("status", "")

            if status == "COMPLETED":
                return job
            if status == "FAILED":
                raise RuntimeError(
                    f"Denoising failed: {job.get('error_message', 'Unknown error')}"
                )

            time.sleep(POLL_INTERVAL)

        raise TimeoutError(f"Denoising timed out after {timeout}s")

    def denoise(
        self,
        *,
        file: Optional[str] = None,
        url: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> Dict[str, Any]:
        """
        Denoise audio and wait for completion.

        Example:
            >>> result = client.denoiser.denoise(file="./noisy-audio.mp3")
            >>> print(result["output_url"])
        """
        job = self.create(file=file, url=url)
        return self.wait_for_completion(job["id"], timeout=timeout)




