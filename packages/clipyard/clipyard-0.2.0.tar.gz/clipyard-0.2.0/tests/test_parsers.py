"""Tests for input parsers."""

import tempfile
from pathlib import Path

import pandas as pd
import pytest

from clipyard.parsers import parse_csv_file, parse_txt_file


class TestParseTxtFile:
    """Tests for parse_txt_file function."""

    def test_parse_youtube_ids(self):
        """Test parsing text file with YouTube IDs."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("dQw4w9WgXcQ\n")
            f.write("8nnu9MPvna8\n")
            f.write("rmvDxxNubIg\n")
            temp_path = Path(f.name)

        try:
            sources = parse_txt_file(temp_path, platform="youtube")
            assert len(sources) == 3
            assert all(s.platform == "youtube" for s in sources)
            assert sources[0].video_id == "dQw4w9WgXcQ"
            assert sources[1].video_id == "8nnu9MPvna8"
            assert sources[2].video_id == "rmvDxxNubIg"
        finally:
            temp_path.unlink()

    def test_parse_youtube_urls(self):
        """Test parsing text file with YouTube URLs."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("https://www.youtube.com/watch?v=dQw4w9WgXcQ\n")
            f.write("https://youtu.be/8nnu9MPvna8\n")
            f.write("https://www.youtube.com/shorts/rmvDxxNubIg\n")
            temp_path = Path(f.name)

        try:
            sources = parse_txt_file(temp_path, platform="youtube")
            assert len(sources) == 3
            assert all(s.platform == "youtube" for s in sources)
            assert sources[0].video_id == "dQw4w9WgXcQ"
            assert sources[1].video_id == "8nnu9MPvna8"
            assert sources[2].video_id == "rmvDxxNubIg"
        finally:
            temp_path.unlink()

    def test_parse_youtube_urls_with_params(self):
        """Test parsing text file with YouTube URLs containing query parameters."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("https://youtu.be/rmvDxxNubIg?si=AdQ9kTnk16Oj-kG-&t=1\n")
            f.write("https://www.youtube.com/watch?v=dQw4w9WgXcQ&feature=share\n")
            temp_path = Path(f.name)

        try:
            sources = parse_txt_file(temp_path, platform="youtube")
            assert len(sources) == 2
            assert sources[0].video_id == "rmvDxxNubIg"
            assert sources[1].video_id == "dQw4w9WgXcQ"
        finally:
            temp_path.unlink()

    def test_parse_vimeo_ids(self):
        """Test parsing text file with Vimeo IDs."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("178940541\n")
            f.write("123456789\n")
            temp_path = Path(f.name)

        try:
            sources = parse_txt_file(temp_path, platform="vimeo")
            assert len(sources) == 2
            assert all(s.platform == "vimeo" for s in sources)
            assert sources[0].video_id == "178940541"
            assert sources[1].video_id == "123456789"
        finally:
            temp_path.unlink()

    def test_parse_vimeo_urls(self):
        """Test parsing text file with Vimeo URLs."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("https://vimeo.com/178940541\n")
            f.write("https://vimeo.com/123456789\n")
            temp_path = Path(f.name)

        try:
            sources = parse_txt_file(temp_path, platform="vimeo")
            assert len(sources) == 2
            assert all(s.platform == "vimeo" for s in sources)
            assert sources[0].video_id == "178940541"
            assert sources[1].video_id == "123456789"
        finally:
            temp_path.unlink()

    def test_parse_mixed_ids_and_urls(self):
        """Test parsing text file with mixed IDs and URLs."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("dQw4w9WgXcQ\n")
            f.write("https://www.youtube.com/watch?v=8nnu9MPvna8\n")
            f.write("rmvDxxNubIg\n")
            temp_path = Path(f.name)

        try:
            sources = parse_txt_file(temp_path, platform="youtube")
            assert len(sources) == 3
            assert all(s.platform == "youtube" for s in sources)
        finally:
            temp_path.unlink()

    def test_skip_empty_lines(self):
        """Test that empty lines are skipped."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("dQw4w9WgXcQ\n")
            f.write("\n")
            f.write("8nnu9MPvna8\n")
            f.write("   \n")
            f.write("rmvDxxNubIg\n")
            temp_path = Path(f.name)

        try:
            sources = parse_txt_file(temp_path, platform="youtube")
            assert len(sources) == 3
        finally:
            temp_path.unlink()

    def test_skip_comments(self):
        """Test that comment lines (starting with #) are skipped."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("# This is a comment\n")
            f.write("dQw4w9WgXcQ\n")
            f.write("# Another comment\n")
            f.write("8nnu9MPvna8\n")
            temp_path = Path(f.name)

        try:
            sources = parse_txt_file(temp_path, platform="youtube")
            assert len(sources) == 2
        finally:
            temp_path.unlink()

    def test_accepts_any_id_with_explicit_platform(self):
        """Test that any bare ID is accepted when platform is explicitly provided."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("dQw4w9WgXcQ\n")
            f.write("some_custom_id\n")
            f.write("8nnu9MPvna8\n")
            temp_path = Path(f.name)

        try:
            # When platform is explicitly provided, all bare IDs are accepted
            sources = parse_txt_file(temp_path, platform="youtube")
            assert len(sources) == 3
            assert sources[1].video_id == "some_custom_id"
            assert (
                sources[1].video_url == "https://www.youtube.com/watch?v=some_custom_id"
            )
        finally:
            temp_path.unlink()

    def test_skip_unrecognized_ids_without_platform(self):
        """Test that unrecognized bare IDs are skipped when no platform is provided."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("dQw4w9WgXcQ\n")  # Valid YouTube ID (11 chars)
            f.write("invalid_line\n")  # Invalid (not 11 chars, not numeric)
            f.write("8nnu9MPvna8\n")  # Valid YouTube ID (11 chars)
            temp_path = Path(f.name)

        try:
            # When no platform is specified, IDs must match known patterns
            sources = parse_txt_file(temp_path, platform=None)
            assert len(sources) == 2
        finally:
            temp_path.unlink()


class TestParseCsvFile:
    """Tests for parse_csv_file function."""

    def test_parse_csv_with_ids_only(self):
        """Test parsing CSV with only video IDs."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            df = pd.DataFrame(
                {"video_id": ["dQw4w9WgXcQ", "8nnu9MPvna8", "rmvDxxNubIg"]}
            )
            df.to_csv(f.name, index=False)
            temp_path = Path(f.name)

        try:
            sources = parse_csv_file(
                temp_path, id_column="video_id", platform="youtube"
            )
            assert len(sources) == 3
            assert all(s.platform == "youtube" for s in sources)
            assert sources[0].video_id == "dQw4w9WgXcQ"
        finally:
            temp_path.unlink()

    def test_parse_csv_with_urls(self):
        """Test parsing CSV with video URLs."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            df = pd.DataFrame(
                {
                    "video_id": ["dQw4w9WgXcQ", "8nnu9MPvna8"],
                    "video_url": [
                        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                        "https://youtu.be/8nnu9MPvna8?si=abc123",
                    ],
                }
            )
            df.to_csv(f.name, index=False)
            temp_path = Path(f.name)

        try:
            sources = parse_csv_file(
                temp_path,
                id_column="video_id",
                url_column="video_url",
                platform="youtube",
            )
            assert len(sources) == 2
            assert sources[0].video_id == "dQw4w9WgXcQ"
            assert sources[1].video_id == "8nnu9MPvna8"
            assert sources[1].video_url == "https://youtu.be/8nnu9MPvna8?si=abc123"
        finally:
            temp_path.unlink()

    def test_parse_csv_with_urls_extracting_id(self):
        """Test that IDs are extracted from URLs when URL column is provided."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            df = pd.DataFrame(
                {
                    "video_id": ["wrong_id", "another_wrong"],
                    "video_url": [
                        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                        "https://youtu.be/8nnu9MPvna8",
                    ],
                }
            )
            df.to_csv(f.name, index=False)
            temp_path = Path(f.name)

        try:
            sources = parse_csv_file(
                temp_path,
                id_column="video_id",
                url_column="video_url",
                platform="youtube",
            )
            assert len(sources) == 2
            # IDs should be extracted from URLs, not from video_id column
            assert sources[0].video_id == "dQw4w9WgXcQ"
            assert sources[1].video_id == "8nnu9MPvna8"
        finally:
            temp_path.unlink()

    def test_parse_csv_with_missing_url_column(self):
        """Test parsing CSV when URL column is specified but missing."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            df = pd.DataFrame({"video_id": ["dQw4w9WgXcQ", "8nnu9MPvna8"]})
            df.to_csv(f.name, index=False)
            temp_path = Path(f.name)

        try:
            sources = parse_csv_file(
                temp_path,
                id_column="video_id",
                url_column="video_url",  # Column doesn't exist
                platform="youtube",
            )
            assert len(sources) == 2
            # Should build URLs from IDs
            assert sources[0].video_url == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        finally:
            temp_path.unlink()

    def test_parse_csv_with_empty_urls(self):
        """Test parsing CSV with empty URL values."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            df = pd.DataFrame(
                {
                    "video_id": ["dQw4w9WgXcQ", "8nnu9MPvna8"],
                    "video_url": ["https://www.youtube.com/watch?v=dQw4w9WgXcQ", ""],
                }
            )
            df.to_csv(f.name, index=False)
            temp_path = Path(f.name)

        try:
            sources = parse_csv_file(
                temp_path,
                id_column="video_id",
                url_column="video_url",
                platform="youtube",
            )
            assert len(sources) == 2
            assert sources[0].video_url == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            assert sources[1].video_url == "https://www.youtube.com/watch?v=8nnu9MPvna8"
        finally:
            temp_path.unlink()

    def test_parse_csv_with_vimeo(self):
        """Test parsing CSV with Vimeo videos."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            df = pd.DataFrame({"video_id": ["178940541", "123456789"]})
            df.to_csv(f.name, index=False)
            temp_path = Path(f.name)

        try:
            sources = parse_csv_file(temp_path, id_column="video_id", platform="vimeo")
            assert len(sources) == 2
            assert all(s.platform == "vimeo" for s in sources)
        finally:
            temp_path.unlink()

    def test_parse_csv_missing_id_column(self):
        """Test that missing ID column raises ValueError."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            df = pd.DataFrame({"wrong_column": ["dQw4w9WgXcQ"]})
            df.to_csv(f.name, index=False)
            temp_path = Path(f.name)

        try:
            with pytest.raises(ValueError, match="must contain 'video_id' column"):
                parse_csv_file(temp_path, id_column="video_id", platform="youtube")
        finally:
            temp_path.unlink()

    def test_parse_csv_custom_column_names(self):
        """Test parsing CSV with custom column names."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            df = pd.DataFrame(
                {
                    "id": ["dQw4w9WgXcQ", "8nnu9MPvna8"],
                    "url": [
                        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                        "https://youtu.be/8nnu9MPvna8",
                    ],
                }
            )
            df.to_csv(f.name, index=False)
            temp_path = Path(f.name)

        try:
            sources = parse_csv_file(
                temp_path, id_column="id", url_column="url", platform="youtube"
            )
            assert len(sources) == 2
        finally:
            temp_path.unlink()

    def test_parse_csv_skip_empty_rows(self):
        """Test that rows with empty video_id are skipped."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            df = pd.DataFrame({"video_id": ["dQw4w9WgXcQ", "", "8nnu9MPvna8", None]})
            df.to_csv(f.name, index=False)
            temp_path = Path(f.name)

        try:
            sources = parse_csv_file(
                temp_path, id_column="video_id", platform="youtube"
            )
            assert len(sources) == 2
        finally:
            temp_path.unlink()
