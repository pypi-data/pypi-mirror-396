"""
S3 storage backend.

Stores files in S3 with content-addressable layout.
"""
from pathlib import Path
from typing import Optional, Dict, Any, List
import json

from .base import StorageBackend, compute_content_hash
from ..utils import ensure_dir


class S3Storage(StorageBackend):
    """S3 storage backend."""

    def __init__(
        self,
        bucket: str,
        prefix: str = "",
        **s3_config
    ):
        """
        Initialize S3 storage.

        Args:
            bucket: S3 bucket name
            prefix: Key prefix for all objects (default: '' - no prefix)
                   Note: Bucket name already contains 'warpbucket-' prefix
            **s3_config: Additional boto3 client config
        """
        try:
            import boto3
        except ImportError:
            raise ImportError(
                "boto3 is required for S3 storage. "
                "Install with: pip install boto3"
            )

        # Filter out warpdata-specific config keys that boto3 doesn't understand
        # Only pass valid boto3 client parameters
        boto3_params = {}
        valid_boto3_keys = {'region_name', 'aws_access_key_id', 'aws_secret_access_key',
                            'aws_session_token', 'endpoint_url', 'verify', 'config'}
        for key, value in s3_config.items():
            if key in valid_boto3_keys:
                boto3_params[key] = value

        self.s3 = boto3.client('s3', **boto3_params)
        self.bucket = bucket
        self.prefix = prefix

        # Build base path (handle empty prefix)
        if prefix:
            self.base_path = f"{prefix}/objects"
        else:
            self.base_path = "objects"

    def put(
        self,
        local_path: Path,
        metadata: Optional[Dict[str, Any]] = None,
        overwrite: bool = False,
        show_progress: bool = False,
    ) -> str:
        """Upload file to S3."""
        # Compute content hash
        content_hash = compute_content_hash(local_path)

        # Get S3 key
        storage_key = self._get_storage_key(content_hash)
        s3_key = f"{self.base_path}/{storage_key}"

        # Skip if already exists (deduplication) unless overwrite
        if self._exists_in_s3(s3_key) and not overwrite:
            return content_hash

        # Prepare extra args
        extra_args = {}
        if metadata:
            # S3 metadata keys must be lowercase and alphanumeric
            s3_metadata = {
                k.lower().replace('-', '_'): str(v)
                for k, v in metadata.items()
            }
            extra_args['Metadata'] = s3_metadata

        # Get file size for progress
        file_size = local_path.stat().st_size

        # Upload file with optional progress bar
        if show_progress and file_size > 1_000_000:  # Show progress for files > 1MB
            from tqdm import tqdm

            with tqdm(
                total=file_size,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
                desc=f"    ↑ {local_path.name}",
                leave=False,
                bar_format='{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{rate_fmt}]'
            ) as pbar:
                def progress_callback(bytes_transferred):
                    pbar.update(bytes_transferred)

                self.s3.upload_file(
                    str(local_path),
                    self.bucket,
                    s3_key,
                    ExtraArgs=extra_args,
                    Callback=progress_callback
                )
        else:
            self.s3.upload_file(
                str(local_path),
                self.bucket,
                s3_key,
                ExtraArgs=extra_args
            )

        return content_hash

    def get(
        self,
        content_hash: str,
        local_path: Path
    ):
        """Download file from S3."""
        storage_key = self._get_storage_key(content_hash)
        s3_key = f"{self.base_path}/{storage_key}"

        # Ensure parent directory exists
        ensure_dir(local_path.parent)

        # Download file
        try:
            self.s3.download_file(
                self.bucket,
                s3_key,
                str(local_path)
            )
        except Exception as e:
            raise FileNotFoundError(
                f"Content hash not found in S3: {content_hash}"
            ) from e

    def exists(
        self,
        content_hash: str
    ) -> bool:
        """Check if file exists in S3."""
        storage_key = self._get_storage_key(content_hash)
        s3_key = f"{self.base_path}/{storage_key}"
        return self._exists_in_s3(s3_key)

    def delete(
        self,
        content_hash: str
    ):
        """Delete file from S3."""
        storage_key = self._get_storage_key(content_hash)
        s3_key = f"{self.base_path}/{storage_key}"

        self.s3.delete_object(
            Bucket=self.bucket,
            Key=s3_key
        )

    def _exists_in_s3(self, s3_key: str) -> bool:
        """Check if S3 object exists."""
        try:
            self.s3.head_object(
                Bucket=self.bucket,
                Key=s3_key
            )
            return True
        except self.s3.exceptions.NoSuchKey:
            return False
        except self.s3.exceptions.ClientError as e:
            # Handle 404 and 403 - treat as not exists (403 can mean object doesn't exist in some S3 configs)
            if e.response['Error']['Code'] in ('404', '403'):
                return False
            # For other errors (network), re-raise
            raise
        except Exception as e:
            # Log unexpected errors
            import sys
            print(f"Warning: Unexpected error checking S3 object {s3_key}: {e}", file=sys.stderr)
            # Assume doesn't exist to be safe (will trigger re-upload)
            return False

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
        s3_key = f"{self.base_path}/{storage_key}"

        try:
            response = self.s3.head_object(
                Bucket=self.bucket,
                Key=s3_key
            )
            return response.get('Metadata', {})
        except:
            return None

    # =========================================================================
    # Cloud Manifest Operations
    # =========================================================================

    def put_manifest(
        self,
        workspace: str,
        name: str,
        version_hash: str,
        manifest_data: Dict[str, Any],
        update_latest: bool = True,
    ) -> str:
        """
        Upload a cloud manifest to S3.

        Args:
            workspace: Dataset workspace
            name: Dataset name
            version_hash: Version hash
            manifest_data: Manifest dict to serialize as JSON
            update_latest: Also update the latest.json pointer

        Returns:
            S3 key where manifest was uploaded
        """
        import json
        from ..manifest import get_manifest_key, get_latest_manifest_key

        # Serialize manifest to JSON
        manifest_json = json.dumps(manifest_data, indent=2, default=str)
        manifest_bytes = manifest_json.encode('utf-8')

        # Upload versioned manifest
        manifest_key = get_manifest_key(workspace, name, version_hash)
        self.s3.put_object(
            Bucket=self.bucket,
            Key=manifest_key,
            Body=manifest_bytes,
            ContentType='application/json',
        )

        # Update latest.json pointer
        if update_latest:
            latest_key = get_latest_manifest_key(workspace, name)
            latest_pointer = json.dumps({
                "version_hash": version_hash,
                "manifest_key": manifest_key,
            }).encode('utf-8')
            self.s3.put_object(
                Bucket=self.bucket,
                Key=latest_key,
                Body=latest_pointer,
                ContentType='application/json',
            )

        return manifest_key

    def get_manifest(
        self,
        workspace: str,
        name: str,
        version_hash: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Download a cloud manifest from S3.

        Args:
            workspace: Dataset workspace
            name: Dataset name
            version_hash: Version hash (if None, fetches latest)

        Returns:
            Parsed manifest dict, or None if not found
        """
        import json
        from ..manifest import get_manifest_key, get_latest_manifest_key

        # If no version specified, get latest pointer first
        if version_hash is None:
            latest_key = get_latest_manifest_key(workspace, name)
            try:
                response = self.s3.get_object(Bucket=self.bucket, Key=latest_key)
                latest_data = json.loads(response['Body'].read().decode('utf-8'))
                version_hash = latest_data.get('version_hash')
                if not version_hash:
                    return None
            except self.s3.exceptions.NoSuchKey:
                return None
            except Exception:
                return None

        # Fetch the versioned manifest
        manifest_key = get_manifest_key(workspace, name, version_hash)
        try:
            response = self.s3.get_object(Bucket=self.bucket, Key=manifest_key)
            manifest_data = json.loads(response['Body'].read().decode('utf-8'))
            return manifest_data
        except self.s3.exceptions.NoSuchKey:
            return None
        except Exception:
            return None

    def manifest_exists(
        self,
        workspace: str,
        name: str,
        version_hash: Optional[str] = None,
    ) -> bool:
        """
        Check if a manifest exists in S3.

        Args:
            workspace: Dataset workspace
            name: Dataset name
            version_hash: Version hash (if None, checks latest.json)

        Returns:
            True if manifest exists
        """
        from ..manifest import get_manifest_key, get_latest_manifest_key

        if version_hash is None:
            key = get_latest_manifest_key(workspace, name)
        else:
            key = get_manifest_key(workspace, name, version_hash)

        try:
            self.s3.head_object(Bucket=self.bucket, Key=key)
            return True
        except:
            return False

    def list_manifests(
        self,
        workspace: Optional[str] = None,
        name: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        List all manifests in the bucket.

        Args:
            workspace: Filter by workspace (optional)
            name: Filter by name (optional, requires workspace)

        Returns:
            List of manifest info dicts with workspace, name, version_hash
        """
        # Build prefix
        prefix = "warp/manifests/"
        if workspace:
            prefix += f"{workspace}/"
            if name:
                prefix += f"{name}/"

        manifests = []
        paginator = self.s3.get_paginator('list_objects_v2')

        for page in paginator.paginate(Bucket=self.bucket, Prefix=prefix):
            for obj in page.get('Contents', []):
                key = obj['Key']
                # Skip latest.json pointers
                if key.endswith('/latest.json'):
                    continue
                # Skip non-JSON files
                if not key.endswith('.json'):
                    continue

                # Parse: warp/manifests/workspace/name/version_hash.json
                parts = key.split('/')
                if len(parts) >= 5:
                    ws = parts[2]
                    nm = parts[3]
                    version_file = parts[4]
                    vh = version_file.replace('.json', '')

                    manifests.append({
                        'workspace': ws,
                        'name': nm,
                        'version_hash': vh,
                        'key': key,
                        'size': obj.get('Size', 0),
                        'last_modified': obj.get('LastModified'),
                    })

        return manifests
