"""
Filesystem abstraction using fsspec.

Provides a unified interface for accessing files across different storage backends.
"""
import fsspec
from pathlib import Path
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse

from ..core.config import get_config
from ..core.uris import URI, parse_uri


class FileSystem:
    """
    Unified filesystem interface using fsspec.
    """

    def __init__(self, uri: Optional[URI] = None, **storage_options):
        """
        Initialize filesystem for a given URI.

        Args:
            uri: URI object (optional)
            **storage_options: Additional options for fsspec
        """
        self.uri = uri
        self.storage_options = storage_options
        self._fs: Optional[fsspec.AbstractFileSystem] = None

    def _get_fs(self, scheme: str) -> fsspec.AbstractFileSystem:
        """
        Get or create an fsspec filesystem for the given scheme.

        Args:
            scheme: URI scheme (e.g., 'file', 's3', 'http')

        Returns:
            fsspec filesystem instance
        """
        if self._fs is not None:
            return self._fs

        # Merge storage options from config
        options = dict(self.storage_options)

        config = get_config()

        # Add credentials from config based on scheme
        if scheme == "s3":
            s3_config = config.get_profile_config("s3")

            # Handle basic options (anon, key, secret, token)
            for key in ["anon", "key", "secret", "token"]:
                if key in s3_config and key not in options:
                    options[key] = s3_config[key]

            # Map config keys to fsspec keys
            if "aws_access_key_id" in s3_config and "key" not in options:
                options["key"] = s3_config["aws_access_key_id"]
            if "aws_secret_access_key" in s3_config and "secret" not in options:
                options["secret"] = s3_config["aws_secret_access_key"]

            # Handle region_name - must be passed via client_kwargs for s3fs
            if "region_name" in s3_config and "client_kwargs" not in options:
                options["client_kwargs"] = {"region_name": s3_config["region_name"]}

        elif scheme == "hf":
            hf_config = config.get_profile_config("hf")
            if "token" in hf_config and "token" not in options:
                options["token"] = hf_config["token"]

        elif scheme in ("http", "https"):
            # HTTP doesn't need special credentials in most cases
            pass

        # Create the filesystem
        self._fs = fsspec.filesystem(scheme, **options)
        return self._fs

    def open(self, path: str, mode: str = "rb", **kwargs):
        """
        Open a file for reading or writing.

        Args:
            path: File path or URL
            mode: File mode ('rb', 'wb', etc.)
            **kwargs: Additional arguments for fsspec.open

        Returns:
            File-like object
        """
        uri = parse_uri(path) if isinstance(path, str) else path
        fs = self._get_fs(uri.scheme)

        if uri.is_local:
            # For local files, use the absolute path
            file_path = uri.path
        else:
            # For remote files, use the full URL
            file_path = uri.to_fsspec_url()

        return fs.open(file_path, mode, **kwargs)

    def info(self, path: str) -> Dict[str, Any]:
        """
        Get metadata about a file.

        Args:
            path: File path or URL

        Returns:
            Dictionary with file metadata (size, type, etc.)
        """
        uri = parse_uri(path)
        fs = self._get_fs(uri.scheme)

        if uri.is_local:
            file_path = uri.path
        else:
            file_path = uri.to_fsspec_url()

        return fs.info(file_path)

    def exists(self, path: str) -> bool:
        """
        Check if a file or directory exists.

        Args:
            path: File path or URL

        Returns:
            True if exists, False otherwise
        """
        uri = parse_uri(path)
        fs = self._get_fs(uri.scheme)

        if uri.is_local:
            file_path = uri.path
        else:
            file_path = uri.to_fsspec_url()

        return fs.exists(file_path)

    def glob(self, pattern: str) -> List[str]:
        """
        Find files matching a glob pattern.

        Args:
            pattern: Glob pattern

        Returns:
            List of matching file paths
        """
        uri = parse_uri(pattern)
        fs = self._get_fs(uri.scheme)

        if uri.is_local:
            file_pattern = uri.path
        else:
            file_pattern = uri.to_fsspec_url()

        matches = fs.glob(file_pattern)

        # Convert back to full URLs for remote filesystems
        # Some fsspec implementations already return fully-qualified paths
        if not uri.is_local:
            normalized_matches = []
            for match in matches:
                # Only add scheme if match doesn't already have one
                if "://" not in match:
                    match = f"{uri.scheme}://{match}"
                normalized_matches.append(match)
            matches = normalized_matches

        return matches

    def copy_to_local(self, remote_path: str, local_path: Path) -> Path:
        """
        Copy a remote file to a local path.

        Args:
            remote_path: Remote file path or URL
            local_path: Local destination path

        Returns:
            Local path where file was saved
        """
        uri = parse_uri(remote_path)
        fs = self._get_fs(uri.scheme)

        # Ensure local directory exists
        local_path.parent.mkdir(parents=True, exist_ok=True)

        if uri.is_local:
            # For local files, just copy
            import shutil

            shutil.copy2(uri.path, local_path)
        else:
            # For remote files, download
            remote_url = uri.to_fsspec_url()
            fs.get(remote_url, str(local_path))

        return local_path

    def get_etag(self, path: str) -> Optional[str]:
        """
        Get the ETag for a remote file (if available).

        Args:
            path: File path or URL

        Returns:
            ETag string, or None if not available
        """
        try:
            info = self.info(path)
            # Try different keys where ETag might be stored
            for key in ["ETag", "etag", "version_id", "checksum"]:
                if key in info:
                    return str(info[key]).strip('"')
        except Exception:
            pass

        return None


def get_filesystem(uri: str, **storage_options) -> FileSystem:
    """
    Get a FileSystem instance for a given URI.

    Args:
        uri: URI string
        **storage_options: Additional storage options

    Returns:
        FileSystem instance
    """
    parsed_uri = parse_uri(uri)
    return FileSystem(parsed_uri, **storage_options)
