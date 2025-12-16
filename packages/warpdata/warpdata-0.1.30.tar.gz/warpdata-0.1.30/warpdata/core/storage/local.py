"""
Local filesystem storage backend.

Stores files in content-addressable layout under cache directory.
"""
from pathlib import Path
from typing import Optional, Dict, Any
import shutil
import json

from .base import StorageBackend, compute_content_hash
from ..utils import ensure_dir


class LocalStorage(StorageBackend):
    """Local filesystem storage backend."""

    def __init__(self, storage_dir: Path):
        """
        Initialize local storage.

        Args:
            storage_dir: Root directory for storage
        """
        self.storage_dir = ensure_dir(storage_dir)
        self.objects_dir = ensure_dir(storage_dir / "objects")

    def put(
        self,
        local_path: Path,
        metadata: Optional[Dict[str, Any]] = None,
        overwrite: bool = False,
    ) -> str:
        """Upload file to local storage."""
        # Compute content hash
        content_hash = compute_content_hash(local_path)

        # Get storage path
        storage_key = self._get_storage_key(content_hash)
        storage_path = self.objects_dir / storage_key

        # Skip if already exists (deduplication) unless overwrite
        if storage_path.exists() and not overwrite:
            return content_hash

        # Create parent directory
        ensure_dir(storage_path.parent)

        # Copy file
        shutil.copy2(local_path, storage_path)

        # Store metadata if provided
        if metadata:
            metadata_path = storage_path.with_suffix('.meta.json')
            metadata_path.write_text(json.dumps(metadata))

        return content_hash

    def get(
        self,
        content_hash: str,
        local_path: Path
    ):
        """Download file from local storage."""
        storage_key = self._get_storage_key(content_hash)
        storage_path = self.objects_dir / storage_key

        if not storage_path.exists():
            raise FileNotFoundError(
                f"Content hash not found in local storage: {content_hash}"
            )

        # Ensure parent directory exists
        ensure_dir(local_path.parent)

        # Copy file
        shutil.copy2(storage_path, local_path)

    def exists(
        self,
        content_hash: str
    ) -> bool:
        """Check if file exists in local storage."""
        storage_key = self._get_storage_key(content_hash)
        storage_path = self.objects_dir / storage_key
        return storage_path.exists()

    def delete(
        self,
        content_hash: str
    ):
        """Delete file from local storage."""
        storage_key = self._get_storage_key(content_hash)
        storage_path = self.objects_dir / storage_key

        if storage_path.exists():
            storage_path.unlink()

            # Delete metadata if exists
            metadata_path = storage_path.with_suffix('.meta.json')
            if metadata_path.exists():
                metadata_path.unlink()

    def get_metadata(
        self,
        content_hash: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a stored file.

        Args:
            content_hash: SHA256 hash of file

        Returns:
            Metadata dict or None if no metadata stored
        """
        storage_key = self._get_storage_key(content_hash)
        storage_path = self.objects_dir / storage_key
        metadata_path = storage_path.with_suffix('.meta.json')

        if metadata_path.exists():
            return json.loads(metadata_path.read_text())

        return None
