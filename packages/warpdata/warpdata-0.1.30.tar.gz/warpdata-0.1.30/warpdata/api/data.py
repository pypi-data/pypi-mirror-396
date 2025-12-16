"""
Core data loading API for warpdata.

Provides the main functions for loading and inspecting data:
- load(): Load data from any source (returns DuckDB relation)
- schema(): Inspect data schema
- head(): Preview first N rows
"""
import duckdb
from pathlib import Path
from typing import Union, Optional, Dict, Any

from ..core.uris import parse_uri, resolve_dataset_id
from ..core.registry import get_registry_readonly, get_registry
from ..core.cache import get_cache
from ..engine.duck import get_engine


def _fetch_raw_data_from_manifest(workspace: str, name: str, version_hash: str) -> None:
    """Fetch and download raw data directly from S3 manifest."""
    import os
    from pathlib import Path

    try:
        from .storage import DEFAULT_BUCKET, get_storage_backend
        from ..core.storage.bucket_utils import normalize_bucket_name
        from ..core.storage.s3 import S3Storage

        bucket = os.environ.get("WARPDATA_BUCKET", DEFAULT_BUCKET)
        bucket = normalize_bucket_name(bucket)

        # Get S3 storage to fetch manifest
        storage = S3Storage(bucket=bucket)
        manifest = storage.get_manifest(workspace, name, version_hash)

        if not manifest:
            # Try without version hash (get latest)
            manifest = storage.get_manifest(workspace, name, None)

        if not manifest:
            print(f"  ⚠️  No manifest found in S3 for {workspace}/{name}")
            return

        raw_data = manifest.get("raw_data", [])
        if not raw_data:
            print(f"  ℹ️  No raw data in manifest")
            return

        print(f"  📥 Downloading {len(raw_data)} raw data files from S3...")

        # Compute local raw data directory
        raw_base = Path.home() / ".warpdata" / "raw" / workspace / name
        raw_base.mkdir(parents=True, exist_ok=True)

        # Also register in local registry
        from ..core.registry import get_registry
        registry = get_registry()

        for rd in raw_data:
            content_hash = rd.get("content_hash")
            source_path = rd.get("source_path", "")
            size = rd.get("size")
            source_type = rd.get("source_type", "file")
            metadata = rd.get("metadata") or {}

            if not content_hash:
                continue

            # Check if this is a compressed directory
            # Note: compressed flag is at top level of raw_data entry, not in metadata
            is_compressed = rd.get("compressed", False)
            compression_format = rd.get("compression_format") or "tar.gz"

            # Local path (directory name for compressed, file for regular)
            filename = Path(source_path).name
            local_path = raw_base / filename

            # For compressed directories: need to download AND extract
            # Check if already properly extracted (exists as directory)
            # or if it's a file that needs extraction
            needs_download = not local_path.exists()
            needs_extract = False

            if is_compressed:
                if local_path.exists() and local_path.is_file():
                    # File exists but should be a directory - it's a compressed archive
                    # that was downloaded but not extracted (from older buggy version)
                    needs_extract = True
                    needs_download = False
                    print(f"    📦 {filename} exists as file, extracting...")
                elif local_path.exists() and local_path.is_dir():
                    # Already properly extracted
                    needs_download = False
                    needs_extract = False

            if needs_download or needs_extract:
                try:
                    if is_compressed:
                        # Download to temp file and extract
                        import tempfile
                        from ..core.compression import decompress_archive

                        if needs_extract and local_path.is_file():
                            # Move existing file to temp location for extraction
                            suffix = '.tar.zst' if compression_format == 'tar.zst' else '.tar.gz'
                            fd, temp_archive = tempfile.mkstemp(suffix=suffix)
                            os.close(fd)
                            import shutil
                            shutil.move(str(local_path), temp_archive)
                            archive_path = Path(temp_archive)
                        else:
                            # Download to temp file
                            suffix = '.tar.zst' if compression_format == 'tar.zst' else '.tar.gz'
                            fd, temp_archive = tempfile.mkstemp(suffix=suffix)
                            os.close(fd)
                            archive_path = Path(temp_archive)

                            print(f"    ↓ {filename} (compressed)...")
                            storage.get(content_hash, archive_path)

                        try:
                            # Extract to parent (creates the directory)
                            decompress_archive(
                                archive_path,
                                raw_base,
                                compression_format=compression_format,
                            )
                            print(f"    ✓ {filename} (extracted)")
                        finally:
                            if temp_archive and Path(temp_archive).exists():
                                Path(temp_archive).unlink()
                    else:
                        # Regular file download
                        storage.get(content_hash, local_path)
                        print(f"    ✓ {filename}")
                except Exception as e:
                    print(f"    ✗ {filename}: {e}")
                    continue

            # Register in local registry
            try:
                registry.add_raw_data_source(
                    workspace=workspace,
                    name=name,
                    version_hash=version_hash,
                    source_type=source_type,
                    source_path=str(local_path),
                    size=size,
                    content_hash=content_hash,
                    metadata=metadata,
                )
            except Exception:
                pass  # May already exist

    except Exception as e:
        import sys
        print(f"  ⚠️  Failed to fetch raw data from S3: {e}", file=sys.stderr)


def _ensure_raw_data_exists(workspace: str, name: str, version_hash: str) -> None:
    """
    Ensure raw data files exist locally, downloading from S3 if missing.

    Called after dataset is registered to make sure raw data is available.
    """
    import os
    from pathlib import Path

    # Check if auto-fetch is disabled
    if os.environ.get("WARPDATA_NO_AUTO_FETCH", "").lower() in ("1", "true", "yes"):
        return

    # Get raw data sources from registry
    registry = get_registry_readonly()
    raw_sources = registry.list_raw_data_sources(workspace, name, version_hash)

    if not raw_sources:
        # No raw data registered - try to fetch from S3 manifest
        print(f"  ℹ️  No raw data sources registered locally, checking S3...")
        _fetch_raw_data_from_manifest(workspace, name, version_hash)
        return

    # Check if any raw data files are missing
    missing = []
    for source in raw_sources:
        source_path = Path(source.get("source_path", ""))
        if source_path and not source_path.exists():
            missing.append(source)

    if not missing:
        return  # All raw data exists

    # Download missing raw data from S3
    print(f"  📥 Downloading {len(missing)} missing raw data files...")

    try:
        from .storage import DEFAULT_BUCKET, get_storage_backend
        from ..core.storage.bucket_utils import normalize_bucket_name

        bucket = os.environ.get("WARPDATA_BUCKET", DEFAULT_BUCKET)
        bucket = normalize_bucket_name(bucket)

        storage = get_storage_backend("s3", bucket=bucket)

        for source in missing:
            content_hash = source.get("content_hash")
            source_path = Path(source.get("source_path", ""))

            if not content_hash or not source_path:
                continue

            # Ensure parent directory exists
            source_path.parent.mkdir(parents=True, exist_ok=True)

            try:
                storage.get(content_hash, source_path)
                print(f"    ✓ {source_path.name}")
            except Exception as e:
                print(f"    ✗ {source_path.name}: {e}")

    except Exception as e:
        import sys
        print(f"  ⚠️  Raw data download failed: {e}", file=sys.stderr)


def _try_auto_register_from_remote(workspace: str, name: str, version: str) -> Optional[Dict[str, Any]]:
    """
    Try to auto-pull a dataset from remote S3 storage.

    Called when a dataset is not found in the local registry.
    Downloads both metadata and raw data, then returns the dataset version info.
    Silently returns None if the dataset isn't available remotely.
    """
    import os

    # Check if auto-fetch is disabled
    if os.environ.get("WARPDATA_NO_AUTO_FETCH", "").lower() in ("1", "true", "yes"):
        return None

    try:
        from .storage import pull_dataset, DEFAULT_BUCKET
        from ..core.storage.bucket_utils import normalize_bucket_name

        dataset_id = f"warpdata://{workspace}/{name}"

        # Allow bucket override via environment variable
        bucket = os.environ.get("WARPDATA_BUCKET", DEFAULT_BUCKET)
        bucket = normalize_bucket_name(bucket)

        # Pull dataset (registers + downloads raw data)
        print(f"  📥 Auto-pulling {workspace}/{name} from s3://{bucket}...")
        try:
            pull_dataset(
                dataset_id,
                bucket=bucket,
                include_raw=True,
                mode="full",
            )
        except Exception as pull_err:
            # Raw data download may fail, but registration might have succeeded
            # Continue to check registry
            import sys
            print(f"  ⚠️  Pull partially failed: {pull_err}", file=sys.stderr)

        # Re-fetch from registry (registration may have succeeded even if download failed)
        from ..core.registry import reset_registry
        reset_registry()  # Clear cached registry to pick up new data
        registry = get_registry_readonly()
        return registry.get_dataset_version(workspace, name, version)

    except Exception as e:
        # Silently fail - dataset just isn't available remotely
        import sys
        if os.environ.get("WARPDATA_DEBUG"):
            print(f"  ⚠️  Auto-pull failed: {e}", file=sys.stderr)
        return None


def load(
    source: str,
    as_format: str = "duckdb",
    limit: Optional[int] = None,
    include_rid: bool = False,
    resolve_paths: bool = False,
    raw_data_dir: Optional[str] = None,
    **options
) -> Union[duckdb.DuckDBPyRelation, Any]:
    """
    Load data from any source.

    For registered datasets, this uses DuckDB's ATTACH to efficiently
    query the dataset's .duckdb file without copying data.

    Supports:
    - Local files: /path/to/file.parquet
    - Registered datasets: warpdata://workspace/name[@version]
    - Shorthand: workspace/name or just name

    Args:
        source: Data source URI or path
        as_format: Output format ('duckdb', 'pandas', 'polars', 'arrow')
        limit: Optional row limit
        include_rid: If True, prepend a 'rid' column with 0-based row numbers.
                     Useful for embeddings workflows (load_embeddings with rids param).
                     Note: row order is stable within a single query but depends on
                     underlying scan order.
        resolve_paths: If True, resolve *_path columns to local raw data directory.
                       Useful for datasets with image/file references after pulling.
        raw_data_dir: Custom raw data directory. If None, uses ~/.warpdata/raw/
        **options: Additional options

    Returns:
        Data in requested format (default: DuckDB relation)

    Examples:
        >>> import warpdata as wd
        >>> rel = wd.load("warpdata://test/simple")
        >>> rel.filter("a > 1").df()

        >>> df = wd.load("test/simple", as_format="pandas")

        >>> # With row IDs for embeddings workflow
        >>> rel = wd.load("text/corpus", include_rid=True)
        >>> df = rel.limit(1000).df()
        >>> rids = df['rid'].tolist()
        >>> X = load_embeddings("text/corpus", space="minilm", rids=rids)

        >>> # Resolve file paths after pulling dataset
        >>> df = wd.load("vision/vesuvius", as_format="pandas", resolve_paths=True)
        >>> # df['image_path'] now points to ~/.warpdata/raw/vision/vesuvius/...
    """
    # Resolve shorthand dataset names (centralized in core.uris)
    source = resolve_dataset_id(source)

    # Parse URI
    uri = parse_uri(source)

    # Handle warpdata:// URIs (registered datasets)
    if uri.is_warpdata:
        result = _load_registered_dataset(uri, as_format, limit, include_rid, **options)

        # Resolve paths if requested
        if resolve_paths and as_format in ("pandas", "polars"):
            result = _resolve_path_columns(result, uri.workspace, uri.name, raw_data_dir)

        return result

    # Handle direct file paths
    return _load_direct_file(source, as_format, limit, include_rid, **options)


def _load_registered_dataset(
    uri,
    as_format: str = "duckdb",
    limit: Optional[int] = None,
    include_rid: bool = False,
    **options
) -> Any:
    """
    Load a registered dataset using DuckDB ATTACH or direct parquet read.

    Args:
        uri: Parsed warpdata:// URI
        as_format: Output format
        limit: Optional row limit
        include_rid: If True, prepend a 'rid' column with 0-based row numbers
        **options: Additional options

    Returns:
        Data in requested format
    """
    registry = get_registry_readonly()
    engine = get_engine()

    workspace = uri.workspace
    name = uri.name
    version = uri.version or "latest"

    # Get dataset version info
    dataset_ver = registry.get_dataset_version(workspace, name, version)
    if not dataset_ver:
        # Try to auto-register from remote storage
        dataset_ver = _try_auto_register_from_remote(workspace, name, version)
        if not dataset_ver:
            raise FileNotFoundError(f"Dataset not found: warpdata://{workspace}/{name}")

    version_hash = dataset_ver["version_hash"]

    # Ensure raw data exists (download if missing)
    _ensure_raw_data_exists(workspace, name, version_hash)

    manifest = registry.get_manifest(workspace, name, version_hash)

    # Check if this is a skip_ingest dataset (format=parquet, ingested=False)
    if manifest and manifest.get("format") == "parquet" and not manifest.get("ingested", True):
        # Load directly from parquet resources
        resources = manifest.get("resources", [])
        if not resources:
            raise FileNotFoundError(f"No resources found for dataset: warpdata://{workspace}/{name}")

        # Build list of parquet file paths
        parquet_paths = []
        for r in resources:
            res_uri = r.get("uri", "")
            if res_uri.startswith("file://"):
                parquet_paths.append(res_uri[7:])
            elif res_uri.startswith("s3://"):
                parquet_paths.append(res_uri)
            else:
                parquet_paths.append(res_uri)

        # Read parquet files directly
        if len(parquet_paths) == 1:
            base_query = f"read_parquet('{parquet_paths[0]}')"
        else:
            paths_list = ", ".join([f"'{p}'" for p in parquet_paths])
            base_query = f"read_parquet([{paths_list}])"

        # Build SELECT with optional rid column
        if include_rid:
            relation = engine.conn.sql(f"SELECT (row_number() OVER () - 1)::BIGINT AS rid, * FROM {base_query}")
        else:
            relation = engine.conn.sql(f"SELECT * FROM {base_query}")

        # Apply limit if specified
        if limit is not None:
            relation = relation.limit(limit)

        return _convert_format(relation, as_format, engine)

    # Normal path: ATTACH DuckDB file
    db_path = registry.get_dataset_path(workspace, name, version)

    if not db_path:
        raise FileNotFoundError(f"Dataset not found: warpdata://{workspace}/{name}")

    if not Path(db_path).exists():
        raise FileNotFoundError(f"Dataset file not found: {db_path}")

    # Create safe alias for the database
    db_alias = f"{workspace}_{name}".replace("-", "_").replace(".", "_")

    # Check if already attached
    attached_dbs = engine.conn.execute("SELECT database_name FROM duckdb_databases()").fetchall()
    attached_names = [row[0] for row in attached_dbs]

    if db_alias not in attached_names:
        engine.conn.execute(f"ATTACH '{db_path}' AS {db_alias} (READ_ONLY)")

    # Create relation to the main table with optional rid column
    if include_rid:
        relation = engine.conn.sql(f"SELECT (row_number() OVER () - 1)::BIGINT AS rid, * FROM {db_alias}.main")
    else:
        relation = engine.conn.sql(f"SELECT * FROM {db_alias}.main")

    # Apply limit if specified
    if limit is not None:
        relation = relation.limit(limit)

    # Convert to requested format
    return _convert_format(relation, as_format, engine)


def _load_direct_file(
    source: str,
    as_format: str = "duckdb",
    limit: Optional[int] = None,
    include_rid: bool = False,
    **options
) -> Any:
    """
    Load data directly from a file.

    Args:
        source: File path
        as_format: Output format
        limit: Optional row limit
        include_rid: If True, prepend a 'rid' column with 0-based row numbers
        **options: Additional options

    Returns:
        Data in requested format
    """
    cache = get_cache()
    engine = get_engine()

    # Get local path (downloads if remote)
    local_path = cache.get(source)

    # Read with engine
    relation = engine.read_file(local_path)

    # Add rid column if requested
    if include_rid:
        # Wrap the relation with row_number() to add rid
        relation = engine.conn.sql(
            "SELECT (row_number() OVER () - 1)::BIGINT AS rid, * FROM relation"
        )

    # Apply limit if specified
    if limit is not None:
        relation = relation.limit(limit)

    # Convert to requested format
    return _convert_format(relation, as_format, engine)


def _convert_format(relation, as_format: str, engine) -> Any:
    """
    Convert a DuckDB relation to the requested format.

    Args:
        relation: DuckDB relation
        as_format: Target format
        engine: DuckDB engine

    Returns:
        Data in requested format
    """
    if as_format == "duckdb":
        return relation
    elif as_format == "pandas":
        return engine.to_df(relation, "pandas")
    elif as_format == "polars":
        try:
            return engine.to_df(relation, "polars")
        except ImportError:
            raise ImportError("polars is not installed. Install with: pip install polars")
    elif as_format == "arrow":
        return engine.to_df(relation, "arrow")
    else:
        raise ValueError(f"Unsupported format: {as_format}")


def schema(source: str) -> Dict[str, str]:
    """
    Get the schema of a data source.

    Args:
        source: Data source URI or path

    Returns:
        Dictionary mapping column names to types

    Examples:
        >>> import warpdata as wd
        >>> schema = wd.schema("test/simple")
        >>> print(schema)
        {'a': 'BIGINT', 'b': 'VARCHAR'}
    """
    # Load as duckdb relation and extract schema
    relation = load(source, as_format="duckdb")
    schema_dict = {}
    for col_name, col_type in zip(relation.columns, relation.types):
        schema_dict[col_name] = str(col_type)
    return schema_dict


def head(source: str, n: int = 5, as_format: str = "duckdb") -> Any:
    """
    Preview the first N rows of a data source.

    Args:
        source: Data source URI or path
        n: Number of rows to return (default: 5)
        as_format: Output format ('duckdb', 'pandas', 'polars')

    Returns:
        First N rows in requested format

    Examples:
        >>> import warpdata as wd
        >>> preview = wd.head("test/simple", n=10)
        >>> print(preview)
    """
    return load(source, as_format=as_format, limit=n)


def _resolve_path_columns(df, workspace: str, name: str, raw_data_dir: Optional[str] = None):
    """
    Resolve *_path columns to local raw data directory.

    Detects columns ending in '_path' and rewrites absolute paths to point
    to the local raw data directory.

    Args:
        df: DataFrame (pandas or polars)
        workspace: Dataset workspace
        name: Dataset name
        raw_data_dir: Custom raw data directory (default: ~/.warpdata/raw/)

    Returns:
        DataFrame with resolved paths
    """
    import os

    # Determine raw data directory
    if raw_data_dir:
        base_dir = Path(raw_data_dir)
    else:
        base_dir = Path.home() / ".warpdata" / "raw" / workspace / name

    # Detect path columns
    path_columns = [col for col in df.columns if col.endswith('_path')]

    if not path_columns:
        return df

    # Check if this is pandas or polars
    is_polars = hasattr(df, 'with_columns')

    if is_polars:
        import polars as pl

        for col in path_columns:
            df = df.with_columns(
                pl.col(col).map_elements(
                    lambda p: str(base_dir / Path(p).name) if p and isinstance(p, str) else p,
                    return_dtype=pl.Utf8
                ).alias(col)
            )
    else:
        # pandas
        for col in path_columns:
            df[col] = df[col].apply(
                lambda p: str(base_dir / Path(p).name) if p and isinstance(p, str) else p
            )

    return df


def resolve_paths(
    df,
    workspace: str,
    name: str,
    raw_data_dir: Optional[str] = None,
    path_columns: Optional[list] = None,
):
    """
    Resolve file path columns to local raw data directory.

    Use this to fix paths after pulling a dataset to a new machine.

    Args:
        df: DataFrame (pandas or polars)
        workspace: Dataset workspace (e.g., 'vision')
        name: Dataset name (e.g., 'vesuvius-scrolls')
        raw_data_dir: Custom raw data directory. Default: ~/.warpdata/raw/{workspace}/{name}/
        path_columns: List of column names to resolve. Default: auto-detect *_path columns

    Returns:
        DataFrame with resolved paths

    Examples:
        >>> import warpdata as wd
        >>> import pandas as pd
        >>>
        >>> df = wd.load("vision/vesuvius-scrolls", as_format="pandas")
        >>> df = wd.resolve_paths(df, "vision", "vesuvius-scrolls")
        >>> # df['image_path'] now points to ~/.warpdata/raw/vision/vesuvius-scrolls/...
    """
    # Determine raw data directory
    if raw_data_dir:
        base_dir = Path(raw_data_dir)
    else:
        base_dir = Path.home() / ".warpdata" / "raw" / workspace / name

    # Detect path columns if not specified
    if path_columns is None:
        path_columns = [col for col in df.columns if col.endswith('_path')]

    if not path_columns:
        return df

    # Check if this is pandas or polars
    is_polars = hasattr(df, 'with_columns')

    if is_polars:
        import polars as pl

        for col in path_columns:
            df = df.with_columns(
                pl.col(col).map_elements(
                    lambda p: str(base_dir / Path(p).name) if p and isinstance(p, str) else p,
                    return_dtype=pl.Utf8
                ).alias(col)
            )
    else:
        # pandas
        for col in path_columns:
            df[col] = df[col].apply(
                lambda p: str(base_dir / Path(p).name) if p and isinstance(p, str) else p
            )

    return df
