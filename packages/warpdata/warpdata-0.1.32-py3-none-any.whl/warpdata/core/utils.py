"""
Utility functions for warpdata.
"""
import hashlib
import os
from pathlib import Path
from typing import Union, Optional


def expand_path(path: Union[str, Path]) -> Path:
    """
    Expand a path with user home directory and environment variables.

    Args:
        path: Path to expand

    Returns:
        Expanded Path object
    """
    path_str = str(path)
    expanded = os.path.expanduser(os.path.expandvars(path_str))
    return Path(expanded).resolve()


def get_warpdata_home() -> Path:
    """
    Get the warpdata home directory.

    Checks in order:
    1. WARPDATA_HOME environment variable
    2. Default: ~/.warpdata

    Returns:
        Path to warpdata home directory
    """
    home_env = os.getenv("WARPDATA_HOME")
    if home_env:
        return expand_path(home_env)

    return expand_path("~/.warpdata")


def ensure_dir(path: Path) -> Path:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        path: Directory path to ensure

    Returns:
        The path (for chaining)
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


def compute_hash(data: Union[str, bytes], algorithm: str = "sha1") -> str:
    """
    Compute a hash of the given data.

    Args:
        data: Data to hash (string or bytes)
        algorithm: Hash algorithm to use (default: sha1)

    Returns:
        Hexadecimal hash string
    """
    if isinstance(data, str):
        data = data.encode("utf-8")

    hasher = hashlib.new(algorithm)
    hasher.update(data)
    return hasher.hexdigest()


def compute_file_hash(file_path: Path, algorithm: str = "sha1", chunk_size: int = 8192) -> str:
    """
    Compute hash of a file's contents.

    Args:
        file_path: Path to file
        algorithm: Hash algorithm to use
        chunk_size: Size of chunks to read

    Returns:
        Hexadecimal hash string
    """
    hasher = hashlib.new(algorithm)

    with open(file_path, "rb") as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)

    return hasher.hexdigest()


def safe_filename(name: str) -> str:
    """
    Convert a string to a safe filename.

    Args:
        name: String to convert

    Returns:
        Safe filename string
    """
    # Replace unsafe characters with underscores
    unsafe_chars = '<>:"/\\|?*'
    safe_name = name
    for char in unsafe_chars:
        safe_name = safe_name.replace(char, "_")

    return safe_name
