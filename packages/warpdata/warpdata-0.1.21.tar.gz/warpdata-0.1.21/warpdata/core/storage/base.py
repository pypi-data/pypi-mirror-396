"""
Abstract storage backend interface for warpdata.

Provides content-addressable storage with support for:
- Local filesystem
- S3
- Future: GCS, Azure Blob, etc.
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Dict, Any
import hashlib


def compute_content_hash(file_path: Path) -> str:
    """
    Compute SHA256 hash of file contents.

    Args:
        file_path: Path to file

    Returns:
        Hex digest of SHA256 hash
    """
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()


class StorageBackend(ABC):
    """Abstract storage backend interface."""

    @abstractmethod
    def put(
        self,
        local_path: Path,
        metadata: Optional[Dict[str, Any]] = None,
        overwrite: bool = False,
    ) -> str:
        """
        Upload file to storage.

        Args:
            local_path: Path to local file
            metadata: Optional metadata to store with file
            overwrite: If True, always (re)upload even if object exists

        Returns:
            Content hash (SHA256) of uploaded file
        """
        pass

    @abstractmethod
    def get(
        self,
        content_hash: str,
        local_path: Path
    ):
        """
        Download file from storage by content hash.

        Args:
            content_hash: SHA256 hash of file
            local_path: Where to save downloaded file
        """
        pass

    @abstractmethod
    def exists(
        self,
        content_hash: str
    ) -> bool:
        """
        Check if file exists in storage.

        Args:
            content_hash: SHA256 hash of file

        Returns:
            True if file exists
        """
        pass

    @abstractmethod
    def delete(
        self,
        content_hash: str
    ):
        """
        Delete file from storage.

        Args:
            content_hash: SHA256 hash of file
        """
        pass

    def _get_storage_key(self, content_hash: str) -> str:
        """
        Get storage key from content hash.

        Uses content-addressable layout: ab/cd/abcd1234...

        Args:
            content_hash: SHA256 hash

        Returns:
            Storage key
        """
        return f"{content_hash[:2]}/{content_hash[2:4]}/{content_hash}"
