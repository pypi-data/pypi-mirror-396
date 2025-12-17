# clipyard

A lightweight wrapper around `yt-dlp` that aims to make downloading large video datasets easier and faster through a simple CLI

## Features

- **Multiple Input Sources**: Support for text files, CSV files, and HuggingFace datasets. For files, you can provide the actual file or a publicly accesible URL
- **Input Types**: Either provide a list of IDs and the platform (typically YouTube/Vimdeo, or a list of URLs)
- **Parallel Downloads**: Configurable parallel workers for fast batch downloads
- **Metadata Tracking**: Saves download summaries and failure reasons to quickly inspect download summaries, and easy re-launching of runs
- **Good Defaults**: Takes the pain out of configuring `yt-dlp` by putting good defaults in place. Videos are downloaded in h264, and m4a codecs (typically does not require re-encoding). This has two benefits: fast decoding, and ability to preview files quickly using the filesystem

PS: This library is in early development, and is an evolution of [this script](https://github.com/ridouaneg/sf20k/blob/45202b402135d3a8b96d74b54cb7892608d377d9/scripts/download_videos.py)

## Installation

```bash
pip install clipyard
pip install clipyard[datasets]  # For HuggingFace dataset support

clipyard -h
clipyard download -h
```

Or, if you use `uv` (recommended):

```bash
uv tool install clipyard[datasets]
uv tool run clipyard download -h
```


## Examples (w/ Best Practices)

Refer to [this doc to setup cookies for downloading](./docs/cookies-setup.md).
Note that some of these args presented here are not mandatory, but are the suggested way to use this tool for best quality of life.

### SF20K Dataset (Text File)

This cmd downloads `test_expert` split of the [SF20K](https://huggingface.co/datasets/rghermi/sf20k) dataset, in 720p. Note

```bash
uv tool run clipyard download \
  --input-type huggingface \
  --hf-dataset "rghermi/sf20k" \
  --hf-split test_expert \
  --id-column video_id \
  --url-column video_url \
  --output-dir /mnt/DataSSD/datasets/sf20k/test_expert/720p/ \
  --metadata-dir /mnt/DataSSD/datasets/sf20k/test_expert/metadata/ \
  --cookies cookies.txt
```

### VUE-TR-V2 Dataset (HuggingFace)

```bash
uv tool run clipyard download \
  --input-type txt \
  --input "https://raw.githubusercontent.com/bytedance/vidi/refs/heads/main/VUE_TR_V2/video_id.txt" \
  --output-dir /mnt/DataSSD/datasets/vue-tr-v2/videos/ \
  --metadata-dir /mnt/DataSSD/datasets/vue-tr-v2/metadata/ \
  --cookies cookies.txt

uv tool run clipyard download \
  --input-type txt \
  --input "https://raw.githubusercontent.com/bytedance/vidi/refs/heads/main/VUE_TR/video_id.txt" \
  --output-dir /mnt/DataSSD/datasets/vue-tr-v2/videos/ \
  --metadata-dir /mnt/DataSSD/datasets/vue-tr-v2/metadata-v1/ \
  --cookies cookies.txt
```

---

## Re-Launching Runs

If you ran a download with `--metadata-dir`, a `download_config.json` file is saved. You can relaunch the same download with:

```bash
clipyard download --config ./metadata/download_config.json
```

You can also override specific settings:

```bash
clipyard download --config ./metadata/download_config.json --workers 8  # More workers
clipyard download --config ./metadata/download_config.json --output-dir ./new-downloads  # Different output dir
```


## Command-Line Arguments

### Required Arguments

- `--input-type`: Type of input source (required unless `--config` is provided)
  - Options: `txt`, `csv`, `huggingface`
  
- `--output-dir`: Directory to save downloaded videos (required unless `--config` is provided)

### Config File

- `--config`: Path to a saved config JSON file (from a previous run's `--metadata-dir`)
  - When provided, loads settings from the config file
  - CLI arguments can override config file values
  - Allows relaunching a download with the same settings

### Input Arguments

- `--input`: Input file path (for `txt`/`csv`) or dataset name (for `huggingface`)
- `--platform`: Default platform for video IDs when not specified in URLs
  - Options: `youtube`, `vimeo`
  - Default: `youtube`
- `--id-column`: Column name containing video IDs
  - Default: `video_id`
  - At least one of `--id-column` or `--url-column` must be provided
- `--url-column`: Column name containing video URLs (optional)
  - If only URL column is provided: video IDs are extracted from URLs
  - If only ID column is provided: URLs are built from video IDs
  - If both are provided: URLs are preferred (IDs extracted from URLs)
- `--hf-dataset`: HuggingFace dataset identifier (e.g., `"rghermi/sf20k"`)
- `--hf-split`: HuggingFace dataset split to use
  - Default: `train`

### Output Arguments

- `--metadata-dir`: Directory to save download metadata
  - Creates three files:
    - `download_summary.csv`: All download results (success, failed, skipped)
    - `failed_videos.csv`: Only failed downloads (for retry)
    - `download_config.json`: Configuration for re-running the download

### Download Arguments

- `--resolution`: Video resolution to download
  - Options: `144`, `240`, `360`, `480`, `720`, `1080`
  - Default: `720`
- `--workers`: Number of parallel workers for downloading videos
  - Default: `4`
  - Recommended: 4-8 for faster downloads
- `--threads`: Number of threads per download (passed to yt-dlp `--concurrent-fragments`)
  - Default: `1`
  - Recommended: 2-4 for faster individual downloads
- `--max-videos`: Maximum number of videos to download (useful for testing)
  - If not specified, downloads all videos
- `--cookies`: Path to cookies file (.txt) for yt-dlp
  - Required for some restricted/private videos
- `--replace-existing`: Replace videos if they've already been downloaded previously
- `--silence-errors`: Silence yt-dlp errors and warnings
- `--sleep-interval`: Number of seconds to sleep before each download (passed to yt-dlp)
  - Default: `5`
- `--max-sleep-interval`: Maximum number of seconds to sleep before each download (passed to yt-dlp)
  - Default: `10`

## Input Formats

**Text files**: One video ID or URL per line. Empty lines and lines starting with `#` are ignored.

**CSV files**: At least one of the following must be provided:
- Video ID column (default: `video_id`): IDs are used to construct URLs
- Video URL column: IDs are extracted from URLs
- Both columns: URLs are preferred (IDs extracted from URLs)

**HuggingFace datasets**: Specify dataset name and split. At least one of the following must be provided:
- Video ID column (default: `video_id`): IDs are used to construct URLs
- Video URL column: IDs are extracted from URLs
- Both columns: URLs are preferred (IDs extracted from URLs)

## Python API

You can also use clipyard programmatically:

```python
from clipyard import (
    parse_txt_file,
    download_videos,
    DownloadConfig,
    save_summary_csv,
)
from pathlib import Path

# Parse input
sources = parse_txt_file(Path("videos.txt"), platform="youtube")

# Configure download
config = DownloadConfig(
    output_dir=Path("./downloads"),
    resolution=1080,
    workers=4,
    threads=2,
)

# Download
results = download_videos(sources, config)

# Save summary
save_summary_csv(results, Path("summary.csv"))
```

## Context For LLMs

Use [development.md](./docs/development.md) for developer documentation, tailored for LLM use.
