"""
Dataset management API for warpdata.

Provides functions for:
- Registering datasets (with automatic DuckDB ingestion)
- Listing datasets
- Getting dataset info
- Removing datasets
"""
import duckdb
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional, Union

from ..core.uris import parse_uri, require_warpdata_id
from ..core.registry import get_registry, get_registry_readonly
from ..core.cache import get_cache
from ..core.utils import compute_hash
from ..core.manifest import canonicalize_uri, build_resource_entry


def register_dataset(
    dataset_id: str,
    resources: List[str],
    schema: Optional[Dict[str, str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    raw_data: Optional[List[Union[str, Path, Dict[str, Any]]]] = None,
    file_format: Optional[str] = None,
    skip_ingest: bool = False,
) -> str:
    """
    Register a new dataset by ingesting data into a DuckDB file.

    This function:
    1. Parses the dataset ID
    2. Creates a .duckdb file in the cache directory (unless skip_ingest=True)
    3. Ingests all resources into a single 'main' table
    4. Registers the dataset in the registry
    5. Optionally registers raw data sources for provenance tracking

    Args:
        dataset_id: Dataset ID (e.g., 'warpdata://test/simple')
        resources: List of resource paths (local files or URLs)
        schema: Optional schema dictionary (auto-inferred if not provided)
        metadata: Optional metadata dictionary
        raw_data: Optional list of raw data sources for provenance tracking.
                  Can be strings/Paths (local files/dirs/URLs) or dicts with
                  keys: source_path, source_type, size, metadata
        file_format: Optional file format override (e.g., 'parquet', 'csv').
                     If not provided, inferred from first file extension.
        skip_ingest: If True, register dataset without copying data into DuckDB.
                     Data will be read directly from parquet files. Use for large
                     datasets to avoid OOM during ingestion.

    Returns:
        Version hash

    Examples:
        >>> import warpdata as wd
        >>> wd.register_dataset(
        ...     "warpdata://test/simple",
        ...     ["data.parquet"]
        ... )
        >>> # With raw data tracking
        >>> wd.register_dataset(
        ...     "warpdata://crypto/binance-klines",
        ...     ["curated.parquet"],
        ...     raw_data=["/data/raw/binance-bulk/"]
        ... )
    """
    # Parse dataset ID
    uri = parse_uri(dataset_id)
    if not uri.is_warpdata:
        raise ValueError(f"Invalid dataset ID. Must be warpdata:// URI: {dataset_id}")

    workspace = uri.workspace
    name = uri.name

    if not workspace or not name:
        raise ValueError(f"Invalid dataset ID format: {dataset_id}")

    if not resources:
        raise ValueError("No resources provided")

    # Compute version hash from resources
    version_hash = compute_hash(str(resources) + str(time.time()))[:16]

    # Create dataset directory
    cache = get_cache()
    dataset_dir = cache.datasets_dir / workspace / name / version_hash
    dataset_dir.mkdir(parents=True, exist_ok=True)
    db_path = dataset_dir / "data.duckdb"

    # Resolve resources to local paths and build canonical resource metadata
    local_paths = []
    resources_meta = []

    for resource in resources:
        canonical_uri = canonicalize_uri(resource)

        # Resolve to local path for ingestion
        if canonical_uri.startswith("file://"):
            local_path = Path(canonical_uri[7:])
        else:
            # Remote file - download to cache
            local_path = cache.get(canonical_uri)

        local_paths.append(str(local_path))

        # Get file size for metadata
        size = None
        try:
            size = local_path.stat().st_size if isinstance(local_path, Path) else Path(local_path).stat().st_size
        except Exception:
            pass

        resources_meta.append(build_resource_entry(
            uri=canonical_uri,
            size=size,
        ))

    # Detect format from file_format param or first file extension
    if file_format:
        ext = f".{file_format.lower().lstrip('.')}"
    else:
        first_file = Path(local_paths[0])
        ext = first_file.suffix.lower()

    # Handle skip_ingest mode - register parquet files directly without copying
    if skip_ingest:
        if ext not in (".parquet", ".pq"):
            raise ValueError(f"skip_ingest only supported for parquet files, got: {ext}")

        print(f"Registering dataset (skip_ingest=True, {len(local_paths)} parquet files)...")

        # Read schema and row count directly from parquet (only metadata, no full load)
        with duckdb.connect() as dconn:
            if len(local_paths) == 1:
                parquet_expr = f"read_parquet('{local_paths[0]}')"
            else:
                paths_list = ", ".join([f"'{p}'" for p in local_paths])
                parquet_expr = f"read_parquet([{paths_list}])"

            # Get schema (reads parquet footer only)
            if schema is None:
                schema = {}
                result = dconn.execute(f"DESCRIBE SELECT * FROM {parquet_expr}").fetchall()
                for row in result:
                    schema[row[0]] = row[1]

            # Get row count (fast for parquet - uses metadata)
            row_count = dconn.execute(f"SELECT COUNT(*) FROM {parquet_expr}").fetchone()[0]

        print(f"  ✓ Registered {row_count:,} rows ({len(schema)} columns) - data stays in parquet")

        # Build manifest pointing to parquet files
        manifest = {
            "schema": schema,
            "resources": resources_meta,
            "format": "parquet",
            "row_count": row_count,
            "metadata": metadata or {},
            "ingested": False,
        }
    else:
        # Normal ingestion path
        print(f"Ingesting data into {db_path}...")

        # Create DuckDB file and ingest data
        with duckdb.connect(str(db_path)) as dconn:
            if ext in (".parquet", ".pq"):
                # For parquet files, DuckDB can read a list directly
                if len(local_paths) == 1:
                    dconn.execute(f"CREATE TABLE main AS SELECT * FROM read_parquet('{local_paths[0]}')")
                else:
                    # Multiple files - union them
                    paths_list = ", ".join([f"'{p}'" for p in local_paths])
                    dconn.execute(f"CREATE TABLE main AS SELECT * FROM read_parquet([{paths_list}])")

            elif ext in (".csv", ".tsv"):
                sep = "\\t" if ext == ".tsv" else ","
                if len(local_paths) == 1:
                    dconn.execute(f"CREATE TABLE main AS SELECT * FROM read_csv('{local_paths[0]}', auto_detect=TRUE, sep='{sep}')")
                else:
                    paths_list = ", ".join([f"'{p}'" for p in local_paths])
                    dconn.execute(f"CREATE TABLE main AS SELECT * FROM read_csv([{paths_list}], auto_detect=TRUE, sep='{sep}')")

            elif ext in (".json", ".jsonl", ".ndjson"):
                if len(local_paths) == 1:
                    dconn.execute(f"CREATE TABLE main AS SELECT * FROM read_json('{local_paths[0]}', auto_detect=TRUE)")
                else:
                    paths_list = ", ".join([f"'{p}'" for p in local_paths])
                    dconn.execute(f"CREATE TABLE main AS SELECT * FROM read_json([{paths_list}], auto_detect=TRUE)")

            elif ext == ".arrow":
                # Arrow IPC files
                import pyarrow.ipc as ipc
                tables = []
                for p in local_paths:
                    with open(p, 'rb') as f:
                        reader = ipc.open_stream(f)
                        tables.append(reader.read_all())
                if len(tables) == 1:
                    dconn.from_arrow(tables[0]).create("main")
                else:
                    import pyarrow as pa
                    combined = pa.concat_tables(tables)
                    dconn.from_arrow(combined).create("main")
            else:
                raise ValueError(f"Unsupported file format: {ext}")

            # Get row count for metadata
            row_count = dconn.execute("SELECT COUNT(*) FROM main").fetchone()[0]

            # Get schema
            if schema is None:
                schema = {}
                result = dconn.execute("DESCRIBE main").fetchall()
                for row in result:
                    schema[row[0]] = row[1]

        print(f"  ✓ Ingested {row_count:,} rows into {db_path.name}")

        # Build manifest with canonical resources
        manifest = {
            "schema": schema,
            "resources": resources_meta,  # Canonical format: list[{uri, size, checksum, type}]
            "format": "duckdb",
            "row_count": row_count,
            "metadata": metadata or {},
            "ingested": True,
        }

    # Register in database
    registry = get_registry()
    # For skip_ingest, storage_path points to first parquet file; otherwise to duckdb
    storage_path = local_paths[0] if skip_ingest else str(db_path)
    registry.register_dataset(
        workspace, name, version_hash, manifest,
        storage_path=storage_path
    )

    # Register raw data sources if provided
    if raw_data:
        for item in raw_data:
            if isinstance(item, dict):
                # Dict entry with explicit fields
                source_path = str(item.get("source_path") or item.get("path") or "")
                source_type = str(item.get("source_type") or "file")
                size = item.get("size")
                md = item.get("metadata") or {}
            else:
                # String or Path - resolve and detect type
                item_str = str(item)
                if item_str.startswith(("http://", "https://", "s3://")):
                    source_path = item_str
                    source_type = "url"
                    size = None
                else:
                    p = Path(item_str).expanduser().resolve()
                    source_path = str(p)
                    if p.exists() and p.is_dir():
                        source_type = "directory"
                        try:
                            size = sum(f.stat().st_size for f in p.rglob("*") if f.is_file())
                        except Exception:
                            size = None
                    elif p.exists() and p.is_file():
                        source_type = "file"
                        try:
                            size = p.stat().st_size
                        except Exception:
                            size = None
                    else:
                        source_type = "file"  # Assume file even if not found
                        size = None
                md = {}

            if source_path:
                registry.register_raw_data_source(
                    workspace=workspace,
                    name=name,
                    version_hash=version_hash,
                    source_type=source_type,
                    source_path=source_path,
                    size=size,
                    content_hash=None,
                    metadata=md,
                )

    print(f"  ✓ Registered {dataset_id} (version: {version_hash})")
    return version_hash


def list_datasets(workspace: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    List all registered datasets.

    Args:
        workspace: Optional workspace filter

    Returns:
        List of dataset info dictionaries

    Examples:
        >>> import warpdata as wd
        >>> datasets = wd.list_datasets()
        >>> for ds in datasets:
        ...     print(f"{ds['workspace']}/{ds['name']}: {ds['latest_version']}")
    """
    registry = get_registry_readonly()
    return registry.list_datasets(workspace)


def dataset_info(dataset_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a dataset.

    Args:
        dataset_id: Dataset ID (e.g., 'warpdata://test/simple' or 'test/simple')

    Returns:
        Dictionary with dataset info including manifest

    Examples:
        >>> import warpdata as wd
        >>> info = wd.dataset_info("warpdata://test/simple")
        >>> print(info['manifest']['schema'])
    """
    # Resolve dataset ID (must be warpdata://, not a file)
    dataset_id = require_warpdata_id(dataset_id)
    uri = parse_uri(dataset_id)

    workspace = uri.workspace
    name = uri.name
    version = uri.version or "latest"

    # Get dataset version info (read-only)
    registry = get_registry_readonly()
    dataset_ver = registry.get_dataset_version(workspace, name, version)

    if dataset_ver is None:
        raise ValueError(f"Dataset not found: {dataset_id}")

    # Get manifest
    manifest = registry.get_manifest(workspace, name, dataset_ver["version_hash"])

    # Get storage path
    storage_path = registry.get_dataset_path(workspace, name, version)

    return {
        "workspace": workspace,
        "name": name,
        "version_hash": dataset_ver["version_hash"],
        "manifest": manifest,
        "storage_path": storage_path,
        "created_at": dataset_ver.get("created_at"),
    }


def remove_dataset(dataset_id: str, version: Optional[str] = None):
    """
    Remove a dataset or specific version from the registry.

    Args:
        dataset_id: Dataset ID (e.g., 'warpdata://test/simple')
        version: Optional version to remove (removes all versions if not specified)

    Examples:
        >>> import warpdata as wd
        >>> wd.remove_dataset("warpdata://test/old-dataset")
    """
    # Resolve dataset ID (must be warpdata://, not a file)
    dataset_id = require_warpdata_id(dataset_id)
    uri = parse_uri(dataset_id)

    workspace = uri.workspace
    name = uri.name

    # Get registry and remove
    registry = get_registry()
    registry.remove_dataset(workspace, name, version_hash=version)


def verify_dataset(dataset_id: str) -> Dict[str, Any]:
    """
    Verify that a dataset's DuckDB file exists and is readable.

    Args:
        dataset_id: Dataset ID

    Returns:
        Report dict with 'ok' boolean and details
    """
    # Resolve dataset ID (must be warpdata://, not a file)
    dataset_id = require_warpdata_id(dataset_id)
    uri = parse_uri(dataset_id)

    registry = get_registry_readonly()
    version_info = registry.get_dataset_version(uri.workspace, uri.name, uri.version or "latest")

    if not version_info:
        return {"ok": False, "error": "Dataset not found"}

    storage_path = registry.get_dataset_path(uri.workspace, uri.name, uri.version or "latest")

    if not storage_path:
        return {"ok": False, "error": "No storage path registered"}

    if not Path(storage_path).exists():
        return {"ok": False, "error": f"DuckDB file not found: {storage_path}"}

    # Try to read the file
    try:
        with duckdb.connect(storage_path, read_only=True) as conn:
            row_count = conn.execute("SELECT COUNT(*) FROM main").fetchone()[0]
            return {
                "ok": True,
                "storage_path": storage_path,
                "row_count": row_count,
                "version_hash": version_info["version_hash"],
            }
    except Exception as e:
        return {"ok": False, "error": f"Failed to read DuckDB file: {e}"}


def verify_datasets(workspace: Optional[str] = None) -> Dict[str, Any]:
    """
    Verify all datasets in the registry.

    Returns:
        Summary report with per-dataset results
    """
    registry = get_registry_readonly()
    datasets = registry.list_datasets(workspace)
    results = []
    issues = 0

    for ds in datasets:
        ds_id = f"warpdata://{ds['workspace']}/{ds['name']}"
        report = verify_dataset(ds_id)
        results.append({"dataset_id": ds_id, **report})
        if not report["ok"]:
            issues += 1

    return {
        "total": len(results),
        "with_issues": issues,
        "ok": issues == 0,
        "results": results,
    }
