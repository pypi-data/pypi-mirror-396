"""Video download library for downloading large video datasets."""

from clipyard.downloader import download_video, download_videos
from clipyard.metadata import (
    get_failed_videos,
    load_config_json,
    save_config_json,
    save_summary_csv,
)
from clipyard.models import DownloadConfig, DownloadResult, VideoSource
from clipyard.parsers import parse_csv_file, parse_huggingface_dataset, parse_txt_file
from clipyard.url_utils import (
    build_video_url,
    detect_platform_from_id,
    extract_video_id,
)

__all__ = [
    # Models
    "VideoSource",
    "DownloadConfig",
    "DownloadResult",
    # URL utilities
    "extract_video_id",
    "build_video_url",
    "detect_platform_from_id",
    # Parsers
    "parse_txt_file",
    "parse_csv_file",
    "parse_huggingface_dataset",
    # Downloader
    "download_video",
    "download_videos",
    # Metadata
    "save_summary_csv",
    "save_config_json",
    "load_config_json",
    "get_failed_videos",
]
