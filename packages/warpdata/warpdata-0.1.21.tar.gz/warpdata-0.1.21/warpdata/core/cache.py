"""
Local caching layer for remote resources.

Provides transparent caching of remote files with validation.
"""
import json
import shutil
from pathlib import Path
from typing import Optional, Dict, Any
import tempfile

from .config import get_config
from .utils import compute_file_hash, ensure_dir
from .uris import parse_uri, URI
from ..io.fsspec_fs import get_filesystem


class Cache:
    """
    Manages local caching of remote resources.
    """

    def __init__(self, cache_dir: Optional[Path] = None):
        """
        Initialize cache.

        Args:
            cache_dir: Cache directory (uses config if not provided)
        """
        if cache_dir is None:
            cache_dir = get_config().cache_dir

        self.cache_dir = ensure_dir(cache_dir)
        self.files_dir = ensure_dir(self.cache_dir / "files")
        self.datasets_dir = ensure_dir(self.cache_dir / "datasets")
        self.metadata_dir = ensure_dir(self.cache_dir / "metadata")

    def _get_cache_key(self, uri: str) -> str:
        """
        Generate a cache key for a URI.

        Args:
            uri: URI string

        Returns:
            Cache key (hash of the URI)
        """
        from .utils import compute_hash

        return compute_hash(uri)[:16]

    def _get_cache_path(self, uri: str) -> Path:
        """
        Get the cache path for a URI.

        Args:
            uri: URI string

        Returns:
            Path to cached file
        """
        cache_key = self._get_cache_key(uri)
        return self.files_dir / cache_key

    def _get_metadata_path(self, uri: str) -> Path:
        """
        Get the metadata file path for a cached resource.

        Args:
            uri: URI string

        Returns:
            Path to metadata file
        """
        cache_key = self._get_cache_key(uri)
        return self.metadata_dir / f"{cache_key}.json"

    def _load_metadata(self, uri: str) -> Optional[Dict[str, Any]]:
        """
        Load metadata for a cached resource.

        Args:
            uri: URI string

        Returns:
            Metadata dictionary, or None if not cached
        """
        metadata_path = self._get_metadata_path(uri)

        if not metadata_path.exists():
            return None

        try:
            with open(metadata_path, "r") as f:
                return json.load(f)
        except Exception:
            return None

    def _save_metadata(self, uri: str, metadata: Dict[str, Any]):
        """
        Save metadata for a cached resource.

        Args:
            uri: URI string
            metadata: Metadata to save
        """
        metadata_path = self._get_metadata_path(uri)
        metadata_path.parent.mkdir(parents=True, exist_ok=True)

        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

    def _is_valid(
        self,
        uri: str,
        cached_path: Path,
        skip_remote_check: bool = True,
        expected_size: Optional[int] = None,
        expected_hash: Optional[str] = None,
        verify_hash: bool = False,
    ) -> bool:
        """
        Check if a cached resource is still valid.

        Args:
            uri: URI string
            cached_path: Path to cached file
            skip_remote_check: If True, skip slow remote HEAD requests (default: True)
                              Set to False to validate against remote ETags/sizes
            expected_size: Expected file size from manifest (faster than remote check)
            expected_hash: Expected SHA256 hash from manifest (for verification)
            verify_hash: If True, verify hash even if size matches (slow but thorough)

        Returns:
            True if valid, False otherwise
        """
        if not cached_path.exists():
            return False

        # Load cached metadata
        metadata = self._load_metadata(uri)
        if metadata is None:
            return False

        # Fast path 1: Check against expected size from manifest (no remote call)
        if expected_size is not None:
            local_size = cached_path.stat().st_size
            if local_size != expected_size:
                return False
            # Size matches - optionally verify hash
            if verify_hash and expected_hash:
                from .storage import compute_content_hash
                actual_hash = compute_content_hash(cached_path)
                return actual_hash == expected_hash
            return True

        # Fast path 2: if file exists and has matching size in metadata, trust it
        # This avoids slow HEAD requests to S3 for every file
        if skip_remote_check:
            if "size" in metadata:
                local_size = cached_path.stat().st_size
                return local_size == metadata["size"]
            # No size in metadata, but file exists - trust it
            return True

        # Slow path: validate against remote (only when skip_remote_check=False)
        try:
            fs = get_filesystem(uri)
            current_etag = fs.get_etag(uri)

            # If we have ETags, compare them
            if current_etag and "etag" in metadata:
                return current_etag == metadata["etag"]

            # Otherwise, compare file sizes
            remote_info = fs.info(uri)
            if "size" in remote_info and "size" in metadata:
                return remote_info["size"] == metadata["size"]

        except Exception:
            # If we can't validate, assume it's still valid
            # (better than re-downloading unnecessarily)
            return True

        return True

    def get(self, uri: str, force_refresh: bool = False) -> Path:
        """
        Get a resource from cache, downloading if necessary.

        Args:
            uri: URI string
            force_refresh: Force re-download even if cached

        Returns:
            Path to cached file
        """
        parsed_uri = parse_uri(uri)

        # Local files don't need caching
        if parsed_uri.is_local:
            local_path = Path(parsed_uri.path)
            if not local_path.exists():
                raise FileNotFoundError(f"Local file not found: {local_path}")
            return local_path

        # Check cache
        cache_path = self._get_cache_path(uri)

        if not force_refresh and self._is_valid(uri, cache_path):
            return cache_path

        # Check if file exists but metadata is missing (already downloaded)
        if cache_path.exists() and not force_refresh:
            # File exists but validation failed - likely missing metadata
            # Trust the file and recreate metadata
            metadata = self._load_metadata(uri)
            if metadata is None:
                file_size = cache_path.stat().st_size
                self._save_metadata(uri, {
                    "uri": uri,
                    "size": file_size,
                    "type": "file",
                })
                return cache_path

        # Download to cache
        return self._download(uri, cache_path)

    def _download(self, uri: str, cache_path: Path) -> Path:
        """
        Download a remote resource to cache.

        Args:
            uri: URI string
            cache_path: Path to cache file

        Returns:
            Path to cached file
        """
        # Download to temporary file first (atomic write)
        with tempfile.NamedTemporaryFile(delete=False, dir=cache_path.parent) as tmp_file:
            tmp_path = Path(tmp_file.name)

        try:
            # Use boto3 directly for S3 (faster and more reliable than fsspec)
            if uri.startswith("s3://"):
                self._download_s3(uri, tmp_path)
                # Get metadata from boto3
                import boto3
                s3 = boto3.client('s3')
                bucket, key = uri[5:].split("/", 1)
                head = s3.head_object(Bucket=bucket, Key=key)
                metadata = {
                    "uri": uri,
                    "etag": head.get("ETag", "").strip('"'),
                    "size": head.get("ContentLength"),
                    "type": "file",
                }
            else:
                # Use fsspec for non-S3 URIs
                fs = get_filesystem(uri)
                fs.copy_to_local(uri, tmp_path)
                etag = fs.get_etag(uri)
                info = fs.info(uri)
                metadata = {
                    "uri": uri,
                    "etag": etag,
                    "size": info.get("size"),
                    "type": info.get("type"),
                }

            # Move temp file to final location
            tmp_path.replace(cache_path)

            # Save metadata
            self._save_metadata(uri, metadata)

            return cache_path

        except Exception as e:
            # Clean up temp file on error
            if tmp_path.exists():
                tmp_path.unlink()
            raise

    def _download_s3(self, uri: str, local_path: Path) -> None:
        """
        Download from S3 using boto3 with progress bar.

        Much faster and more reliable than fsspec for large files.
        """
        import boto3
        from tqdm import tqdm

        # Parse S3 URI
        bucket, key = uri[5:].split("/", 1)

        s3 = boto3.client('s3')

        # Get file size for progress bar
        head = s3.head_object(Bucket=bucket, Key=key)
        file_size = head['ContentLength']

        # Download with progress
        with tqdm(total=file_size, unit='B', unit_scale=True, unit_divisor=1024,
                  desc=f"    ↓ {key.split('/')[-1][:16]}", leave=False) as pbar:
            def progress_callback(bytes_transferred):
                pbar.update(bytes_transferred)

            s3.download_file(
                bucket, key, str(local_path),
                Callback=progress_callback
            )

    def clear(self):
        """Clear the entire cache."""
        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir)
            ensure_dir(self.cache_dir)
            ensure_dir(self.files_dir)
            ensure_dir(self.datasets_dir)
            ensure_dir(self.metadata_dir)

    def get_dataset_cache_dir(self, workspace: str, name: str, version: str) -> Path:
        """
        Get cache directory for a specific dataset version.

        Args:
            workspace: Workspace name
            name: Dataset name
            version: Dataset version

        Returns:
            Path to dataset cache directory
        """
        dataset_dir = self.datasets_dir / workspace / name / version
        return ensure_dir(dataset_dir)


# Global cache instance
_global_cache: Optional[Cache] = None


def get_cache() -> Cache:
    """
    Get the global cache instance.

    Returns:
        Cache instance
    """
    global _global_cache

    if _global_cache is None:
        _global_cache = Cache()

    return _global_cache


def reset_cache():
    """Reset the global cache (useful for testing)."""
    global _global_cache
    _global_cache = None
