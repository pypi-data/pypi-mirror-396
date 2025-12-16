"""
Manifest resource normalization utilities.

Provides a canonical schema for manifest resources and backward-compatible
readers for legacy formats.

Canonical resource schema:
    {
        "uri": str,           # file://abs/path OR s3://... OR https://...
        "size": int | None,   # bytes (optional)
        "checksum": str | None,  # optional (etag, sha1/sha256, etc.)
        "type": str           # "file" (reserved for future: directory, table, etc.)
    }
"""
from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, Optional, TypedDict, Union


class Resource(TypedDict, total=False):
    """Canonical resource entry."""
    uri: str
    size: Optional[int]
    checksum: Optional[str]
    type: str


def _to_file_uri(p: Union[str, Path]) -> str:
    """Convert a local path to file:// URI."""
    p = Path(p).expanduser().resolve()
    return f"file://{p}"


def normalize_resources(resources: Any) -> List[Resource]:
    """
    Normalize resources into canonical list[Resource].

    Supports legacy formats:
      - list[str] (local paths or URLs)
      - list[{"uri": "..."}]
      - list[{"path": "..."}]  (older format)

    Args:
        resources: Raw resources from manifest (any format)

    Returns:
        List of canonical Resource dicts

    Examples:
        >>> normalize_resources(["/path/to/file.parquet"])
        [{"uri": "file:///path/to/file.parquet", "size": None, "checksum": None, "type": "file"}]

        >>> normalize_resources([{"uri": "s3://bucket/key"}])
        [{"uri": "s3://bucket/key", "size": None, "checksum": None, "type": "file"}]
    """
    if resources is None:
        return []

    out: List[Resource] = []

    if isinstance(resources, list):
        for item in resources:
            # Legacy: list[str] - local paths or URLs
            if isinstance(item, str):
                uri = item
                if "://" not in uri:
                    uri = _to_file_uri(uri)
                out.append({
                    "uri": uri,
                    "size": None,
                    "checksum": None,
                    "type": "file"
                })
                continue

            # Canonical or semi-canonical: list[dict]
            if isinstance(item, dict):
                uri = item.get("uri") or item.get("path")
                if not uri:
                    raise ValueError(f"Invalid resource entry (missing uri): {item}")
                if "://" not in uri:
                    uri = _to_file_uri(uri)

                out.append({
                    "uri": uri,
                    "size": item.get("size"),
                    "checksum": item.get("checksum"),
                    "type": item.get("type") or "file",
                })
                continue

            raise ValueError(f"Unsupported resource entry type: {type(item)}")

        return out

    raise ValueError(f"Unsupported resources container type: {type(resources)}")


def resource_uris(manifest: Dict[str, Any]) -> List[str]:
    """
    Convenience: return list of resource URIs from any manifest version.

    Args:
        manifest: Dataset manifest dict

    Returns:
        List of URI strings

    Examples:
        >>> resource_uris({"resources": ["/path/file.parquet"]})
        ["file:///path/file.parquet"]
    """
    res = normalize_resources(manifest.get("resources"))
    return [r["uri"] for r in res]


def canonicalize_uri(resource: str) -> str:
    """
    Convert a resource string to canonical URI format.

    Args:
        resource: Path or URI string

    Returns:
        Canonical URI (file:// for local paths)
    """
    if "://" in resource:
        # Normalize file:// to absolute path
        if resource.startswith("file://"):
            return f"file://{Path(resource[7:]).expanduser().resolve()}"
        return resource
    # Treat as local path
    return _to_file_uri(resource)


def build_resource_entry(
    uri: str,
    size: Optional[int] = None,
    checksum: Optional[str] = None,
    resource_type: str = "file"
) -> Resource:
    """
    Build a canonical resource entry.

    Args:
        uri: Resource URI (will be canonicalized)
        size: File size in bytes (optional)
        checksum: Checksum string (optional)
        resource_type: Resource type (default: "file")

    Returns:
        Canonical Resource dict
    """
    return {
        "uri": canonicalize_uri(uri),
        "size": size,
        "checksum": checksum,
        "type": resource_type,
    }


# ============================================================================
# Cloud Manifest Schema
# ============================================================================
# Cloud manifests are stored at:
#   warp/manifests/<workspace>/<name>/<version_hash>.json
#   warp/manifests/<workspace>/<name>/latest.json  (pointer to latest)
# ============================================================================

CLOUD_MANIFEST_VERSION = 1


class CloudManifestResource(TypedDict, total=False):
    """Resource entry in a cloud manifest."""
    content_hash: str          # SHA256 hash of content
    uri: str                   # S3 URI where file is stored
    size: int                  # Exact byte size
    extension: str             # File extension (parquet, arrow, etc.)


class CloudManifestEmbedding(TypedDict, total=False):
    """Embedding space entry in a cloud manifest."""
    space_name: str
    provider: str
    model: str
    dimension: int
    distance_metric: str
    files: List[Dict[str, Any]]  # List of {name, content_hash, size, uri}


class CloudManifestRawData(TypedDict, total=False):
    """Raw data entry in a cloud manifest."""
    source_path: str           # Original source path
    source_type: str           # file, directory
    content_hash: str          # SHA256 hash
    size: int                  # Size in bytes
    compressed: bool           # Whether compressed
    compression_format: str    # tar.gz, etc.
    uri: str                   # S3 URI


class CloudManifestSchema(TypedDict, total=False):
    """Schema information in a cloud manifest."""
    columns: List[Dict[str, Any]]  # List of {name, type, nullable}


class CloudManifest(TypedDict, total=False):
    """Cloud manifest structure for dataset discovery and download."""
    manifest_version: int      # Schema version for forward compat
    dataset: str               # Full dataset identifier (workspace/name)
    version_hash: str          # 16-char version hash
    created_at: str            # ISO timestamp
    row_count: Optional[int]   # Row count if available
    schema: CloudManifestSchema  # Column schema
    resources: List[CloudManifestResource]
    embeddings: List[CloudManifestEmbedding]
    raw_data: List[CloudManifestRawData]
    metadata: Dict[str, Any]   # User metadata


def build_cloud_manifest(
    workspace: str,
    name: str,
    version_hash: str,
    resources: List[Dict[str, Any]],
    schema: Optional[Dict[str, str]] = None,
    row_count: Optional[int] = None,
    embeddings: Optional[List[Dict[str, Any]]] = None,
    raw_data: Optional[List[Dict[str, Any]]] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> CloudManifest:
    """
    Build a cloud manifest JSON structure.

    Args:
        workspace: Dataset workspace
        name: Dataset name
        version_hash: Version hash (16+ chars)
        resources: List of resource dicts with content_hash, uri, size, extension
        schema: Column schema dict {column_name: type_string}
        row_count: Total row count (optional)
        embeddings: List of embedding space dicts
        raw_data: List of raw data source dicts
        metadata: Additional metadata dict

    Returns:
        CloudManifest dict ready for JSON serialization
    """
    from datetime import datetime, timezone

    # Convert schema dict to list format
    schema_list = []
    if schema:
        for col_name, col_type in schema.items():
            schema_list.append({
                "name": col_name,
                "type": col_type,
                "nullable": True  # Default to nullable
            })

    return {
        "manifest_version": CLOUD_MANIFEST_VERSION,
        "dataset": f"{workspace}/{name}",
        "version_hash": version_hash,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "row_count": row_count,
        "schema": {"columns": schema_list} if schema_list else {"columns": []},
        "resources": resources or [],
        "embeddings": embeddings or [],
        "raw_data": raw_data or [],
        "metadata": metadata or {},
    }


def parse_cloud_manifest(data: Union[str, bytes, Dict]) -> CloudManifest:
    """
    Parse a cloud manifest from JSON string, bytes, or dict.

    Args:
        data: JSON string, bytes, or already-parsed dict

    Returns:
        CloudManifest dict

    Raises:
        ValueError: If manifest version is unsupported or data is invalid
    """
    import json

    if isinstance(data, bytes):
        data = data.decode('utf-8')
    if isinstance(data, str):
        data = json.loads(data)

    # Validate version
    version = data.get("manifest_version", 1)
    if version > CLOUD_MANIFEST_VERSION:
        raise ValueError(
            f"Unsupported manifest version {version}. "
            f"Max supported: {CLOUD_MANIFEST_VERSION}. "
            "Please upgrade warpdata."
        )

    return data


def get_manifest_key(workspace: str, name: str, version_hash: str) -> str:
    """
    Get the S3 key for a manifest.

    Args:
        workspace: Dataset workspace
        name: Dataset name
        version_hash: Version hash

    Returns:
        S3 key string (e.g., "warp/manifests/workspace/name/version.json")
    """
    return f"warp/manifests/{workspace}/{name}/{version_hash}.json"


def get_latest_manifest_key(workspace: str, name: str) -> str:
    """
    Get the S3 key for the latest.json pointer.

    Args:
        workspace: Dataset workspace
        name: Dataset name

    Returns:
        S3 key string (e.g., "warp/manifests/workspace/name/latest.json")
    """
    return f"warp/manifests/{workspace}/{name}/latest.json"


class ManifestNotFoundError(Exception):
    """Raised when a manifest is not found in cloud storage."""
    pass
