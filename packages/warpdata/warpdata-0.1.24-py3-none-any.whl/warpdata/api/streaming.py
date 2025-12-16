"""
High-performance streaming API for huge datasets.

This module provides zero-copy Arrow streaming for datasets too large to fit in RAM.
"""
from typing import Iterator, List, Optional, Tuple
import pyarrow as pa

from ..core.uris import parse_uri, require_warpdata_id
from ..core.registry import get_registry_readonly
from ..core.cache import get_cache
from ..core.manifest import resource_uris
from ..engine.duck import get_engine


def stream(
    dataset_id: str,
    columns: Optional[List[str]] = None,
    batch_size: int = 10000,
    shard: Optional[Tuple[int, int]] = None,
    limit: Optional[int] = None,
) -> Iterator[pa.RecordBatch]:
    """
    Stream a huge dataset efficiently without loading it into RAM.

    Uses zero-copy Arrow batches from DuckDB for maximum performance.
    Supports file-level sharding for distributed/multi-worker training.

    Args:
        dataset_id: Dataset ID (e.g., 'warpdata://text/wikipedia-main' or 'text/wikipedia-main')
        columns: Specific columns to read (projection pushdown for speed)
        batch_size: Number of rows per yielded batch
        shard: Tuple (rank, world_size) for distributed training.
               Splits files among workers to avoid reading duplicates.
        limit: Maximum number of rows to stream (useful for testing)

    Yields:
        PyArrow RecordBatch objects (zero-copy, can convert to numpy/torch)

    Example:
        >>> import warpdata as wd
        >>> # Stream 50K row batches
        >>> for batch in wd.stream('text/wikipedia-main', batch_size=50000):
        ...     # Convert to numpy
        ...     data = batch.to_pandas().to_numpy()
        ...     train_step(data)

        >>> # Multi-worker sharding (8 workers, this is worker 3)
        >>> for batch in wd.stream('text/wikipedia-main', shard=(3, 8)):
        ...     # Only reads 1/8th of files
        ...     process(batch)

        >>> # Column projection (only read 'text' column)
        >>> for batch in wd.stream('text/wikipedia-main', columns=['text']):
        ...     texts = batch['text'].to_pylist()
    """

    # 1. Resolve and validate dataset ID (must be a warpdata:// URI, not a file)
    dataset_id = require_warpdata_id(dataset_id)
    uri = parse_uri(dataset_id)

    # 2. Get manifest to find actual files
    registry = get_registry_readonly()
    ver = registry.get_dataset_version(uri.workspace, uri.name, uri.version or "latest")

    if ver is None:
        raise ValueError(f"Dataset not found: {dataset_id}")

    manifest = registry.get_manifest(uri.workspace, uri.name, ver["version_hash"])

    if not manifest or "resources" not in manifest:
        raise ValueError(f"No resources found for {dataset_id}")

    # 3. Get local file paths (backward-compatible with legacy manifest formats)
    resources = resource_uris(manifest)
    cache = get_cache()
    local_paths = [str(cache.get(r)) for r in resources]

    # 4. Apply file-level sharding (critical for multi-worker efficiency)
    # Instead of every worker reading all files, assign files to workers
    if shard:
        rank, world_size = shard
        if rank >= world_size:
            raise ValueError(f"Invalid shard: rank {rank} >= world_size {world_size}")

        # Round-robin assignment: worker 0 gets files [0,8,16...], worker 1 gets [1,9,17...]
        local_paths = local_paths[rank::world_size]

        if not local_paths:
            # This worker has no files assigned
            return iter(())

    # 5. Load into DuckDB relation
    engine = get_engine()

    # Read all assigned files (DuckDB handles multiple Parquet efficiently)
    rel = engine.conn.read_parquet(local_paths)

    # Apply column projection (only read needed columns from disk)
    if columns:
        # Quote column names to handle special characters
        cols_str = ", ".join(f'"{c}"' for c in columns)
        rel = rel.project(cols_str)

    # Apply row limit if specified
    if limit is not None:
        rel = rel.limit(limit)

    # 6. Stream using zero-copy Arrow batches
    yield from engine.stream_arrow(rel, batch_size)


def stream_batch_dicts(
    dataset_id: str,
    columns: Optional[List[str]] = None,
    batch_size: int = 10000,
    shard: Optional[Tuple[int, int]] = None,
    limit: Optional[int] = None,
) -> Iterator[dict]:
    """
    Stream batches as dictionaries of lists (similar to current WarpStreamingDataset).

    This is a convenience wrapper around stream() for compatibility with
    existing collators that expect {column: [values]} format.

    Args:
        Same as stream()

    Yields:
        dict mapping column names to lists of values

    Example:
        >>> for batch in wd.stream_batch_dicts('text/wikipedia-main'):
        ...     texts = batch['text']  # List of strings
        ...     process(texts)
    """
    for arrow_batch in stream(dataset_id, columns, batch_size, shard, limit):
        # Convert Arrow batch to dict of lists
        yield arrow_batch.to_pydict()
