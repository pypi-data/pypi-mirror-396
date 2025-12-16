"""
FAISS index building with intelligent policy selection.

Supports:
- IndexFlatIP/L2 for small datasets (exact search)
- IndexHNSWFlat for medium datasets (fast approximate)
- IVF for large datasets (requires training)
"""
from __future__ import annotations
import json
import logging
from pathlib import Path
from typing import Optional, Tuple
import numpy as np

from .types import EmbeddingSpaceMeta, IndexType, Metric
from .parquet_store import _read_vectors_fast

logger = logging.getLogger(__name__)


# Thresholds for index type selection
FLAT_MAX_ROWS = 100_000  # Use flat index for datasets < 100K rows
HNSW_MAX_ROWS = 2_000_000  # Use HNSW for datasets < 2M rows
# Above 2M: use IVF (requires training)


def select_index_type(
    row_count: int,
    dimension: int,
    metric: Metric,
    force_type: Optional[IndexType] = None,
) -> Tuple[IndexType, dict]:
    """
    Select the best index type based on data size.

    Args:
        row_count: Number of vectors
        dimension: Vector dimension
        metric: Distance metric
        force_type: Override automatic selection

    Returns:
        Tuple of (IndexType, params_dict)
    """
    if force_type:
        return force_type, _default_params(force_type, row_count, dimension)

    # Binary metrics use binary indexes
    if metric in ("hamming", "jaccard"):
        if row_count <= HNSW_MAX_ROWS:
            return "binary_flat", {}
        return "binary_ivf", {"nlist": min(int(np.sqrt(row_count)), 4096)}

    # Float metrics
    if row_count <= FLAT_MAX_ROWS:
        return "flat", {}

    if row_count <= HNSW_MAX_ROWS:
        # HNSW: good tradeoff between speed and accuracy
        return "hnsw", {
            "M": 32,  # Number of connections per layer
            "efConstruction": 200,  # Construction-time search depth
            "efSearch": 64,  # Query-time search depth
        }

    # Large dataset: use IVF
    nlist = min(int(np.sqrt(row_count)), 4096)
    return "ivf_flat", {
        "nlist": nlist,
        "nprobe": min(nlist // 4, 64),  # Query-time clusters to search
    }


def _default_params(index_type: IndexType, row_count: int, dimension: int) -> dict:
    """Get default parameters for an index type."""
    if index_type == "flat":
        return {}
    elif index_type == "hnsw":
        return {"M": 32, "efConstruction": 200, "efSearch": 64}
    elif index_type in ("ivf_flat", "ivf_pq"):
        nlist = min(int(np.sqrt(row_count)), 4096)
        return {"nlist": nlist, "nprobe": min(nlist // 4, 64)}
    elif index_type == "binary_flat":
        return {}
    elif index_type == "binary_ivf":
        nlist = min(int(np.sqrt(row_count)), 4096)
        return {"nlist": nlist}
    return {}


def build_index(
    vectors_path: Path,
    output_dir: Path,
    meta: EmbeddingSpaceMeta,
    force_type: Optional[IndexType] = None,
    normalize_for_cosine: bool = True,
    show_progress: bool = True,
) -> Tuple[Path, dict]:
    """
    Build a FAISS index for an embedding space.

    Args:
        vectors_path: Path to vectors.parquet
        output_dir: Directory to write index files
        meta: Embedding space metadata
        force_type: Override automatic index type selection
        normalize_for_cosine: L2-normalize vectors before indexing for cosine
        show_progress: Show progress bar

    Returns:
        Tuple of (index_path, index_metadata)
    """
    try:
        import faiss
    except ImportError:
        raise ImportError(
            "FAISS is not installed. Install with: pip install faiss-cpu "
            "or pip install faiss-gpu"
        )

    # Select index type
    index_type, params = select_index_type(
        meta.row_count, meta.dimension, meta.metric, force_type
    )

    logger.info(
        f"Building {index_type} index for {meta.row_count:,} vectors "
        f"(dim={meta.dimension}, metric={meta.metric})"
    )

    # Load vectors
    rids, X = _read_vectors_fast(vectors_path, meta.dimension)

    # Normalize for cosine similarity
    normalized = False
    if meta.metric == "cosine" and normalize_for_cosine:
        norms = np.linalg.norm(X, axis=1, keepdims=True)
        X = X / (norms + 1e-8)
        normalized = True
        logger.info("Normalized vectors for cosine similarity")

    # Build index based on type
    if index_type == "flat":
        index = _build_flat_index(X, meta.metric, meta.dimension)
    elif index_type == "hnsw":
        index = _build_hnsw_index(X, meta.metric, meta.dimension, params)
    elif index_type == "ivf_flat":
        index = _build_ivf_index(X, meta.metric, meta.dimension, params, show_progress)
    else:
        # Fallback to flat
        logger.warning(f"Index type {index_type} not implemented, using flat")
        index = _build_flat_index(X, meta.metric, meta.dimension)
        index_type = "flat"

    # Write index
    index_path = output_dir / "index.faiss"
    faiss.write_index(index, str(index_path))

    # Write index metadata
    index_meta = {
        "index_type": index_type,
        "metric": meta.metric,
        "dimension": meta.dimension,
        "row_count": meta.row_count,
        "normalized": normalized,
        "params": params,
    }

    index_json_path = output_dir / "index.json"
    with open(index_json_path, "w") as f:
        json.dump(index_meta, f, indent=2)

    logger.info(f"Wrote index to {index_path}")

    return index_path, index_meta


def _build_flat_index(
    X: np.ndarray,
    metric: Metric,
    dimension: int,
) -> "faiss.Index":
    """Build a flat (exact) index."""
    import faiss

    if metric in ("cosine", "dot"):
        # Inner product after normalization
        index = faiss.IndexFlatIP(dimension)
    else:
        # L2 distance
        index = faiss.IndexFlatL2(dimension)

    index.add(X.astype(np.float32))
    return index


def _build_hnsw_index(
    X: np.ndarray,
    metric: Metric,
    dimension: int,
    params: dict,
) -> "faiss.Index":
    """Build an HNSW index (fast approximate search)."""
    import faiss

    M = params.get("M", 32)
    ef_construction = params.get("efConstruction", 200)

    # HNSW with inner product or L2
    if metric in ("cosine", "dot"):
        index = faiss.IndexHNSWFlat(dimension, M, faiss.METRIC_INNER_PRODUCT)
    else:
        index = faiss.IndexHNSWFlat(dimension, M, faiss.METRIC_L2)

    # Set construction parameters
    index.hnsw.efConstruction = ef_construction

    # Add vectors
    index.add(X.astype(np.float32))

    # Set search parameters
    index.hnsw.efSearch = params.get("efSearch", 64)

    return index


def _build_ivf_index(
    X: np.ndarray,
    metric: Metric,
    dimension: int,
    params: dict,
    show_progress: bool = True,
) -> "faiss.Index":
    """Build an IVF index (scalable approximate search)."""
    import faiss

    nlist = params.get("nlist", min(int(np.sqrt(len(X))), 4096))

    logger.info(f"Training IVF index with {nlist} clusters...")

    # Create quantizer
    if metric in ("cosine", "dot"):
        quantizer = faiss.IndexFlatIP(dimension)
        index = faiss.IndexIVFFlat(
            quantizer, dimension, nlist, faiss.METRIC_INNER_PRODUCT
        )
    else:
        quantizer = faiss.IndexFlatL2(dimension)
        index = faiss.IndexIVFFlat(quantizer, dimension, nlist, faiss.METRIC_L2)

    # Train on sample if dataset is large
    train_size = min(len(X), nlist * 256)  # At least 256 vectors per cluster
    if train_size < len(X):
        # Random sample for training
        indices = np.random.choice(len(X), train_size, replace=False)
        train_data = X[indices].astype(np.float32)
    else:
        train_data = X.astype(np.float32)

    index.train(train_data)

    # Add all vectors
    index.add(X.astype(np.float32))

    # Set search parameter
    index.nprobe = params.get("nprobe", min(nlist // 4, 64))

    return index


def remove_index(storage_path: Path) -> bool:
    """
    Remove index files from an embedding space.

    Args:
        storage_path: Path to embeddings/<space>/ directory

    Returns:
        True if files were removed
    """
    index_path = storage_path / "index.faiss"
    index_json_path = storage_path / "index.json"

    removed = False
    if index_path.exists():
        index_path.unlink()
        removed = True
    if index_json_path.exists():
        index_json_path.unlink()
        removed = True

    return removed
