"""Tests for URL utilities."""

import pytest

from clipyard.url_utils import (
    build_video_url,
    detect_platform_from_id,
    extract_video_id,
)


class TestExtractVideoId:
    """Tests for extract_video_id function."""

    def test_youtube_watch_url(self):
        """Test extracting ID from standard YouTube watch URL."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        video_id, platform = extract_video_id(url)
        assert video_id == "dQw4w9WgXcQ"
        assert platform == "youtube"

    def test_youtube_watch_url_with_query_params(self):
        """Test extracting ID from YouTube URL with query parameters."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&feature=share&si=abc123"
        video_id, platform = extract_video_id(url)
        assert video_id == "dQw4w9WgXcQ"
        assert platform == "youtube"

    def test_youtube_watch_url_with_timestamp(self):
        """Test extracting ID from YouTube URL with timestamp."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=42"
        video_id, platform = extract_video_id(url)
        assert video_id == "dQw4w9WgXcQ"
        assert platform == "youtube"

    def test_youtube_watch_url_with_fragment(self):
        """Test extracting ID from YouTube URL with fragment."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ#t=42"
        video_id, platform = extract_video_id(url)
        assert video_id == "dQw4w9WgXcQ"
        assert platform == "youtube"

    def test_youtube_watch_url_no_www(self):
        """Test extracting ID from YouTube URL without www."""
        url = "https://youtube.com/watch?v=dQw4w9WgXcQ"
        video_id, platform = extract_video_id(url)
        assert video_id == "dQw4w9WgXcQ"
        assert platform == "youtube"

    def test_youtube_watch_url_mobile(self):
        """Test extracting ID from mobile YouTube URL."""
        url = "https://m.youtube.com/watch?v=dQw4w9WgXcQ"
        video_id, platform = extract_video_id(url)
        assert video_id == "dQw4w9WgXcQ"
        assert platform == "youtube"

    def test_youtube_shorts_url(self):
        """Test extracting ID from YouTube Shorts URL."""
        url = "https://www.youtube.com/shorts/8nnu9MPvna8"
        video_id, platform = extract_video_id(url)
        assert video_id == "8nnu9MPvna8"
        assert platform == "youtube"

    def test_youtube_shorts_url_with_params(self):
        """Test extracting ID from YouTube Shorts URL with query parameters."""
        url = "https://www.youtube.com/shorts/8nnu9MPvna8?si=AdQ9kTnk16Oj-kG-"
        video_id, platform = extract_video_id(url)
        assert video_id == "8nnu9MPvna8"
        assert platform == "youtube"

    def test_youtube_youtu_be_url(self):
        """Test extracting ID from youtu.be short URL."""
        url = "https://youtu.be/dQw4w9WgXcQ"
        video_id, platform = extract_video_id(url)
        assert video_id == "dQw4w9WgXcQ"
        assert platform == "youtube"

    def test_youtube_youtu_be_url_with_params(self):
        """Test extracting ID from youtu.be URL with query parameters."""
        url = "https://youtu.be/rmvDxxNubIg?si=AdQ9kTnk16Oj-kG-&t=1"
        video_id, platform = extract_video_id(url)
        assert video_id == "rmvDxxNubIg"
        assert platform == "youtube"

    def test_youtube_youtu_be_url_with_fragment(self):
        """Test extracting ID from youtu.be URL with fragment."""
        url = "https://youtu.be/dQw4w9WgXcQ#t=42"
        video_id, platform = extract_video_id(url)
        assert video_id == "dQw4w9WgXcQ"
        assert platform == "youtube"

    def test_vimeo_url(self):
        """Test extracting ID from Vimeo URL."""
        url = "https://vimeo.com/178940541"
        video_id, platform = extract_video_id(url)
        assert video_id == "178940541"
        assert platform == "vimeo"

    def test_vimeo_url_with_params(self):
        """Test extracting ID from Vimeo URL with query parameters."""
        url = "https://vimeo.com/178940541?autoplay=1"
        video_id, platform = extract_video_id(url)
        assert video_id == "178940541"
        assert platform == "vimeo"

    def test_vimeo_url_with_fragment(self):
        """Test extracting ID from Vimeo URL with fragment."""
        url = "https://vimeo.com/178940541#t=42"
        video_id, platform = extract_video_id(url)
        assert video_id == "178940541"
        assert platform == "vimeo"

    def test_vimeo_url_www(self):
        """Test extracting ID from Vimeo URL with www."""
        url = "https://www.vimeo.com/178940541"
        video_id, platform = extract_video_id(url)
        assert video_id == "178940541"
        assert platform == "vimeo"

    def test_generic_url_extracts_path(self):
        """Test that generic URLs extract the last path segment as ID."""
        video_id, platform = extract_video_id("https://example.com/videos/my-video-123")
        assert video_id == "my-video-123"
        assert platform == "example"

    def test_twitter_url(self):
        """Test extracting from Twitter/X URL."""
        video_id, platform = extract_video_id(
            "https://twitter.com/user/status/1234567890"
        )
        assert video_id == "1234567890"
        assert platform == "twitter"

    def test_x_url(self):
        """Test extracting from x.com URL."""
        video_id, platform = extract_video_id("https://x.com/user/status/1234567890")
        assert video_id == "1234567890"
        assert platform == "twitter"

    def test_tiktok_url(self):
        """Test extracting from TikTok URL."""
        video_id, platform = extract_video_id(
            "https://www.tiktok.com/@user/video/1234567890"
        )
        assert video_id == "1234567890"
        assert platform == "tiktok"

    def test_dailymotion_url(self):
        """Test extracting from Dailymotion URL."""
        video_id, platform = extract_video_id(
            "https://www.dailymotion.com/video/x8abc123"
        )
        assert video_id == "x8abc123"
        assert platform == "dailymotion"

    def test_url_fallback_to_hash(self):
        """Test that URLs without a usable path segment fall back to hash."""
        video_id, platform = extract_video_id("https://example.com/")
        # Should get a hash since there's no meaningful path
        assert len(video_id) == 12  # MD5 hash truncated to 12 chars
        assert platform == "example"

    def test_invalid_format(self):
        """Test that malformed URL raises ValueError."""
        with pytest.raises(ValueError, match="Invalid URL format"):
            extract_video_id("not a url")

    def test_empty_string(self):
        """Test that empty string raises ValueError."""
        with pytest.raises(ValueError, match="Invalid URL format"):
            extract_video_id("")


class TestBuildVideoUrl:
    """Tests for build_video_url function."""

    def test_build_youtube_url(self):
        """Test building YouTube URL from ID."""
        url = build_video_url("dQw4w9WgXcQ", "youtube")
        assert url == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    def test_build_vimeo_url(self):
        """Test building Vimeo URL from ID."""
        url = build_video_url("178940541", "vimeo")
        assert url == "https://vimeo.com/178940541"

    def test_unsupported_platform(self):
        """Test that unsupported platform raises ValueError."""
        with pytest.raises(ValueError, match="Cannot build URL for platform"):
            build_video_url("test", "twitter")

    def test_none_platform(self):
        """Test that None platform raises ValueError."""
        with pytest.raises(ValueError, match="Cannot build URL for video ID"):
            build_video_url("test", None)


class TestDetectPlatformFromId:
    """Tests for detect_platform_from_id function."""

    def test_detect_youtube_id(self):
        """Test detecting YouTube from 11-character ID."""
        platform = detect_platform_from_id("dQw4w9WgXcQ")
        assert platform == "youtube"

    def test_detect_youtube_id_with_dash(self):
        """Test detecting YouTube from ID with dash."""
        platform = detect_platform_from_id("dQw4w9WgX-c")
        assert platform == "youtube"

    def test_detect_youtube_id_with_underscore(self):
        """Test detecting YouTube from ID with underscore."""
        platform = detect_platform_from_id("dQw4w9WgX_c")
        assert platform == "youtube"

    def test_detect_vimeo_id(self):
        """Test detecting Vimeo from numeric ID."""
        platform = detect_platform_from_id("178940541")
        assert platform == "vimeo"

    def test_detect_vimeo_id_long(self):
        """Test detecting Vimeo from long numeric ID."""
        platform = detect_platform_from_id("123456789012345")
        assert platform == "vimeo"

    def test_invalid_id_format(self):
        """Test that invalid ID format raises ValueError."""
        with pytest.raises(ValueError, match="Could not detect platform"):
            detect_platform_from_id("invalid")

    def test_too_short_id(self):
        """Test that too short ID raises ValueError."""
        with pytest.raises(ValueError):
            detect_platform_from_id("short")

    def test_too_long_youtube_id(self):
        """Test that too long ID raises ValueError."""
        with pytest.raises(ValueError):
            detect_platform_from_id("dQw4w9WgXcQx")
