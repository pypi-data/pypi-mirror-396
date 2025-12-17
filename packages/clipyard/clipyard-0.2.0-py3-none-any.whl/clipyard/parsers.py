"""Input parsers for different data sources."""

from pathlib import Path

import pandas as pd

try:
    from datasets import load_dataset
except ImportError:
    load_dataset = None

from clipyard.models import VideoSource
from clipyard.url_utils import (
    build_video_url,
    detect_platform_from_id,
    extract_video_id,
)


def _parse_dataframe_row(
    row: pd.Series,
    id_column: str | None,
    url_column: str | None,
    platform: str | None = None,
) -> VideoSource | None:
    """
    Parse a single row from a pandas DataFrame into a VideoSource.

    This is a shared helper function used by both CSV and HuggingFace parsers.

    Behavior:
    - If only URL column is provided: extract ID from URL
    - If only ID column is provided: construct URL from ID
    - If both are provided: prefer URL (extract ID from URL)

    Args:
        row: Pandas Series representing a single row
        id_column: Optional name of the column containing video IDs
        url_column: Optional name of the column containing video URLs
        platform: Default platform if needed for URL construction

    Returns:
        VideoSource object or None if row should be skipped
    """
    video_id: str | None = None
    video_url: str | None = None
    detected_platform: str | None = platform

    # Check URL column first (preferred if both are provided)
    if url_column and url_column in row.index:
        url_value = row[url_column]
        if not pd.isna(url_value):
            url_value = str(url_value).strip()
            if url_value:
                if url_value.startswith("http"):
                    # Extract ID & Platform from URL
                    extracted_id, detected_platform = extract_video_id(url_value)
                    video_id = extracted_id
                    video_url = url_value
                else:
                    # URL column contains ID, not URL
                    video_id = url_value
                    try:
                        detected_platform = detect_platform_from_id(video_id)
                    except ValueError:
                        detected_platform = platform
                    video_url = build_video_url(video_id, detected_platform)

    # If we don't have a video_id yet, try ID column
    if video_id is None:
        if id_column and id_column in row.index:
            id_value = row[id_column]
            if not pd.isna(id_value):
                id_value = str(id_value).strip()
                if id_value:
                    video_id = id_value
                    # If we already have a URL from URL column, keep it
                    if video_url is None:
                        try:
                            detected_platform = detect_platform_from_id(video_id)
                        except ValueError:
                            detected_platform = platform
                        video_url = build_video_url(video_id, detected_platform)

    # If we still don't have a video_id, we can't proceed
    if video_id is None or not video_id:
        return None

    # Ensure we have a URL
    if video_url is None:
        try:
            detected_platform = detect_platform_from_id(video_id)
        except ValueError:
            detected_platform = platform
        video_url = build_video_url(video_id, detected_platform)

    return VideoSource(
        video_id=video_id, video_url=video_url, platform=detected_platform
    )


def _validate_dataframe_columns(
    df: pd.DataFrame,
    id_column: str | None,
    url_column: str | None,
    source_name: str = "Dataset",
) -> tuple[str | None, str | None]:
    """
    Validate and adjust id_column and url_column for a DataFrame.

    This helper function ensures that:
    - At least one of id_column or url_column is provided
    - The specified columns exist in the DataFrame
    - If a specified column doesn't exist but the other does, it adjusts accordingly

    Args:
        df: The DataFrame to validate against
        id_column: Optional name of the column containing video IDs
        url_column: Optional name of the column containing video URLs
        source_name: Name of the data source for error messages (e.g., "CSV file", "Dataset")

    Returns:
        Tuple of (adjusted_id_column, adjusted_url_column)

    Raises:
        ValueError: If neither column is provided or if neither specified column exists
    """
    # At least one column must be provided
    if not id_column and not url_column:
        raise ValueError(
            f"At least one of id_column or url_column must be provided. "
            f"Found columns: {df.columns.tolist()}"
        )

    # Check that specified columns exist
    if id_column and id_column not in df.columns:
        if url_column and url_column in df.columns:
            # URL column exists, so we can proceed without ID column
            id_column = None
        else:
            raise ValueError(
                f"{source_name} must contain '{id_column}' column. "
                f"Found columns: {df.columns.tolist()}"
            )

    if url_column and url_column not in df.columns:
        if id_column and id_column in df.columns:
            # ID column exists, so we can proceed without URL column
            url_column = None
        else:
            raise ValueError(
                f"{source_name} must contain '{url_column}' column. "
                f"Found columns: {df.columns.tolist()}"
            )

    return id_column, url_column


def _dedupe_and_subset_dataframe(
    df: pd.DataFrame,
    id_column: str | None,
    url_column: str | None,
) -> pd.DataFrame:
    "Deduplicate and subset a DataFrame based on the provided columns"
    columns = [x for x in (id_column, url_column) if x]
    df = df.loc[:, columns]
    df = df.drop_duplicates()
    return df


def parse_txt_file(filepath: Path, platform: str | None = None) -> list[VideoSource]:
    """
    Parse a text file with one video ID or URL per line.

    Args:
        filepath: Path to the text file
        platform: Default platform if line contains only an ID (default: youtube)

    Returns:
        List of VideoSource objects
    """
    sources = []

    with open(filepath, encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line or line.startswith("#"):  # Skip empty lines and comments
                continue

            try:
                # Check if it looks like a URL
                if line.startswith("http"):
                    video_id, detected_platform = extract_video_id(line)
                    video_url = line
                else:
                    # Treat as bare ID
                    video_id = line
                    if platform is None:
                        detected_platform = detect_platform_from_id(video_id)
                    else:
                        detected_platform = platform
                    video_url = build_video_url(video_id, detected_platform)

                sources.append(
                    VideoSource(
                        video_id=video_id,
                        video_url=video_url,
                        platform=detected_platform,
                    )
                )
            except ValueError as e:
                print(f"Warning: Skipping line {line_num} in {filepath}: {e}")
                continue

    return sources


def parse_csv_file(
    filepath: Path,
    id_column: str | None = "video_id",
    url_column: str | None = None,
    platform: str | None = None,
) -> list[VideoSource]:
    """
    Parse a CSV file with video IDs and/or URLs.

    Behavior:
    - If only URL column is provided: extract ID from URL
    - If only ID column is provided: construct URL from ID
    - If both are provided: prefer URL (extract ID from URL)

    Args:
        filepath: Path to the CSV file
        id_column: Optional name of the column containing video IDs (default: "video_id")
        url_column: Optional name of the column containing video URLs
        platform: Default platform if needed for URL construction (default: youtube)

    Returns:
        List of VideoSource objects

    Raises:
        ValueError: If neither id_column nor url_column is provided, or if specified columns don't exist
    """
    df = pd.read_csv(filepath)

    id_column, url_column = _validate_dataframe_columns(
        df, id_column, url_column, source_name="CSV file"
    )
    df = _dedupe_and_subset_dataframe(df, id_column, url_column)

    sources = []
    for _, row in df.iterrows():
        source = _parse_dataframe_row(row, id_column, url_column, platform)
        if source is not None:
            sources.append(source)

    return sources


def parse_huggingface_dataset(
    dataset_name: str,
    split: str = "train",
    id_column: str | None = "video_id",
    url_column: str | None = None,
    platform: str | None = None,
) -> list[VideoSource]:
    """
    Parse a HuggingFace dataset.

    Behavior:
    - If only URL column is provided: extract ID from URL
    - If only ID column is provided: construct URL from ID
    - If both are provided: prefer URL (extract ID from URL)

    Args:
        dataset_name: HuggingFace dataset identifier (e.g., "rghermi/sf20k")
        split: Dataset split to use (default: "train")
        id_column: Optional name of the column containing video IDs (default: "video_id")
        url_column: Optional name of the column containing video URLs
        platform: Default platform if needed for URL construction (default: youtube)

    Returns:
        List of VideoSource objects

    Raises:
        ValueError: If neither id_column nor url_column is provided, or if specified columns don't exist
        ImportError: If the datasets package is not installed
    """
    if load_dataset is None:
        raise ImportError(
            "The 'datasets' package is required to parse HuggingFace datasets. "
            "Install it with: pip install datasets or pip install clipyard[datasets]"
        )
    dataset = load_dataset(dataset_name, split=split)
    df = dataset.to_pandas()

    id_column, url_column = _validate_dataframe_columns(
        df, id_column, url_column, source_name="Dataset"
    )
    df = _dedupe_and_subset_dataframe(df, id_column, url_column)

    sources = []

    for _, row in df.iterrows():
        source = _parse_dataframe_row(row, id_column, url_column, platform)
        if source is not None:
            sources.append(source)

    return sources
