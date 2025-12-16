"""
Image dataset utilities for warpdata.

Provides auto-detection and helper functions for working with image datasets:
- is_image_dataset(): Check if a dataset contains image columns
- get_image_columns(): Get names of detected image columns
- decode_image(): Convert BLOB bytes to PIL Image
- load_images(): Load dataset with automatic image decoding
"""
import io
from typing import List, Dict, Any, Optional, Union, Callable

from .data import load, schema as get_schema


# Common names for image columns (case-insensitive matching)
IMAGE_COLUMN_NAMES = {
    'image', 'img', 'photo', 'picture', 'frame',
    'image_data', 'img_data', 'image_bytes', 'img_bytes',
    'thumbnail', 'preview',
}

# DuckDB types that can contain image data
IMAGE_BLOB_TYPES = {'BLOB', 'BYTEA', 'VARBINARY'}


def is_image_dataset(source: str) -> bool:
    """
    Check if a dataset contains image columns.

    Auto-detects image columns by:
    1. Looking for BLOB/binary columns with image-related names
    2. Checking column types

    Args:
        source: Dataset ID or file path

    Returns:
        True if dataset has detected image columns

    Examples:
        >>> import warpdata as wd
        >>> wd.is_image_dataset("vision/coco-embedded")
        True
        >>> wd.is_image_dataset("text/wikipedia")
        False
    """
    cols = get_image_columns(source)
    return len(cols) > 0


def get_image_columns(source: str) -> List[str]:
    """
    Get names of detected image columns in a dataset.

    Detection logic:
    1. BLOB/binary columns with names matching common image column names
    2. Columns explicitly named 'image' or 'img' regardless of type

    Args:
        source: Dataset ID or file path

    Returns:
        List of column names detected as image columns

    Examples:
        >>> import warpdata as wd
        >>> wd.get_image_columns("vision/coco-embedded")
        ['image']
    """
    ds_schema = get_schema(source)
    image_cols = []

    for col_name, col_type in ds_schema.items():
        col_lower = col_name.lower()
        type_upper = col_type.upper()

        # Check if it's a BLOB type with an image-related name
        if type_upper in IMAGE_BLOB_TYPES:
            if col_lower in IMAGE_COLUMN_NAMES or any(n in col_lower for n in IMAGE_COLUMN_NAMES):
                image_cols.append(col_name)
        # Also include if explicitly named 'image' even if not BLOB (could be path)
        elif col_lower == 'image' or col_lower == 'img':
            image_cols.append(col_name)

    return image_cols


def decode_image(data: bytes, format: str = "PIL"):
    """
    Decode image bytes to a usable image object.

    Args:
        data: Raw image bytes (JPEG, PNG, etc.)
        format: Output format - "PIL" (default), "numpy", or "bytes"

    Returns:
        PIL.Image.Image, numpy array, or bytes depending on format

    Raises:
        ImportError: If PIL/numpy not installed
        ValueError: If format not recognized or image can't be decoded

    Examples:
        >>> import warpdata as wd
        >>> df = wd.load("vision/coco-embedded", limit=1, as_format="pandas")
        >>> img = wd.decode_image(df['image'].iloc[0])
        >>> img.size
        (640, 480)
    """
    if data is None:
        return None

    if format == "bytes":
        return data

    if format == "PIL":
        try:
            from PIL import Image
        except ImportError:
            raise ImportError("PIL/Pillow is required for image decoding. Install with: pip install Pillow")

        return Image.open(io.BytesIO(data))

    elif format == "numpy":
        try:
            from PIL import Image
            import numpy as np
        except ImportError as e:
            raise ImportError(f"PIL and numpy required for numpy format: {e}")

        img = Image.open(io.BytesIO(data))
        return np.array(img)

    else:
        raise ValueError(f"Unknown format: {format}. Supported: 'PIL', 'numpy', 'bytes'")


def decode_images_column(df, column: str = "image", format: str = "PIL", inplace: bool = False):
    """
    Decode all images in a DataFrame column.

    Args:
        df: pandas DataFrame with image bytes column
        column: Name of column containing image bytes
        format: Output format - "PIL" or "numpy"
        inplace: If True, modify DataFrame in place; otherwise return new DataFrame

    Returns:
        DataFrame with decoded images (or None if inplace=True)

    Examples:
        >>> import warpdata as wd
        >>> df = wd.load("vision/coco-embedded", limit=10, as_format="pandas")
        >>> df = wd.decode_images_column(df, "image")
        >>> df['image'].iloc[0]  # Now a PIL Image
        <PIL.JpegImagePlugin.JpegImageFile ...>
    """
    if not inplace:
        df = df.copy()

    df[column] = df[column].apply(lambda x: decode_image(x, format) if x is not None else None)

    if not inplace:
        return df


def load_images(
    source: str,
    decode: bool = True,
    image_format: str = "PIL",
    limit: Optional[int] = None,
    columns: Optional[List[str]] = None,
    **options
):
    """
    Load an image dataset with automatic image decoding.

    This is a convenience wrapper around load() that:
    1. Auto-detects image columns
    2. Optionally decodes BLOB bytes to PIL Images
    3. Returns a pandas DataFrame (images don't work well with DuckDB relations)

    Args:
        source: Dataset ID or file path
        decode: If True, decode image bytes to PIL Images
        image_format: Format for decoded images - "PIL" or "numpy"
        limit: Optional row limit
        columns: Optional list of columns to select (image columns auto-included)
        **options: Additional options passed to load()

    Returns:
        pandas DataFrame with image data

    Examples:
        >>> import warpdata as wd
        >>> df = wd.load_images("vision/coco-embedded", limit=10)
        >>> df['image'].iloc[0].show()  # Display first image

        >>> # Load specific columns plus images
        >>> df = wd.load_images("vision/coco-embedded", columns=["file_name", "first_caption"])
    """
    # Always load as pandas for image handling
    df = load(source, as_format="pandas", limit=limit, **options)

    # Filter columns if specified
    if columns:
        image_cols = get_image_columns(source)
        # Ensure image columns are included
        all_cols = list(columns) + [c for c in image_cols if c not in columns]
        # Only keep columns that exist
        existing_cols = [c for c in all_cols if c in df.columns]
        df = df[existing_cols]

    # Decode images if requested
    if decode:
        image_cols = get_image_columns(source)
        for col in image_cols:
            if col in df.columns:
                df = decode_images_column(df, col, format=image_format)

    return df


def image_dataset_info(source: str) -> Dict[str, Any]:
    """
    Get information about image columns in a dataset.

    Args:
        source: Dataset ID or file path

    Returns:
        Dictionary with image dataset details

    Examples:
        >>> import warpdata as wd
        >>> info = wd.image_dataset_info("vision/coco-embedded")
        >>> print(info)
        {'is_image_dataset': True, 'image_columns': ['image'], ...}
    """
    ds_schema = get_schema(source)
    image_cols = get_image_columns(source)

    return {
        "is_image_dataset": len(image_cols) > 0,
        "image_columns": image_cols,
        "all_columns": list(ds_schema.keys()),
        "schema": ds_schema,
    }
