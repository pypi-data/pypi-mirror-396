"""
Music Service - AI Music Generation
"""

import time
from typing import Optional, List, Dict, Any, Literal, TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import AudioPod

POLL_INTERVAL = 5  # seconds
DEFAULT_TIMEOUT = 600  # 10 minutes

MusicTask = Literal[
    "text2music",
    "prompt2instrumental",
    "lyric2vocals",
    "text2rap",
    "text2samples",
    "audio2audio",
    "songbloom",
]


class Music:
    """AI music generation service."""

    def __init__(self, client: "AudioPod"):
        self._client = client

    def create(
        self,
        prompt: str,
        *,
        lyrics: Optional[str] = None,
        duration: int = 30,
        task: Optional[MusicTask] = None,
        genre: Optional[str] = None,
        display_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate music from text.

        Args:
            prompt: Text prompt describing the music
            lyrics: Lyrics (for vocal tracks)
            duration: Duration in seconds (default: 30)
            task: Task type (auto-detected based on lyrics if not specified)
            genre: Genre preset
            display_name: Display name for the track

        Returns:
            Music job object

        Example:
            >>> job = client.music.create(
            ...     prompt="Upbeat electronic dance music",
            ...     duration=30,
            ... )
        """
        if task is None:
            task = "text2music" if lyrics else "prompt2instrumental"

        endpoint = f"/api/v1/music/{task}"

        return self._client.post(
            endpoint,
            json_data={
                "prompt": prompt,
                "lyrics": lyrics,
                "audio_duration": duration,
                "display_name": display_name,
                "genre_preset": genre,
            },
        )

    def instrumental(
        self, prompt: str, duration: int = 30
    ) -> Dict[str, Any]:
        """Generate instrumental music."""
        return self.create(prompt, duration=duration, task="prompt2instrumental")

    def song(
        self, prompt: str, lyrics: str, duration: int = 60
    ) -> Dict[str, Any]:
        """Generate a song with vocals."""
        return self.create(prompt, lyrics=lyrics, duration=duration, task="text2music")

    def rap(
        self, prompt: str, lyrics: str, duration: int = 60
    ) -> Dict[str, Any]:
        """Generate rap music."""
        return self.create(prompt, lyrics=lyrics, duration=duration, task="text2rap")

    def get(self, job_id: int) -> Dict[str, Any]:
        """Get a music job by ID."""
        return self._client.get(f"/api/v1/music/jobs/{job_id}/status")

    def list(
        self,
        *,
        skip: int = 0,
        limit: int = 50,
        task: Optional[MusicTask] = None,
        status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List music jobs."""
        return self._client.get(
            "/api/v1/music/jobs",
            params={"skip": skip, "limit": limit, "task": task, "status": status},
        )

    def delete(self, job_id: int) -> None:
        """Delete a music job."""
        self._client.delete(f"/api/v1/music/jobs/{job_id}")

    def wait_for_completion(
        self, job_id: int, timeout: int = DEFAULT_TIMEOUT
    ) -> Dict[str, Any]:
        """Wait for music generation to complete."""
        start_time = time.time()

        while time.time() - start_time < timeout:
            job = self.get(job_id)
            status = job.get("status", "").upper()

            if status == "COMPLETED":
                return job
            if status == "FAILED":
                raise RuntimeError(
                    f"Music generation failed: {job.get('error_message', 'Unknown error')}"
                )

            time.sleep(POLL_INTERVAL)

        raise TimeoutError(f"Music generation timed out after {timeout}s")

    def generate(
        self,
        prompt: str,
        *,
        lyrics: Optional[str] = None,
        duration: int = 30,
        task: Optional[MusicTask] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> Dict[str, Any]:
        """
        Generate music and wait for completion.

        Example:
            >>> result = client.music.generate(
            ...     prompt="Upbeat electronic dance music",
            ...     duration=30,
            ... )
            >>> print(result["output_url"])
        """
        job = self.create(prompt, lyrics=lyrics, duration=duration, task=task)
        return self.wait_for_completion(job["id"], timeout=timeout)

    def get_presets(self) -> Dict[str, Any]:
        """Get available genre presets."""
        return self._client.get("/api/v1/music/presets")




