"""Core video download logic using yt-dlp."""

import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

from tqdm import tqdm

from clipyard.models import DownloadConfig, DownloadResult, VideoSource


def _extract_error_reason(result: subprocess.CompletedProcess[str]) -> str | None:
    """
    Extract error reason from yt-dlp subprocess result.

    Args:
        result: Completed subprocess result

    Returns:
        Error reason string or None if successful
    """
    # Successful download, no error reason
    if result.returncode == 0:
        return None

    # Extract error reason from stderr
    error_reason = None
    if result.stderr:
        # Try to extract a meaningful error message
        stderr_lines = result.stderr.strip().split("\n")
        # Look for common error patterns
        for line in reversed(stderr_lines):  # Check from bottom up (most recent errors)
            line_lower = line.lower()
            if (
                "error" in line_lower
                or "unavailable" in line_lower
                or "private" in line_lower
                or "deleted" in line_lower
            ):
                error_reason = line.strip()
                break
        # If no specific error found, use last line or first meaningful line
        if not error_reason:
            for line in reversed(stderr_lines):
                if line.strip() and not line.strip().startswith("["):
                    error_reason = line.strip()[:200]  # Limit length
                    break
    if not error_reason:
        error_reason = "Unknown error"

    return error_reason


def download_video(source: VideoSource, config: DownloadConfig) -> DownloadResult:
    """
    Download a single video using yt-dlp.

    Args:
        source: VideoSource containing video ID, URL, and platform
        config: DownloadConfig with download settings

    Returns:
        DownloadResult with status and error information
    """
    video_path = config.output_dir / f"{source.video_id}.mp4"

    # Skip if video already exists
    if video_path.exists() and not config.replace_existing:
        return DownloadResult(
            video_id=source.video_id,
            video_url=source.video_url,
            status="skipped",
            error_reason=None,
        )

    # Construct yt-dlp command
    # fmt: off
    cmd_args = [
        "yt-dlp",
        "-S", "vcodec:h264,res,acodec:m4a",  # Quicktime compatible; h264 decodes faster as well
        "-f", f"bestvideo[height<={config.resolution}]+bestaudio/best[height<={config.resolution}]",
        "-o", str(video_path),
        "--concurrent-fragments", str(config.threads),
        "--sleep-interval", str(config.sleep_interval),
        "--max-sleep-interval", str(config.max_sleep_interval),
        source.video_url,
    ]
    # fmt: on

    if config.silence_errors:
        cmd_args.extend(["--no-warnings", "--ignore-errors"])

    if config.cookies:
        cmd_args.extend(["--cookies", str(config.cookies)])

    # Execute command and check for errors
    result = subprocess.run(cmd_args, capture_output=True, text=True)

    if result.returncode == 0:
        status = "success"
        error_reason = None
    else:
        status = "failed"
        error_reason = _extract_error_reason(result)

    return DownloadResult(
        video_id=source.video_id,
        video_url=source.video_url,
        status=status,
        error_reason=error_reason,
    )


def download_videos(
    sources: list[VideoSource], config: DownloadConfig
) -> list[DownloadResult]:
    """
    Download multiple videos in parallel using ThreadPoolExecutor.

    Args:
        sources: List of VideoSource objects to download
        config: DownloadConfig with download settings

    Returns:
        List of DownloadResult objects
    """
    # Limit number of videos if specified
    if config.max_videos is not None:
        sources = sources[: config.max_videos]

    total_videos = len(sources)
    results: list[DownloadResult] = []

    # Parallel download using ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=config.workers) as executor:
        # Submit all download tasks
        future_to_source = {
            executor.submit(download_video, source, config): source
            for source in sources
        }

        # Process completed downloads with progress bar
        with tqdm(total=total_videos, desc="Downloading Videos") as pbar:
            for future in as_completed(future_to_source):
                result = future.result()
                results.append(result)
                pbar.update(1)

    return results
