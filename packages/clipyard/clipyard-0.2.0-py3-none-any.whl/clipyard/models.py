"""Data models for video download library."""

from dataclasses import dataclass
from pathlib import Path
from typing import Literal


@dataclass
class VideoSource:
    """Represents a video source with ID, URL, and platform."""

    video_id: str
    video_url: str
    platform: str | None = None


@dataclass
class DownloadConfig:
    """Configuration for video downloads."""

    output_dir: Path
    metadata_dir: Path | None = None
    resolution: int = 1080
    threads: int = 1
    workers: int = 1
    max_videos: int | None = None
    cookies: Path | None = None
    replace_existing: bool = False
    silence_errors: bool = False
    sleep_interval: int = 5
    max_sleep_interval: int = 10


@dataclass
class DownloadResult:
    """Result of a video download attempt."""

    video_id: str
    video_url: str
    status: Literal["success", "failed", "skipped"]
    error_reason: str | None = None
