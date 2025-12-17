# Development Guide

This document provides an overview of the clipyard codebase structure and development workflow. It assumes you've read the README.md and understand what the package does, but haven't explored the internals yet.

## Project Structure

```
clipyard/
├── src/clipyard/          # Main package code
│   ├── __init__.py       # Public API exports
│   ├── models.py         # Data models (dataclasses)
│   ├── url_utils.py      # URL parsing and building utilities
│   ├── parsers.py        # Input source parsers
│   ├── downloader.py     # Core download logic
│   ├── metadata.py       # Metadata saving utilities
│   └── cli.py            # Command-line interface
├── tests/                # Test suite
│   ├── test_url_utils.py  # URL utility tests
│   └── test_parsers.py   # Parser tests
├── pyproject.toml        # Project configuration
└── README.md             # User documentation
```

## Architecture Overview

The package is organized into focused modules with clear responsibilities:

### Core Modules

1. **`models.py`** - Data models using dataclasses
   - `VideoSource`: Represents a video with ID, URL, and platform
   - `DownloadConfig`: Configuration for downloads
   - `DownloadResult`: Result of a download attempt

2. **`url_utils.py`** - URL parsing and building
   - `extract_video_id()`: Extracts video ID from YouTube/Vimeo URLs
   - `build_video_url()`: Builds URL from video ID and platform
   - `detect_platform_from_id()`: Detects platform from ID pattern

3. **`parsers.py`** - Input source parsers
   - `parse_txt_file()`: Parses text files (one ID/URL per line)
   - `parse_csv_file()`: Parses CSV files
   - `parse_huggingface_dataset()`: Parses HuggingFace datasets
   - `_parse_dataframe_row()`: Shared helper for DataFrame parsing

4. **`downloader.py`** - Core download logic
   - `download_video()`: Downloads a single video using yt-dlp
   - `download_videos()`: Orchestrates parallel downloads with progress bar

5. **`metadata.py`** - Metadata utilities
   - `save_summary_csv()`: Saves download results to CSV
   - `save_config_json()`: Saves configuration for re-running
   - `load_config_json()`: Loads configuration from a saved JSON file
   - `get_failed_videos()`: Filters failed downloads

6. **`cli.py`** - Command-line interface
   - `parse_args()`: Parses command-line arguments
   - `main()`: Entry point for CLI
   - `run_download()`: Executes download command

## Data Flow

```
Input Source (txt/csv/hf)
    ↓
Parser (parsers.py)
    ↓
List[VideoSource]
    ↓
Downloader (downloader.py)
    ↓
List[DownloadResult]
    ↓
Metadata (metadata.py)
    ↓
CSV/JSON files
```

## Key Design Decisions

### 1. Source-Agnostic Design

The package is designed to work with any input source. Parsers convert different formats into a common `VideoSource` model, which the downloader consumes. This makes it easy to add new input sources (e.g., JSON, database) without changing the download logic.

### 2. URL Handling

URLs are normalized early in the pipeline with flexible column support:
- If only URL column is provided: video IDs are extracted from URLs
- If only ID column is provided: URLs are built from video IDs
- If both columns are provided: URLs are preferred (IDs extracted from URLs)
- This ensures consistency: the video_id is always the canonical identifier

### 3. Platform Detection

Platform is detected automatically when possible:
- From URL format (YouTube vs Vimeo)
- From ID pattern (11-char alphanumeric = YouTube, numeric = Vimeo)
- Falls back to user-specified platform

### 4. Error Handling

Failed downloads are tracked with error reasons, allowing users to:
- Retry failed downloads
- Analyze failure patterns
- Debug issues

## Development Setup

### 1. Clone and Install

```bash
git clone https://github.com/yourusername/clipyard.git
cd clipyard
pip install -e ".[dev]"
```

### 2. Run Tests

```bash
pytest tests/
```

Run with coverage:

```bash
pytest tests/ --cov=src/clipyard --cov-report=html
```

### 3. Code Quality

The codebase uses:
- Type hints throughout
- Dataclasses for structured data
- Clear function docstrings

## Adding a New Feature

### Example: Adding a New Input Source

Let's say you want to add support for JSON input files:

1. **Add parser function** in `parsers.py`:

```python
def parse_json_file(
    filepath: Path,
    id_key: str = "video_id",
    url_key: str | None = None,
    platform: Literal["youtube", "vimeo"] = "youtube"
) -> list[VideoSource]:
    """Parse a JSON file with video data."""
    import json
    
    with open(filepath, "r") as f:
        data = json.load(f)
    
    sources = []
    for item in data:
        # Use _parse_dataframe_row logic or implement similar
        # ...
    
    return sources
```

2. **Export in `__init__.py`**:

```python
from clipyard.parsers import parse_json_file

__all__ = [
    # ... existing exports
    "parse_json_file",
]
```

3. **Add CLI support** in `cli.py`:

```python
# In parse_args(), add to choices:
choices=["txt", "csv", "huggingface", "json"]

# Add JSON-specific arguments
download_parser.add_argument(
    "--id-key",
    type=str,
    default="video_id",
    help="JSON key for video IDs"
)

# In load_video_sources(), add:
elif args.input_type == "json":
    return parse_json_file(
        Path(args.input),
        id_key=args.id_key,
        url_key=args.url_key,
        platform=platform
    )
```

4. **Add tests** in `tests/test_parsers.py`:

```python
class TestParseJsonFile:
    def test_parse_json_with_ids(self):
        # Test implementation
        pass
```

### Example: Adding a New Platform

1. **Update `models.py`**:

```python
platform: Literal["youtube", "vimeo", "dailymotion"]
```

2. **Add URL patterns** in `url_utils.py`:

```python
# Add extraction logic for dailymotion.com URLs
# Add build_video_url() support
# Add detect_platform_from_id() pattern
```

3. **Update tests** in `tests/test_url_utils.py`

## Testing Strategy

### Unit Tests

Each module has corresponding tests:
- `test_url_utils.py`: Tests URL parsing edge cases (query params, fragments, etc.)
- `test_parsers.py`: Tests all input formats and edge cases

### Test Structure

Tests use pytest and follow this pattern:

```python
class TestFunctionName:
    """Tests for function_name function."""
    
    def test_basic_case(self):
        """Test basic functionality."""
        # Arrange
        # Act
        # Assert
```

### Running Specific Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_url_utils.py

# Run specific test class
pytest tests/test_url_utils.py::TestExtractVideoId

# Run specific test
pytest tests/test_url_utils.py::TestExtractVideoId::test_youtube_watch_url
```

## Code Style

- **Type hints**: All functions should have type hints
- **Docstrings**: All public functions should have docstrings
- **Naming**: Use descriptive names, follow PEP 8
- **Imports**: Group imports (stdlib, third-party, local)

Example:

```python
"""Module docstring."""

from pathlib import Path
from typing import Literal

import pandas as pd

from clipyard.models import VideoSource
```

## Common Patterns

### 1. Parsing DataFrame Rows

Use the shared `_parse_dataframe_row()` helper. Both `id_column` and `url_column` are optional, but at least one must be provided:

```python
for _, row in df.iterrows():
    source = _parse_dataframe_row(row, id_column, url_column, platform)
    if source is not None:
        sources.append(source)
```

The function handles three scenarios:
- Only URL column: extracts ID from URL
- Only ID column: builds URL from ID
- Both columns: prefers URL (extracts ID from URL)

### 2. Handling Optional Paths

```python
metadata_dir = Path(args.metadata_dir) if args.metadata_dir else None
if metadata_dir:
    metadata_dir.mkdir(parents=True, exist_ok=True)
```

### 3. Relaunching from Config

When a download is run with `--metadata-dir`, a `download_config.json` file is saved. You can relaunch the same download using the `--config` flag:

```bash
clipyard download --config ./metadata/download_config.json
```

The config file contains both the download configuration and the original CLI arguments, allowing you to resume or re-run a download with the same settings. CLI arguments can override config file values:

```bash
# Relaunch but with more workers
clipyard download --config ./metadata/download_config.json --workers 8
```

### 4. Error Extraction

Error extraction from yt-dlp output is handled in `_extract_error_reason()` in `downloader.py`. It looks for common error patterns in stderr.

## Debugging

### Enable Verbose Output

The downloader uses `tqdm` for progress bars. For debugging, you can:

1. Add print statements (temporary)
2. Use Python debugger: `import pdb; pdb.set_trace()`
3. Check metadata files for error reasons

### Common Issues

1. **URL parsing fails**: Check `url_utils.py` - may need to add new URL format
2. **Download fails silently**: Check `--silence-errors` flag and error extraction logic
3. **Platform detection wrong**: Check ID patterns in `detect_platform_from_id()`

## Contributing Workflow

1. **Create a branch**: `git checkout -b feature/your-feature`
2. **Make changes**: Follow code style and add tests
3. **Run tests**: `pytest tests/`
4. **Update docs**: Update README.md if user-facing
5. **Submit PR**: Include description of changes and test results

## Future Improvements

Potential areas for contribution:

- [ ] Support for more platforms (Dailymotion, etc.)
- [ ] Support for more input formats (JSON, database, etc.)
- [ ] Resume interrupted downloads
- [ ] Download quality selection (best, worst, specific codec)
- [ ] Progress persistence across restarts
- [ ] Rate limiting for API-friendly downloads
- [ ] Video metadata extraction (title, duration, etc.)

## Questions?

If you have questions about the codebase:
1. Check the relevant module's docstrings
2. Look at existing tests for usage examples
3. Review the data flow diagram above
4. Open an issue for discussion

Happy coding!

