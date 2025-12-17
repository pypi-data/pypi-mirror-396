"""Utilities for parsing and building video URLs."""

import hashlib
import re
from urllib.parse import parse_qs, urlparse

# YouTube ID pattern (11 characters, alphanumeric, dash, underscore)
YOUTUBE_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_-]{11}$")

# Vimeo ID pattern (numeric)
VIMEO_ID_PATTERN = re.compile(r"^\d+$")


def _extract_platform_from_netloc(netloc: str) -> str:
    """
    Extract platform name from a URL's netloc.

    Args:
        netloc: The network location part of a URL (e.g., "www.youtube.com")

    Returns:
        Platform name (e.g., "youtube", "vimeo", "twitter")
    """
    # Remove www. prefix if present
    if netloc.startswith("www."):
        netloc = netloc[4:]

    # Handle common short domains
    domain_map = {
        "youtu.be": "youtube",
        "x.com": "twitter",
        "t.co": "twitter",
        "vm.tiktok.com": "tiktok",
    }
    if netloc in domain_map:
        return domain_map[netloc]

    # Extract the main domain name (first part before .com, .org, etc.)
    # e.g., "youtube.com" -> "youtube", "player.vimeo.com" -> "vimeo"
    parts = netloc.split(".")
    if len(parts) >= 2:
        # For subdomains like "player.vimeo.com", use the second-to-last part
        return parts[-2]

    return netloc


def extract_video_id(url: str) -> tuple[str, str]:
    """
    Extract video ID and platform from a video URL.

    For YouTube and Vimeo, extracts the proper video ID.
    For other platforms, uses the last path segment or a hash of the URL as the ID.

    Args:
        url: Full video URL

    Returns:
        Tuple of (video_id, platform)

    Raises:
        ValueError: If URL format is invalid
    """
    url = url.strip()

    try:
        parsed = urlparse(url)
    except Exception as e:
        raise ValueError(f"Invalid URL format: {url}") from e

    if not parsed.netloc:
        raise ValueError(f"Invalid URL format: {url}")

    platform = _extract_platform_from_netloc(parsed.netloc)

    # YouTube: youtube.com/watch?v=VIDEO_ID
    if parsed.netloc in ("www.youtube.com", "youtube.com", "m.youtube.com"):
        if parsed.path == "/watch":
            query_params = parse_qs(parsed.query)
            if "v" in query_params:
                video_id = query_params["v"][0]
                if YOUTUBE_ID_PATTERN.match(video_id):
                    return (video_id, platform)
        # YouTube Shorts: youtube.com/shorts/VIDEO_ID
        elif parsed.path.startswith("/shorts/"):
            video_id = parsed.path.split("/shorts/")[1].split("?")[0].split("#")[0]
            if YOUTUBE_ID_PATTERN.match(video_id):
                return (video_id, platform)

    # YouTube: youtu.be/VIDEO_ID
    if parsed.netloc in ("youtu.be", "www.youtu.be"):
        video_id = parsed.path.lstrip("/").split("?")[0].split("#")[0]
        if YOUTUBE_ID_PATTERN.match(video_id):
            return (video_id, platform)

    # Vimeo: vimeo.com/VIDEO_ID
    if parsed.netloc in ("vimeo.com", "www.vimeo.com"):
        video_id = parsed.path.lstrip("/").split("?")[0].split("#")[0]
        if VIMEO_ID_PATTERN.match(video_id):
            return (video_id, platform)

    # Generic extraction for other platforms:
    # Try to get the last meaningful path segment as the ID
    path = parsed.path.rstrip("/")
    if path:
        # Get last path segment, removing query params and fragments
        last_segment = path.split("/")[-1].split("?")[0].split("#")[0]
        if last_segment:
            # Sanitize the segment to be filesystem-safe
            video_id = re.sub(r"[^\w\-_]", "_", last_segment)
            if video_id:
                return (video_id, platform)

    # Fallback: use a hash of the URL as the ID
    url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
    return (url_hash, platform)


def build_video_url(video_id: str, platform: str | None) -> str:
    """
    Build a full video URL from a video ID and platform.

    Currently only supports YouTube and Vimeo. For other platforms,
    users must provide the full URL.

    Args:
        video_id: The video ID
        platform: The platform ("youtube" or "vimeo")

    Returns:
        Full video URL

    Raises:
        ValueError: If platform is not supported or not provided
    """
    if platform == "youtube":
        return f"https://www.youtube.com/watch?v={video_id}"
    elif platform == "vimeo":
        return f"https://vimeo.com/{video_id}"
    elif platform is None:
        raise ValueError(
            f"Cannot build URL for video ID '{video_id}' without a platform. "
            "Please provide --platform (youtube/vimeo) or use full URLs instead."
        )
    else:
        raise ValueError(
            f"Cannot build URL for platform '{platform}'. "
            "Only 'youtube' and 'vimeo' support building URLs from bare IDs. "
            "Please provide full URLs for other platforms."
        )


def detect_platform_from_id(video_id: str) -> str:
    """
    Detect platform from a video ID by pattern matching.

    Currently only detects YouTube and Vimeo based on their ID patterns.
    For other platforms, users should provide full URLs instead of bare IDs.

    Args:
        video_id: The video ID to analyze

    Returns:
        Detected platform ("youtube" or "vimeo")

    Raises:
        ValueError: If ID format doesn't match known patterns
    """
    video_id = video_id.strip()

    if YOUTUBE_ID_PATTERN.match(video_id):
        return "youtube"
    elif VIMEO_ID_PATTERN.match(video_id):
        return "vimeo"
    else:
        raise ValueError(
            f"Could not detect platform from video ID: '{video_id}'. "
            "Please provide --platform (youtube/vimeo) or use full URLs instead."
        )
