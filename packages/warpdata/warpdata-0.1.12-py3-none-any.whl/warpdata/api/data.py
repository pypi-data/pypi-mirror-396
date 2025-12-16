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
from ..core.registry import get_registry_readonly
from ..core.cache import get_cache
from ..engine.duck import get_engine


def load(
    source: str,
    as_format: str = "duckdb",
    limit: Optional[int] = None,
    include_rid: bool = False,
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
    """
    # Resolve shorthand dataset names (centralized in core.uris)
    source = resolve_dataset_id(source)

    # Parse URI
    uri = parse_uri(source)

    # Handle warpdata:// URIs (registered datasets)
    if uri.is_warpdata:
        return _load_registered_dataset(uri, as_format, limit, include_rid, **options)

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
        raise FileNotFoundError(f"Dataset not found: warpdata://{workspace}/{name}")

    version_hash = dataset_ver["version_hash"]
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
