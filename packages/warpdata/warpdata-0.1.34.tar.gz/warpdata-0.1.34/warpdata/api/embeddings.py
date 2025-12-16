"""
Embeddings API for warpdata.

Provides functions for:
- Adding embedding spaces to datasets
- Searching embeddings
- Joining search results back to original data
- Listing embedding spaces

v2: Uses EmbeddingStore abstraction for scalable, zero-copy operations.
"""
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Tuple
import numpy as np
import pyarrow.parquet as pq
import pyarrow as pa

logger = logging.getLogger(__name__)

from ..core.uris import parse_uri, require_warpdata_id
from ..core.registry import get_registry, get_registry_readonly
from ..core.cache import get_cache
from ..compute.embeddings import get_provider
from ..embeddings import ParquetEmbeddingStore, open_embedding_store
from ..embeddings.writer import EmbeddingWriter
from ..embeddings.indexer import build_index, select_index_type
from ..embeddings.types import EmbeddingSpaceMeta

# Optional progress bar (tqdm). If not available, we run without UI.
try:  # pragma: no cover - best-effort optional dependency
    from tqdm.auto import tqdm as _tqdm  # type: ignore
except Exception:  # pragma: no cover
    _tqdm = None


def add_embeddings(
    dataset_id: str,
    space: str,
    provider: str,
    source: Dict[str, Any],
    model: Optional[str] = None,
    dimension: Optional[int] = None,
    distance_metric: str = "cosine",
    batch_size: int = 100,
    show_progress: bool = True,
    max_rows: Optional[int] = None,
    rows_per_chunk: Optional[int] = None,
    write_rows_per_group: Optional[int] = None,
    **provider_kwargs,
) -> Path:
    """
    Add an embedding space to a dataset.

    The dataset must first be materialized to have a 'rid' (row ID) column.

    Args:
        dataset_id: Dataset ID (e.g., 'warpdata://nlp/reviews' or shorthand 'nlp/reviews')
        space: Name for this embedding space
        provider: Embedding provider ('numpy', 'sentence-transformers', 'openai', 'clap-audio', 'clip', 'clip-text')
        source: Source configuration (e.g., {'columns': ['text']})
        model: Model name (provider-specific)
        dimension: Embedding dimension (for providers that need it)
        distance_metric: Distance metric ('cosine', 'euclidean', 'dot')
        batch_size: Batch size for processing
        **provider_kwargs: Additional provider arguments

    Returns:
        Path to embedding storage directory

    Examples:
        >>> import warpdata as wd
        >>> wd.add_embeddings(
        ...     "warpdata://nlp/reviews",
        ...     space="openai-ada",
        ...     provider="openai",
        ...     model="text-embedding-ada-002",
        ...     source={"columns": ["review_text"]}
        ... )
    """
    # Resolve dataset ID (must be warpdata://, not a file)
    dataset_id = require_warpdata_id(dataset_id)
    uri = parse_uri(dataset_id)

    workspace = uri.workspace
    name = uri.name
    version = uri.version or "latest"

    # Materialize dataset to ensure rid column exists (do this FIRST)
    from .management import materialize
    from ..engine.duck import get_engine

    # Materialize without updating registry to keep dataset version stable
    materialized_path = materialize(dataset_id, update_registry=False)

    # Get dataset version AFTER materialization (version may have changed)
    registry = get_registry()
    dataset_ver = registry.get_dataset_version(workspace, name, version)

    if dataset_ver is None:
        raise ValueError(f"Dataset not found: {dataset_id}")

    version_hash = dataset_ver["version_hash"]

    # Get embedding provider first to know dimension
    # Resolve default model names per provider for clear registry metadata
    resolved_model = model
    if provider == "sentence-transformers" and resolved_model is None:
        resolved_model = "all-MiniLM-L6-v2"
    elif provider == "openai" and resolved_model is None:
        resolved_model = "text-embedding-ada-002"
    elif provider == "clip" and resolved_model is None:
        resolved_model = "openai/clip-vit-base-patch32"
    elif provider == "clap-audio" and resolved_model is None:
        resolved_model = "laion/clap-htsat-unfused"
    elif provider == "numpy" and dimension is None:
        # Keep None here; dimension is handled below
        pass

    embedding_provider = get_provider(
        provider=provider, model=resolved_model, dimension=dimension, **provider_kwargs
    )
    actual_dimension = embedding_provider.get_dimension()

    # Extract source columns
    columns = source.get("columns", [])
    if not columns:
        raise ValueError("Source must specify 'columns' to embed")

    # Build SQL query to concatenate columns and stream data
    # Safely quote column names, cast to string, and handle NULLs
    safe_columns = [f'COALESCE(CAST("{col}" AS VARCHAR), \'\')' for col in columns]
    text_sql_expr = "trim(" + " || ' ' || ".join(safe_columns) + ")"

    # Determine max text length based on provider
    # Most sentence transformers have 512 token limit (~2000 chars)
    # Truncate at SQL level to save memory and prevent tokenization issues
    if provider == "sentence-transformers":
        max_chars = 8000  # ~2000 tokens with safety margin
        text_sql_expr = f"LEFT({text_sql_expr}, {max_chars})"
    elif provider in ["openai", "clip-text"]:
        max_chars = 32000  # More generous for these models
        text_sql_expr = f"LEFT({text_sql_expr}, {max_chars})"

    # Create streaming query ordered by rid
    # Filter out rows with NULL or empty text to avoid embedding empty strings
    engine = get_engine()
    base_query_core = f"""
    SELECT rid, {text_sql_expr} AS text_to_embed
    FROM read_parquet('{materialized_path}')
    WHERE {text_sql_expr} IS NOT NULL AND {text_sql_expr} != ''
    """

    # Build final queries (count/read) with optional LIMIT
    limit_clause = f" LIMIT {int(max_rows)}" if (max_rows is not None and int(max_rows) > 0) else ""
    count_source_query = base_query_core + limit_clause

    # Determine total row count for progress bar and indexing heuristics
    try:
        count_query = f"SELECT COUNT(*) AS cnt FROM ({count_source_query}) AS sub"
        total_rows = engine.conn.execute(count_query).fetchone()[0]
    except Exception:
        total_rows = None

    # Prepare storage directory
    cache = get_cache()
    dataset_cache_dir = cache.get_dataset_cache_dir(workspace, name, version_hash)
    embeddings_dir = dataset_cache_dir / "embeddings" / space
    embeddings_dir.mkdir(parents=True, exist_ok=True)

    # Save embeddings as Parquet using efficient Arrow FixedSizeList
    vectors_path = embeddings_dir / "vectors.parquet"

    # Check if embeddings already exist and compare sizes
    existing_count = 0
    if vectors_path.exists():
        try:
            existing_table = pq.read_table(vectors_path)
            existing_count = len(existing_table)
            logger.info(f"Found existing embeddings: {existing_count:,} rows")

            # If we're trying to embed more rows than exist, overwrite
            if total_rows is not None and total_rows > existing_count:
                logger.info(f"Target size ({total_rows:,} rows) > existing ({existing_count:,} rows), overwriting...")
                vectors_path.unlink()
                existing_count = 0
            else:
                logger.info(f"Embeddings already complete ({existing_count:,} rows), skipping")
                # Register the space if not already registered
                registry.register_embedding_space(
                    workspace=workspace,
                    name=name,
                    version_hash=version_hash,
                    space_name=space,
                    provider=provider,
                    model=resolved_model or "default",
                    dimension=actual_dimension,
                    distance_metric=distance_metric,
                    storage_path=str(embeddings_dir),
                )
                return vectors_path
        except Exception as e:
            logger.warning(f"Error reading existing embeddings ({e}), will overwrite")
            if vectors_path.exists():
                vectors_path.unlink()
            existing_count = 0

    # Progress bar
    pbar = None
    if show_progress and _tqdm is not None and total_rows is not None:
        desc = f"Embedding {uri.workspace}/{uri.name}:{space}"
        try:
            pbar = _tqdm(total=total_rows, desc=desc, unit="rows")
        except Exception:
            pbar = None

    # Stream rows in batches from DuckDB using LIMIT/OFFSET pages to strictly bound memory
    writer = None
    rows_written = 0

    # Auto-calculate intelligent defaults based on available memory and text size
    def _calculate_smart_defaults():
        try:
            import psutil
            mem = psutil.virtual_memory()
            available_gb = mem.available / (1024**3)

            # Sample text lengths to estimate memory usage
            sample_query = base_query_core + " LIMIT 100"
            try:
                sample_df = engine.conn.execute(sample_query).fetchdf()
                if len(sample_df) > 0:
                    texts = sample_df["text_to_embed"].astype(str)
                    avg_text_bytes = texts.apply(lambda x: len(x.encode('utf-8'))).mean()
                    max_text_bytes = texts.apply(lambda x: len(x.encode('utf-8'))).max()
                else:
                    avg_text_bytes = 1000
                    max_text_bytes = 5000
            except Exception:
                avg_text_bytes = 1000
                max_text_bytes = 5000

            # Estimate memory per row during processing:
            # 1. Text string in Python (UTF-8 + Python object overhead ~50 bytes)
            # 2. Embedding output (dimension × 4 bytes float32)
            # 3. Buffer overhead (lists, arrays, etc.)
            bytes_per_text = avg_text_bytes + 50
            bytes_per_embedding = actual_dimension * 4
            bytes_per_row_buffer = bytes_per_text + bytes_per_embedding + 100

            # Text processing requires much more memory than just storage
            # Account for: batch in RAM, tokenization overhead, model activations
            # Use 3x multiplier for text + tokenization + intermediate tensors
            processing_multiplier = 3.0
            bytes_per_row_processing = bytes_per_text * processing_multiplier

            # Use only 10% of available RAM for buffering (very conservative)
            # This leaves room for model, tokenizer, and CUDA memory
            buffer_memory = available_gb * 0.10 * (1024**3)

            # Calculate max rows based on buffer memory (for write buffer)
            max_buffer_rows = int(buffer_memory / bytes_per_row_buffer)

            # Calculate chunk size based on processing memory
            # We want chunks small enough to process without OOM
            processing_memory = available_gb * 0.15 * (1024**3)
            max_chunk_rows = int(processing_memory / bytes_per_row_processing)

            # Clamp to reasonable ranges based on text size
            # Be extra conservative - multiply text size by 10x for safety
            # (accounts for batch processing, Python overhead, tokenization)
            if avg_text_bytes < 200:  # Very short texts (captions, labels)
                smart_chunk = max(50000, min(max_chunk_rows, 200000))
                smart_write_group = max(100000, min(max_buffer_rows, 500000))
            elif avg_text_bytes < 1000:  # Short texts (tweets, summaries)
                smart_chunk = max(20000, min(max_chunk_rows, 100000))
                smart_write_group = max(50000, min(max_buffer_rows, 200000))
            elif avg_text_bytes < 5000:  # Medium texts (paragraphs, reviews)
                smart_chunk = max(10000, min(max_chunk_rows, 50000))
                smart_write_group = max(30000, min(max_buffer_rows, 100000))
            else:  # Long texts (articles, documents) - very conservative
                smart_chunk = max(5000, min(max_chunk_rows, 20000))
                smart_write_group = max(10000, min(max_buffer_rows, 50000))

            logger.info(f"Auto-tuning: {available_gb:.1f}GB avail, avg_text={avg_text_bytes:.0f}B (max={max_text_bytes:.0f}B), "
                       f"chunk={smart_chunk:,}, write_group={smart_write_group:,}")

            return smart_chunk, smart_write_group
        except Exception as e:
            logger.warning(f"Auto-tuning failed ({e}), using conservative defaults")
            # Fallback to very conservative defaults
            return 20000, 50000

    # Micro-chunk size for the embedding model
    if rows_per_chunk is None:
        smart_chunk, smart_write = _calculate_smart_defaults()
        encode_rows_per_chunk = smart_chunk
    else:
        encode_rows_per_chunk = int(rows_per_chunk)
        smart_write = None

    # Accumulation target for Parquet writes (reduce write overhead)
    if write_rows_per_group is None:
        if smart_write is None:
            smart_write = _calculate_smart_defaults()[1]
        write_group_target = smart_write
    else:
        write_group_target = int(write_rows_per_group)

    # Page size for DuckDB fetch (make larger to reduce disk I/O)
    page_rows = min(encode_rows_per_chunk * 2, 100000)

    # Log the settings being used
    logger.info(f"Embedding settings: rows_per_chunk={encode_rows_per_chunk:,}, write_rows_per_group={write_group_target:,}, page_rows={page_rows:,}")

    to_process = int(total_rows or 0)
    if to_process == 0:
        # Fallback: if count failed for some reason, process in pages until empty
        to_process = 1 << 60  # effectively unlimited; loop will break on empty fetch

    offset = 0
    while offset < to_process:
        page_limit = page_rows if (total_rows is None) else min(page_rows, to_process - offset)
        page_query = base_query_core + f" ORDER BY rid LIMIT {page_limit} OFFSET {offset}"
        try:
            batch_df = engine.conn.execute(page_query).fetchdf()
        except Exception as e:
            # Stop on query errors
            break

        if batch_df is None or len(batch_df) == 0:
            break

        batch_rids = batch_df["rid"].astype("int64").to_numpy()
        batch_texts = batch_df["text_to_embed"].astype(str).tolist()

        # In-memory accumulation buffers to write larger row groups
        buf_rids: list[int] = []
        buf_vecs: list[np.ndarray] = []

        # Process this DataFrame in smaller micro-chunks to avoid large memory spikes
        n = len(batch_texts)
        start = 0
        while start < n:
            end = min(start + encode_rows_per_chunk, n)
            micro_texts = batch_texts[start:end]
            micro_rids = batch_rids[start:end]

            # Compute embeddings for this micro-batch
            try:
                micro_embeddings = embedding_provider.embed(micro_texts, batch_size=batch_size)
            except TypeError:
                micro_embeddings = embedding_provider.embed(micro_texts)

            if micro_embeddings is None or len(micro_embeddings) == 0:
                if pbar is not None:
                    try:
                        pbar.update(len(micro_rids))
                    except Exception:
                        pass
                start = end
                continue

            # Accumulate and flush in larger row groups
            buf_rids.extend([int(x) for x in micro_rids])
            if isinstance(micro_embeddings, np.ndarray):
                buf_vecs.append(micro_embeddings.astype(np.float32, copy=False))
            else:
                buf_vecs.append(np.asarray(micro_embeddings, dtype=np.float32))

            def _flush_buffer():
                nonlocal writer, rows_written, buf_rids, buf_vecs
                if not buf_rids:
                    return
                mat = np.vstack(buf_vecs).astype(np.float32, copy=False)

                # L2-normalize vectors for cosine metric (big win for search speed)
                if distance_metric == "cosine":
                    norms = np.linalg.norm(mat, axis=1, keepdims=True)
                    mat = mat / (norms + 1e-8)

                flat_values = mat.ravel()
                vectors_array = pa.FixedSizeListArray.from_arrays(
                    pa.array(flat_values, type=pa.float32()), list_size=actual_dimension
                )
                table = pa.table({"rid": pa.array(np.array(buf_rids, dtype=np.int64)), "vector": vectors_array})
                if writer is None:
                    writer = pq.ParquetWriter(vectors_path, table.schema, compression='snappy')
                writer.write_table(table)
                rows_written += len(buf_rids)
                # reset buffers
                buf_rids = []
                buf_vecs = []

            if len(buf_rids) >= write_group_target:
                _flush_buffer()

            # Update progress
            if pbar is not None:
                try:
                    pbar.update(len(micro_rids))
                except Exception:
                    pass

            start = end

        # Flush remaining buffered rows for this page
        if buf_rids:
            # function defined above in scope, re-create to avoid mypy issues
            mat = np.vstack(buf_vecs).astype(np.float32, copy=False)

            # L2-normalize vectors for cosine metric
            if distance_metric == "cosine":
                norms = np.linalg.norm(mat, axis=1, keepdims=True)
                mat = mat / (norms + 1e-8)

            flat_values = mat.ravel()
            vectors_array = pa.FixedSizeListArray.from_arrays(
                pa.array(flat_values, type=pa.float32()), list_size=actual_dimension
            )
            table = pa.table({"rid": pa.array(np.array(buf_rids, dtype=np.int64)), "vector": vectors_array})
            if writer is None:
                writer = pq.ParquetWriter(vectors_path, table.schema, compression='snappy')
            writer.write_table(table)
            rows_written += len(buf_rids)
            buf_rids = []
            buf_vecs = []

        # Advance to next page
        offset += len(batch_df)

    if writer is not None:
        writer.close()

    if pbar is not None:
        try:
            pbar.close()
        except Exception:
            pass

    # Handle empty dataset case: create empty vectors file with correct schema
    if rows_written == 0:
        vector_type = pa.list_(pa.float32(), actual_dimension)
        schema = pa.schema([("rid", pa.int64()), ("vector", vector_type)])
        empty_table = pa.table(
            {"rid": pa.array([], type=pa.int64()), "vector": pa.array([], type=vector_type)}
        )
        pq.write_table(empty_table, vectors_path)

    # Build FAISS index using the new index policy
    index_type = None
    index_params = {}
    vectors_normalized = (distance_metric == "cosine")  # Vectors are normalized on write for cosine

    if rows_written > 0:
        try:
            # Create metadata for index builder
            meta = EmbeddingSpaceMeta(
                dataset_id=dataset_id,
                version_hash=version_hash,
                space=space,
                provider=provider,
                model=resolved_model or "default",
                dimension=actual_dimension,
                metric=distance_metric,
                normalized=vectors_normalized,
                row_count=rows_written,
            )

            # Build index using the new policy (HNSW for medium, IVF for large)
            _, index_meta = build_index(
                vectors_path=vectors_path,
                output_dir=embeddings_dir,
                meta=meta,
                normalize_for_cosine=False,  # Already normalized during write
                show_progress=show_progress,
            )
            index_type = index_meta.get("index_type")
            index_params = index_meta.get("params", {})
            logger.info(f"Built {index_type} index for {rows_written:,} vectors")

        except ImportError:
            # FAISS not available, skip index creation
            logger.info("FAISS not installed, skipping index creation")
        except Exception as e:
            logger.warning(f"Index creation failed: {e}")

    # Write space.json for portability
    space_meta = EmbeddingSpaceMeta(
        dataset_id=dataset_id,
        version_hash=version_hash,
        space=space,
        provider=provider,
        model=resolved_model or "default",
        dimension=actual_dimension,
        metric=distance_metric,
        normalized=vectors_normalized,
        row_count=rows_written,
        index_type=index_type,
        index_params=index_params,
        status="ready",
    )
    space_json_path = embeddings_dir / "space.json"
    with open(space_json_path, "w") as f:
        json.dump(space_meta.to_dict(), f, indent=2)

    # Register embedding space in registry with extended metadata
    registry.register_embedding_space(
        workspace=workspace,
        name=name,
        version_hash=version_hash,
        space_name=space,
        provider=provider,
        model=resolved_model or (model or "default"),
        dimension=actual_dimension,
        distance_metric=distance_metric,
        storage_path=str(embeddings_dir),
        # Extended v2 metadata
        row_count=rows_written,
        vector_kind="float32",
        normalized=vectors_normalized,
        index_type=index_type,
        index_params=index_params,
        status="ready",
    )

    return embeddings_dir


def search_embeddings(
    dataset_id: str,
    space: str,
    query: Union[str, List[float]],
    top_k: int = 10,
    distance_metric: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Search embeddings for similar vectors.

    Uses EmbeddingStore for scalable search:
    1. FAISS index if present (HNSW or IVF for large spaces)
    2. Brute force in RAM if data fits
    3. Chunked brute force for large spaces without index

    Args:
        dataset_id: Dataset ID (supports shorthand like 'nlp/reviews')
        space: Embedding space name
        query: Query (text string or vector)
        top_k: Number of results to return
        distance_metric: Distance metric (uses space's metric if not specified)

    Returns:
        List of search results with 'rid', 'score', and 'distance'

    Examples:
        >>> import warpdata as wd
        >>> results = wd.search_embeddings(
        ...     "nlp/reviews",  # Shorthand also works
        ...     space="openai-ada",
        ...     query="Great product, highly recommend!",
        ...     top_k=5
        ... )
    """
    # Resolve dataset ID (must be warpdata://, not a file)
    dataset_id = require_warpdata_id(dataset_id)
    uri = parse_uri(dataset_id)

    workspace = uri.workspace
    name = uri.name
    version = uri.version or "latest"

    # Get embedding space info (use readonly registry)
    registry = get_registry_readonly()
    dataset_ver = registry.get_dataset_version(workspace, name, version)

    if dataset_ver is None:
        raise ValueError(f"Dataset not found: {dataset_id}")

    version_hash = dataset_ver["version_hash"]

    # Get embedding space
    spaces = registry.list_embedding_spaces(workspace, name, version_hash)
    space_info = next((s for s in spaces if s["space_name"] == space), None)

    if space_info is None:
        raise ValueError(f"Embedding space '{space}' not found for dataset {dataset_id}")

    # If query is a string, embed it
    if isinstance(query, str):
        provider = get_provider(
            provider=space_info["provider"],
            model=space_info["model"],
            dimension=space_info["dimension"],
        )
        query_vector = provider.embed([query])[0]
    else:
        query_vector = np.array(query, dtype=np.float32)

    # Validate query vector dimension
    expected_dim = space_info["dimension"]
    if query_vector.shape[0] != expected_dim:
        raise ValueError(
            f"Query vector dimension mismatch: expected {expected_dim}, "
            f"got {query_vector.shape[0]} for embedding space '{space}'"
        )

    # Use provided distance metric or fall back to space's metric
    metric = distance_metric or space_info["distance_metric"]

    # Open EmbeddingStore and search
    storage_path = Path(space_info["storage_path"])
    store = open_embedding_store(storage_path)

    # Use the store's scalable search (handles FAISS index, brute force, chunked)
    results = store.search(query_vector, top_k=top_k, metric=metric)

    # Convert SearchResult objects to dicts
    return [r.to_dict() for r in results]


def load_embeddings(
    dataset_id: str,
    *,
    space: str,
    rids: Optional[List[int]] = None,
    as_numpy: bool = True,
    return_rids: bool = False,
) -> Union[np.ndarray, List[List[float]], Tuple[List[int], np.ndarray], Tuple[List[int], List[List[float]]]]:
    """
    Load embedding vectors for a dataset and space.

    Uses zero-copy Arrow buffer reads for efficiency (no Python list conversion).

    Args:
        dataset_id: Dataset ID (e.g., 'warpdata://vision/celeba-attrs' or shorthand 'vision/celeba-attrs')
        space: Embedding space name to load
        rids: Optional list of row IDs to subset and (re)order
        as_numpy: If True, return a NumPy array of shape (N, dim); otherwise a list of lists
        return_rids: If True, return (rids, vectors)

    Returns:
        Vectors as np.ndarray or list of lists. If return_rids=True, also returns the corresponding rid list.
    """
    # Resolve dataset ID (must be warpdata://, not a file)
    dataset_id = require_warpdata_id(dataset_id)
    uri = parse_uri(dataset_id)

    workspace = uri.workspace
    name = uri.name
    version = uri.version or "latest"

    registry = get_registry_readonly()
    dataset_ver = registry.get_dataset_version(workspace, name, version)
    if dataset_ver is None:
        raise ValueError(
            (
                f"Dataset not found: {dataset_id}.\n"
                f"• Check it exists: warp list | rg '{workspace}/{name}'\n"
                f"• If you meant a shorthand, use full ID: warpdata://{workspace}/{name}"
            )
        )
    version_hash = dataset_ver["version_hash"]

    # Discover embedding space and storage
    spaces = registry.list_embedding_spaces(workspace, name, version_hash)
    wanted = next((s for s in spaces if s.get("space_name") == space), None)
    if not wanted:
        available = ", ".join(sorted(s.get("space_name") for s in spaces)) if spaces else "none"
        raise ValueError(
            (
                f"Embedding space '{space}' not found for {dataset_id}.\n"
                f"• Available spaces: {available}\n"
                f"• Add embeddings: warp embeddings run {workspace}/{name} --space {space}\n"
                f"  or in Python: wd.add_embeddings('{workspace}/{name}', space='{space}', provider='sentence-transformers', source={{'columns':['text']}})"
            )
        )

    storage_path = wanted.get("storage_path")
    if not storage_path:
        raise FileNotFoundError(
            (
                f"Embedding space '{space}' for {dataset_id} is registered without a storage_path.\n"
                f"Recreate the space locally: warp embeddings run {workspace}/{name} --space {space}"
            )
        )

    vectors_path = Path(storage_path) / "vectors.parquet"
    if not vectors_path.exists():
        raise FileNotFoundError(
            (
                f"Missing vectors for {dataset_id} space='{space}'.\n"
                f"Expected file: {vectors_path}\n"
                f"This usually means the embeddings were computed on another machine or the cache was cleared.\n"
                f"Fix: recompute locally → warp embeddings run {workspace}/{name} --space {space}"
            )
        )

    # Open EmbeddingStore for zero-copy reads
    store = open_embedding_store(Path(storage_path))
    dim = store.meta().dimension

    # Use store for efficient loading
    if rids is not None and len(rids) > 0:
        # Use store's get_vectors for filtered access
        arr = store.get_vectors(rids)
        rid_col = list(rids)  # Preserve input order
    else:
        # Load all using zero-copy Arrow buffer reshape (fast path)
        rid_col = store.all_rids().tolist()
        arr = store.all_vectors()

    if as_numpy:
        if return_rids:
            return list(map(int, rid_col)), arr
        return arr
    else:
        # Convert to list of lists if needed
        vecs_list = arr.tolist()
        if return_rids:
            return list(map(int, rid_col)), vecs_list
        return vecs_list


def join_results(
    dataset_id: str,
    rids: List[int],
    columns: Optional[List[str]] = None,
    as_format: str = "pandas",
) -> Any:
    """
    Join search results back to original dataset data.

    IMPORTANT: Preserves the order of rids (ranking order from search results).

    Args:
        dataset_id: Dataset ID (supports shorthand like 'nlp/reviews')
        rids: List of row IDs to retrieve (order is preserved!)
        columns: Columns to retrieve (all if not specified)
        as_format: Output format ('pandas', 'duckdb', 'polars')

    Returns:
        Data in requested format, ordered by input rids

    Examples:
        >>> import warpdata as wd
        >>> results = wd.search_embeddings(..., top_k=5)
        >>> rids = [r["rid"] for r in results]
        >>> data = wd.join_results(dataset_id, rids=rids, columns=["text", "label"])
        >>> # data is ordered by search ranking, not by rid
    """
    # Resolve dataset ID (must be warpdata://, not a file)
    dataset_id = require_warpdata_id(dataset_id)
    uri = parse_uri(dataset_id)

    registry = get_registry_readonly()
    dataset_ver = registry.get_dataset_version(uri.workspace, uri.name, uri.version or "latest")

    if dataset_ver is None:
        raise ValueError(f"Dataset not found: {dataset_id}")

    # Determine path of materialized file without running materialization
    cache = get_cache()
    dataset_cache_dir = cache.get_dataset_cache_dir(
        uri.workspace, uri.name, dataset_ver["version_hash"]
    )
    materialized_path = dataset_cache_dir / "materialized.parquet"

    # Materialize only if file doesn't exist (avoid re-registering to prevent duplicate versions)
    if not materialized_path.exists():
        from .management import materialize
        materialize(dataset_id, output_path=materialized_path, update_registry=False)

    # Load with DuckDB
    from ..engine.duck import get_engine

    engine = get_engine()

    # Handle empty rids list
    if not rids:
        # Return empty result with correct schema
        if columns:
            cols_str = ", ".join(f'"{c}"' for c in columns)
            query = f"SELECT {cols_str} FROM read_parquet('{materialized_path}') LIMIT 0"
        else:
            query = f"SELECT * FROM read_parquet('{materialized_path}') LIMIT 0"
        relation = engine.conn.sql(query)
    else:
        # Use ARRAY_POSITION to preserve ranking order (critical for search results!)
        # This ensures results come back in the same order as the input rids
        if columns:
            cols_str = ", ".join(f'"{c}"' for c in columns)
            query = f"""
            SELECT {cols_str}
            FROM read_parquet('{materialized_path}')
            WHERE rid IN (SELECT UNNEST(?))
            ORDER BY ARRAY_POSITION(?, rid)
            """
        else:
            query = f"""
            SELECT *
            FROM read_parquet('{materialized_path}')
            WHERE rid IN (SELECT UNNEST(?))
            ORDER BY ARRAY_POSITION(?, rid)
            """

        # Execute with parameterized rids (passed twice for WHERE and ORDER BY)
        df = engine.conn.execute(query, [rids, rids]).fetchdf()
        # Convert to DuckDB relation for consistency
        relation = engine.conn.from_df(df)

    # Convert to requested format
    if as_format == "duckdb":
        return relation
    elif as_format == "pandas":
        return engine.to_df(relation, "pandas")
    elif as_format == "polars":
        return engine.to_df(relation, "polars")
    else:
        raise ValueError(f"Unsupported format: {as_format}")


def list_embeddings(dataset_id: str, all_versions: bool = False) -> List[Dict[str, Any]]:
    """
    List all embedding spaces for a dataset.

    Returns extended metadata including row_count, vector_kind, normalized, index_type, status.

    Args:
        dataset_id: Dataset ID (supports shorthand like 'nlp/reviews')
        all_versions: If True, list spaces across all versions

    Returns:
        List of embedding space info dictionaries with extended metadata

    Examples:
        >>> import warpdata as wd
        >>> spaces = wd.list_embeddings("nlp/reviews")  # Shorthand works
        >>> for space in spaces:
        ...     print(f"{space['space_name']}: {space['dimension']}d, {space.get('row_count', '?')} vectors")
    """
    # Resolve dataset ID (must be warpdata://, not a file)
    dataset_id = require_warpdata_id(dataset_id)
    uri = parse_uri(dataset_id)

    workspace = uri.workspace
    name = uri.name
    version = uri.version or "latest"

    # Get dataset version (use readonly registry)
    registry = get_registry_readonly()
    if all_versions:
        # List spaces across all versions
        return registry.list_embedding_spaces_for_dataset(workspace, name)
    else:
        dataset_ver = registry.get_dataset_version(workspace, name, version)
        if dataset_ver is None:
            raise ValueError(f"Dataset not found: {dataset_id}")
        version_hash = dataset_ver["version_hash"]
        return registry.list_embedding_spaces(workspace, name, version_hash)


def remove_embeddings(dataset_id: str, space: str, delete_files: bool = False) -> None:
    """
    Remove an embedding space from a dataset's current version.

    Args:
        dataset_id: Dataset ID (supports shorthand like 'nlp/reviews', optionally pin a version with @hash)
        space: Space name to remove
        delete_files: If True, delete the storage directory on disk
    """
    # Resolve dataset ID (must be warpdata://, not a file)
    dataset_id = require_warpdata_id(dataset_id)
    uri = parse_uri(dataset_id)

    workspace = uri.workspace
    name = uri.name
    version = uri.version or "latest"

    registry = get_registry()
    dataset_ver = registry.get_dataset_version(workspace, name, version)
    if dataset_ver is None:
        raise ValueError(f"Dataset not found: {dataset_id}")
    version_hash = dataset_ver["version_hash"]

    # Fetch storage path before removal
    row = registry.get_embedding_space(workspace, name, version_hash, space)
    storage_path = row.get("storage_path") if row else None

    # Remove from registry
    registry.remove_embedding_space(workspace, name, version_hash, space)

    # Optionally delete files
    if delete_files and storage_path:
        p = Path(storage_path)
        if p.exists():
            import shutil
            shutil.rmtree(p, ignore_errors=True)


def migrate_embeddings_to_latest(
    dataset_id: str,
    move: bool = False,
    copy: bool = False,
) -> List[Dict[str, Any]]:
    """
    Migrate existing embedding spaces from older versions to the latest version
    without recomputation.

    If copy/move are False (default), this will register the existing storage_path
    under the latest version (no disk IO). If move=True, move directories into the
    latest version's embeddings folder and re-register; if copy=True, copy instead.

    Args:
        dataset_id: Dataset ID (supports shorthand like 'nlp/reviews')
        move: If True, move embedding directories to latest version
        copy: If True, copy embedding directories to latest version

    Returns a list of dicts describing migrated spaces.
    """
    if move and copy:
        raise ValueError("Specify only one of move or copy")

    # Resolve dataset ID (must be warpdata://, not a file)
    dataset_id = require_warpdata_id(dataset_id)
    uri = parse_uri(dataset_id)

    workspace = uri.workspace
    name = uri.name
    version = uri.version or "latest"

    registry = get_registry()
    latest = registry.get_dataset_version(workspace, name, version)
    if latest is None:
        raise ValueError(f"Dataset not found: {dataset_id}")
    latest_hash = latest["version_hash"]

    # Spaces on latest
    latest_spaces = {s["space_name"]: s for s in registry.list_embedding_spaces(workspace, name, latest_hash)}

    # Spaces across all versions
    all_spaces = registry.list_embedding_spaces_for_dataset(workspace, name)

    cache = get_cache()
    latest_dir = cache.get_dataset_cache_dir(workspace, name, latest_hash) / "embeddings"
    latest_dir.mkdir(parents=True, exist_ok=True)

    migrated = []
    for row in all_spaces:
        vh = row["version_hash"]
        space = row["space_name"]
        if vh == latest_hash:
            continue  # already on latest
        if space in latest_spaces:
            continue  # already exists on latest with same space name

        src_path = Path(row["storage_path"]).resolve()
        dst_path = src_path
        if move or copy:
            dst_path = latest_dir / space
            # Avoid overwriting
            if dst_path.exists():
                # pick a unique suffix
                i = 1
                while (latest_dir / f"{space}-{i}").exists():
                    i += 1
                dst_path = latest_dir / f"{space}-{i}"
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            import shutil
            if copy:
                shutil.copytree(src_path, dst_path)
            else:
                shutil.move(str(src_path), str(dst_path))

        # Register under latest
        registry.register_embedding_space(
            workspace=workspace,
            name=name,
            version_hash=latest_hash,
            space_name=space,
            provider=row["provider"],
            model=row["model"],
            dimension=row["dimension"],
            distance_metric=row["distance_metric"],
            storage_path=str(dst_path),
        )

        # If moved, remove old registry row
        if move:
            registry.remove_embedding_space(workspace, name, vh, space)

        migrated.append({
            "space": space,
            "from_version": vh,
            "to_version": latest_hash,
            "storage_path": str(dst_path),
            "provider": row["provider"],
            "model": row["model"],
        })

    return migrated
