"""CLI entry point for video download tool."""

import argparse
import os
import tempfile
import time
import urllib.request
from argparse import (
    RawDescriptionHelpFormatter,
    RawTextHelpFormatter,
    ArgumentDefaultsHelpFormatter,
    MetavarTypeHelpFormatter,
)
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import urlparse

from clipyard.downloader import download_videos
from clipyard.metadata import (
    get_failed_videos,
    load_config_json,
    save_config_json,
    save_summary_csv,
)
from clipyard.models import DownloadConfig
from clipyard.parsers import parse_csv_file, parse_huggingface_dataset, parse_txt_file


class CustomHelpFormatter(
    RawTextHelpFormatter,
    # ArgumentDefaultsHelpFormatter,
    # MetavarTypeHelpFormatter,
    # RawDescriptionHelpFormatter,
):
    pass


def is_url(path: str) -> bool:
    """Check if a path is a URL."""
    parsed = urlparse(path)
    return parsed.scheme in ("http", "https")


def download_to_temp_file(url: str, suffix: str = "") -> Path:
    """Download a URL to a temporary file and return the path.

    The caller is responsible for cleaning up the temporary file.
    """
    print(f"🌐 Downloading input file from URL: {url}")
    with urllib.request.urlopen(url) as response:
        fd, temp_path = tempfile.mkstemp(suffix=suffix)
        try:
            with os.fdopen(fd, "wb") as f:
                f.write(response.read())
        except Exception:
            os.unlink(temp_path)
            raise
    return Path(temp_path)


@contextmanager
def resolve_input_path(input_str: str, suffix: str = "") -> Iterator[Path]:
    """Resolve an input path, downloading if it's a URL.

    Yields the resolved Path and cleans up any temporary file on exit.
    """
    if is_url(input_str):
        temp_file = download_to_temp_file(input_str, suffix=suffix)
        try:
            yield temp_file
        finally:
            if temp_file.exists():
                temp_file.unlink()
    else:
        yield Path(input_str)


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Download videos from various sources using yt-dlp",
        formatter_class=CustomHelpFormatter,
    )

    subparsers = parser.add_subparsers(
        dest="command",
        help="Command to run",
        required=True,
    )

    # Download subcommand
    download_parser = subparsers.add_parser(
        "download",
        help="Download videos from various sources",
        formatter_class=CustomHelpFormatter,
    )

    # Config file (for relaunching from saved config)
    download_parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to a saved config JSON file (from a previous run's --metadata-dir). "
        "When provided, loads settings from the config file. "
        "CLI arguments can override config file values.",
    )

    # Input source arguments
    download_parser.add_argument(
        "--input-type",
        type=str,
        default=None,
        choices=["txt", "csv", "huggingface"],
        help="Type of input source (required unless --config is provided)",
    )

    download_parser.add_argument(
        "--input",
        type=str,
        default=None,
        help="Input file path or URL (for txt/csv) or dataset name (for huggingface). "
        "For txt/csv, you can pass a publicly accessible URL and it will be downloaded automatically.",
    )

    # Platform (only needed when providing bare IDs without URLs)
    download_parser.add_argument(
        "--platform",
        type=str,
        default=None,
        help="Platform for building URLs from bare video IDs (youtube/vimeo). "
        "Not needed when providing full URLs - the platform is auto-detected from the URL. If not provided with bare IDs, a best attempt is made to detect it, but not guaranteed.",
    )

    # CSV-specific arguments
    download_parser.add_argument(
        "--id-column",
        type=str,
        default="video_id",
        help="Name of column containing video IDs (default: video_id). "
        "At least one of --id-column or --url-column must be provided.",
    )

    download_parser.add_argument(
        "--url-column",
        type=str,
        default=None,
        help="Name of column containing video URLs (optional). "
        "If provided, video IDs will be extracted from URLs. "
        "If both --id-column and --url-column are provided, URLs are preferred.",
    )

    # HuggingFace-specific arguments
    download_parser.add_argument(
        "--hf-dataset",
        type=str,
        default=None,
        help="HuggingFace dataset identifier (e.g., 'rghermi/sf20k')",
    )

    download_parser.add_argument(
        "--hf-split",
        type=str,
        default="train",
        help="HuggingFace dataset split (default: train)",
    )

    # Output arguments
    download_parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Directory to save downloaded videos (required unless --config is provided)",
    )

    download_parser.add_argument(
        "--metadata-dir",
        type=str,
        default=None,
        help="Directory to save download metadata (CSV summary and config JSON)",
    )

    # Download configuration
    download_parser.add_argument(
        "--resolution",
        type=int,
        default=720,
        choices=[144, 240, 360, 480, 720, 1080],
        help="Video resolution (default: 720)",
    )

    download_parser.add_argument(
        "--threads",
        type=int,
        default=1,
        help="Number of threads per download (passed to yt-dlp --concurrent-fragments)",
    )

    download_parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Number of parallel workers for downloading videos",
    )

    download_parser.add_argument(
        "--max-videos",
        type=int,
        default=None,
        help="Maximum number of videos to download (for debug runs)",
    )

    download_parser.add_argument(
        "--cookies",
        type=str,
        default=None,
        help="Path to cookies file (.txt) for yt-dlp",
    )

    download_parser.add_argument(
        "--replace-existing",
        action="store_true",
        help="Replace existing videos with new downloads. By default, existing videos are skipped.",
    )

    download_parser.add_argument(
        "--silence-errors",
        action="store_true",
        help="Silence yt-dlp errors and warnings",
    )

    download_parser.add_argument(
        "--sleep-interval",
        type=int,
        default=5,
        help="Number of seconds to sleep before each download (passed to yt-dlp, default: 5)",
    )

    download_parser.add_argument(
        "--max-sleep-interval",
        type=int,
        default=10,
        help="Maximum number of seconds to sleep before each download (passed to yt-dlp, default: 10)",
    )

    return parser.parse_args()


def load_video_sources(args) -> list:
    """Load video sources based on input type.

    For txt/csv input types, the input can be either a local file path
    or a publicly accessible URL. URLs are automatically downloaded to
    a temporary file which is cleaned up after parsing.
    """
    platform: str | None = args.platform

    if args.input_type == "txt":
        if not args.input:
            raise ValueError("--input is required for --input-type txt")
        with resolve_input_path(args.input, suffix=".txt") as input_path:
            return parse_txt_file(input_path, platform=platform)

    elif args.input_type == "csv":
        if not args.input:
            raise ValueError("--input is required for --input-type csv")
        with resolve_input_path(args.input, suffix=".csv") as input_path:
            return parse_csv_file(
                input_path,
                id_column=args.id_column,
                url_column=args.url_column,
                platform=platform,
            )

    elif args.input_type == "huggingface":
        dataset_name = args.hf_dataset or args.input
        if not dataset_name:
            raise ValueError(
                "--hf-dataset or --input is required for --input-type huggingface"
            )
        return parse_huggingface_dataset(
            dataset_name=dataset_name,
            split=args.hf_split,
            id_column=args.id_column,
            url_column=args.url_column,
            platform=platform,
        )

    else:
        raise ValueError(f"Unknown input type: {args.input_type}")


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human-readable string."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"


def main():
    """Main CLI entry point."""
    args = parse_args()

    if args.command == "download":
        run_download(args)
    else:
        print(f"Unknown command: {args.command}")
        return 1

    return 0


def apply_config_to_args(args, config_data: dict) -> None:
    """Apply config file values to args."""
    input_args = config_data["input_args"]

    for key, value in input_args.items():
        setattr(args, key, value)


def run_download(args):
    """Run the download command."""
    start_time = time.time()

    # Load config file if provided
    if args.config:
        config_path = Path(args.config).resolve()
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        print(f"📂 Loading config from: {config_path}")
        config_data = load_config_json(config_path)
        apply_config_to_args(args, config_data)

    # Validate required arguments
    if not args.input_type:
        raise ValueError("--input-type is required (or provide --config)")
    if not args.output_dir:
        raise ValueError("--output-dir is required (or provide --config)")

    # Create output directory and convert to absolute path
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    # Setup metadata directory and convert to absolute path
    metadata_dir = Path(args.metadata_dir).resolve() if args.metadata_dir else None
    if metadata_dir:
        metadata_dir.mkdir(parents=True, exist_ok=True)

    # Convert cookies path to absolute if provided
    cookies_path = Path(args.cookies).resolve() if args.cookies else None

    # Load video sources
    print(f"📥 Loading video sources from {args.input_type}...")
    sources = load_video_sources(args)
    print(f"📋 Found {len(sources)} videos to download")

    # Create download config
    config = DownloadConfig(
        output_dir=output_dir,
        metadata_dir=metadata_dir,
        resolution=args.resolution,
        threads=args.threads,
        workers=args.workers,
        max_videos=args.max_videos,
        cookies=cookies_path,
        replace_existing=args.replace_existing,
        silence_errors=args.silence_errors,
        sleep_interval=args.sleep_interval,
        max_sleep_interval=args.max_sleep_interval,
    )

    # Download videos
    print("⬇️  Starting downloads...")
    results = download_videos(sources, config)

    # Calculate statistics
    total_videos = len(results)
    downloaded_count = sum(1 for r in results if r.status == "success")
    skipped_count = sum(1 for r in results if r.status == "skipped")
    failed_count = sum(1 for r in results if r.status == "failed")
    failed_videos = get_failed_videos(results)

    # Save metadata
    if metadata_dir:
        # Save summary CSV
        summary_csv_path = metadata_dir / "download_summary.csv"
        save_summary_csv(results, summary_csv_path)
        print(f"\n💾 Saved download summary to: {summary_csv_path}")

        # Save failed videos CSV
        if failed_videos:
            failed_csv_path = metadata_dir / "failed_videos.csv"
            save_summary_csv(failed_videos, failed_csv_path)
            print(f"💾 Saved {len(failed_videos)} failed videos to: {failed_csv_path}")

        # Save config JSON
        config_json_path = metadata_dir / "download_config.json"
        input_args = vars(args)  # Convert argparse.Namespace to dict
        # Update input_args with absolute paths for relaunching from any directory
        input_args["output_dir"] = str(output_dir)
        if metadata_dir:
            input_args["metadata_dir"] = str(metadata_dir)
        if cookies_path:
            input_args["cookies"] = str(cookies_path)
        save_config_json(config, input_args, config_json_path)
        print(f"💾 Saved download config to: {config_json_path}")

    # Calculate runtime
    end_time = time.time()
    duration_str = format_duration(end_time - start_time)

    # Print summary
    print("\n" + "=" * 50)
    print("📊 DOWNLOAD SUMMARY")
    print("=" * 50)
    print(f"Target Resolution:  {args.resolution}p")
    print(f"Total Videos:       {total_videos}")
    print("-" * 25)
    print(f"✅ Successfully Downloaded: {downloaded_count}")
    print(f"⏩ Skipped (already exist): {skipped_count}")
    print(f"❌ Failed to Download:     {failed_count}")
    print("-" * 25)
    print(f"⏱️  Total Runtime:          {duration_str}")
    print("=" * 50)


if __name__ == "__main__":
    main()
