"""
Storage backend implementations for warpdata.
"""
from typing import Optional
from pathlib import Path

from .base import StorageBackend, compute_content_hash
from .local import LocalStorage
from .s3 import S3Storage


__all__ = [
    "StorageBackend",
    "LocalStorage",
    "S3Storage",
    "get_storage_backend",
    "compute_content_hash",
]


# Global storage instance
_global_storage: Optional[StorageBackend] = None


def get_storage_backend(backend: str = "local", **config) -> StorageBackend:
    """
    Get storage backend by name.

    Args:
        backend: Backend type ('local', 's3')
        **config: Backend-specific configuration

    Returns:
        StorageBackend instance

    Examples:
        >>> # Local storage
        >>> storage = get_storage_backend("local", storage_dir=Path("~/.warpdata/storage"))

        >>> # S3 storage
        >>> storage = get_storage_backend("s3", bucket="my-warp-bucket", prefix="datasets")
    """
    if backend == "local":
        storage_dir = config.get("storage_dir")
        if storage_dir is None:
            from ..config import get_config
            storage_dir = get_config().cache_dir / "storage"
        return LocalStorage(Path(storage_dir))

    elif backend == "s3":
        bucket = config.get("bucket")
        if not bucket:
            raise ValueError("S3 backend requires 'bucket' parameter")
        prefix = config.get("prefix", "warp")
        s3_config = {k: v for k, v in config.items() if k not in ("bucket", "prefix")}
        return S3Storage(bucket, prefix, **s3_config)

    else:
        raise ValueError(f"Unknown storage backend: {backend}")


def set_global_storage(storage: StorageBackend):
    """Set the global storage instance."""
    global _global_storage
    _global_storage = storage


def get_global_storage() -> StorageBackend:
    """
    Get the global storage instance.

    Returns:
        StorageBackend instance (defaults to local storage)
    """
    global _global_storage

    if _global_storage is None:
        _global_storage = get_storage_backend("local")

    return _global_storage
