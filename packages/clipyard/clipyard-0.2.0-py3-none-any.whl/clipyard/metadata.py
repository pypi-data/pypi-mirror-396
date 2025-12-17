"""Metadata saving utilities for download summaries and configs."""

import json
from pathlib import Path

import pandas as pd

from clipyard.models import DownloadConfig, DownloadResult


def save_summary_csv(results: list[DownloadResult], filepath: Path) -> None:
    """
    Save download results to a CSV file.

    Args:
        results: List of DownloadResult objects
        filepath: Path where to save the CSV file
    """
    filepath.parent.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(
        [
            {
                "video_id": result.video_id,
                "video_url": result.video_url,
                "status": result.status,
                "error_reason": result.error_reason,
            }
            for result in results
        ]
    )

    df.to_csv(filepath, index=False)


def save_config_json(config: DownloadConfig, input_args: dict, filepath: Path) -> None:
    """
    Save download configuration and input arguments to a JSON file.

    This allows re-running the download with the same settings.

    Args:
        config: DownloadConfig object
        input_args: Dictionary of input arguments (for CLI re-execution)
        filepath: Path where to save the JSON file
    """
    filepath.parent.mkdir(parents=True, exist_ok=True)

    # Convert Path objects to strings for JSON serialization
    config_dict = {
        "output_dir": str(config.output_dir),
        "metadata_dir": str(config.metadata_dir) if config.metadata_dir else None,
        "resolution": config.resolution,
        "threads": config.threads,
        "workers": config.workers,
        "max_videos": config.max_videos,
        "cookies": str(config.cookies) if config.cookies else None,
        "replace_existing": config.replace_existing,
        "silence_errors": config.silence_errors,
    }

    data = {"config": config_dict, "input_args": input_args}

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def get_failed_videos(results: list[DownloadResult]) -> list[DownloadResult]:
    """
    Filter results to only failed downloads.

    Args:
        results: List of DownloadResult objects

    Returns:
        List of failed DownloadResult objects
    """
    return [r for r in results if r.status == "failed"]


def load_config_json(filepath: Path) -> dict:
    """
    Load download configuration and input arguments from a JSON file.

    This allows re-running a download with the same settings.

    Args:
        filepath: Path to the config JSON file

    Returns:
        Dictionary with 'config' and 'input_args' keys

    Raises:
        FileNotFoundError: If the config file doesn't exist
        json.JSONDecodeError: If the file is not valid JSON
    """
    with open(filepath, encoding="utf-8") as f:
        return json.load(f)
