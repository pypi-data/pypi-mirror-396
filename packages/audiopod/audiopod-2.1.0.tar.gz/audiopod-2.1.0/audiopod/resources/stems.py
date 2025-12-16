"""
Stem Extraction Service - Audio Stem Separation

Simple mode-based API for separating audio into individual stems.
"""

import time
from typing import Optional, Dict, Any, Literal, TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import AudioPod

POLL_INTERVAL = 3  # seconds
DEFAULT_TIMEOUT = 600  # 10 minutes

# Separation modes
StemMode = Literal["single", "two", "four", "six", "producer", "studio", "mastering"]

# Single stem options
SingleStem = Literal["vocals", "drums", "bass", "guitar", "piano", "other"]


class StemExtraction:
    """
    Audio stem separation service.

    Separate audio into individual components using simple mode selection.

    Modes:
        - single: Extract one stem (requires stem parameter)
        - two: Vocals + Instrumental
        - four: Vocals, Drums, Bass, Other
        - six: Vocals, Drums, Bass, Guitar, Piano, Other
        - producer: 8 stems with drum kit decomposition
        - studio: 12 stems for professional mixing
        - mastering: 16 stems maximum detail

    Example:
        >>> client = AudioPod(api_key="ap_...")
        >>>
        >>> # Six-stem separation from YouTube
        >>> job = client.stems.extract(
        ...     url="https://youtube.com/watch?v=VIDEO_ID",
        ...     mode="six"
        ... )
        >>>
        >>> # Wait for completion
        >>> result = client.stems.wait_for_completion(job["id"])
        >>> print(result["download_urls"])
    """

    def __init__(self, client: "AudioPod"):
        self._client = client

    def extract(
        self,
        *,
        file: Optional[str] = None,
        url: Optional[str] = None,
        mode: StemMode = "four",
        stem: Optional[SingleStem] = None,
    ) -> Dict[str, Any]:
        """
        Extract stems from audio using simple mode selection.

        Args:
            file: Path to local audio file (MP3, WAV, FLAC, M4A, OGG)
            url: URL of audio/video (YouTube, SoundCloud, direct link)
            mode: Separation mode:
                - "single": Extract one stem (specify stem param)
                - "two": Vocals + Instrumental
                - "four": Vocals, Drums, Bass, Other (default)
                - "six": Vocals, Drums, Bass, Guitar, Piano, Other
                - "producer": 8 stems with kick, snare, hihat
                - "studio": 12 stems for professional mixing
                - "mastering": 16 stems maximum detail
            stem: For mode="single", which stem to extract:
                vocals, drums, bass, guitar, piano, other

        Returns:
            Job object with id, status, task_id

        Raises:
            ValueError: If neither file nor url provided, or missing stem for single mode

        Example:
            >>> # From URL with 6 stems
            >>> job = client.stems.extract(
            ...     url="https://youtube.com/watch?v=VIDEO_ID",
            ...     mode="six"
            ... )
            >>>
            >>> # From file with 4 stems
            >>> job = client.stems.extract(
            ...     file="./song.mp3",
            ...     mode="four"
            ... )
            >>>
            >>> # Extract only vocals
            >>> job = client.stems.extract(
            ...     url="https://youtube.com/watch?v=VIDEO_ID",
            ...     mode="single",
            ...     stem="vocals"
            ... )
        """
        if not file and not url:
            raise ValueError("Either file or url must be provided")

        if mode == "single" and not stem:
            raise ValueError(
                "stem parameter required for mode='single'. Options: vocals, drums, bass, guitar, piano, other"
            )

        # Build form data
        data = {"mode": mode}
        if stem:
            data["stem"] = stem

        if file:
            return self._client.upload(
                "/api/v1/stem-extraction/api/extract",
                file,
                field_name="file",
                additional_fields=data,
            )

        if url:
            data["url"] = url
            return self._client.post(
                "/api/v1/stem-extraction/api/extract",
                data=data,
            )

        raise ValueError("Either file or url must be provided")

    def status(self, job_id: int) -> Dict[str, Any]:
        """
        Get the status of a stem extraction job.

        Args:
            job_id: The job ID returned from extract()

        Returns:
            Job status with download_urls when completed

        Example:
            >>> status = client.stems.status(5512)
            >>> if status["status"] == "COMPLETED":
            ...     print(status["download_urls"])
        """
        return self._client.get(f"/api/v1/stem-extraction/status/{job_id}")

    def get(self, job_id: int) -> Dict[str, Any]:
        """Get a stem extraction job by ID."""
        return self._client.get(f"/api/v1/stem-extraction/jobs/{job_id}")

    def list(
        self,
        *,
        skip: int = 0,
        limit: int = 50,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        List stem extraction jobs.

        Args:
            skip: Number of jobs to skip (pagination)
            limit: Maximum jobs to return (default: 50)
            status: Filter by status (PENDING, PROCESSING, COMPLETED, FAILED)

        Returns:
            List of stem extraction jobs
        """
        return self._client.get(
            "/api/v1/stem-extraction/jobs",
            params={"skip": skip, "limit": limit, "status": status},
        )

    def delete(self, job_id: int) -> None:
        """Delete a stem extraction job."""
        self._client.delete(f"/api/v1/stem-extraction/jobs/{job_id}")

    def wait_for_completion(self, job_id: int, timeout: int = DEFAULT_TIMEOUT) -> Dict[str, Any]:
        """
        Wait for stem extraction to complete.

        Args:
            job_id: The job ID to wait for
            timeout: Maximum wait time in seconds (default: 600)

        Returns:
            Completed job with download_urls

        Raises:
            RuntimeError: If job fails
            TimeoutError: If timeout exceeded

        Example:
            >>> job = client.stems.extract(url="...", mode="six")
            >>> result = client.stems.wait_for_completion(job["id"])
            >>> for stem, url in result["download_urls"].items():
            ...     print(f"{stem}: {url}")
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            job = self.status(job_id)
            job_status = job.get("status", "")

            if job_status == "COMPLETED":
                return job
            if job_status == "FAILED":
                raise RuntimeError(
                    f"Stem extraction failed: {job.get('error_message', 'Unknown error')}"
                )

            time.sleep(POLL_INTERVAL)

        raise TimeoutError(f"Stem extraction timed out after {timeout}s")

    def separate(
        self,
        *,
        file: Optional[str] = None,
        url: Optional[str] = None,
        mode: StemMode = "four",
        stem: Optional[SingleStem] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> Dict[str, Any]:
        """
        Extract stems and wait for completion (convenience method).

        Args:
            file: Path to local audio file
            url: URL of audio/video
            mode: Separation mode (single, two, four, six, producer, studio, mastering)
            stem: For mode="single", which stem to extract
            timeout: Maximum wait time in seconds

        Returns:
            Completed job with download_urls

        Example:
            >>> # One-liner: extract and wait
            >>> result = client.stems.separate(
            ...     url="https://youtube.com/watch?v=VIDEO_ID",
            ...     mode="six"
            ... )
            >>> print(result["download_urls"]["vocals"])
        """
        job = self.extract(file=file, url=url, mode=mode, stem=stem)
        return self.wait_for_completion(job["id"], timeout=timeout)

    def modes(self) -> Dict[str, Any]:
        """
        Get available separation modes.

        Returns:
            List of available modes with descriptions

        Example:
            >>> modes = client.stems.modes()
            >>> for m in modes["modes"]:
            ...     print(f"{m['mode']}: {m['description']}")
        """
        return self._client.get("/api/v1/stem-extraction/modes")
