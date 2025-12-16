"""
Parquet-based embedding store implementation.

Provides zero-copy reads, chunked iteration, and scalable search.
"""
from __future__ import annotations
import json
import logging
from pathlib import Path
from typing import Iterable, List, Optional, Tuple
import numpy as np

import pyarrow as pa
import pyarrow.parquet as pq
import pyarrow.dataset as ds

from .store import EmbeddingStore
from .types import (
    EmbeddingSpaceMeta,
    VectorBatch,
    FloatBatch,
    BinaryBatch,
    SearchResult,
    Metric,
)

logger = logging.getLogger(__name__)


# Memory threshold for brute-force search (2GB default)
BRUTE_FORCE_MAX_BYTES = 2 * 1024**3

# Popcount lookup table for binary vector Hamming distance
_popcount_table = np.array([bin(i).count('1') for i in range(256)], dtype=np.uint8)


def _read_vectors_fast(
    vectors_path: Path,
    dim: int,
    columns: Optional[List[str]] = None,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Read vectors using zero-copy Arrow buffer reshape.

    This is much faster than to_pylist() for FixedSizeList<float32>.

    Args:
        vectors_path: Path to vectors.parquet
        dim: Vector dimension
        columns: Columns to read (default: ["rid", "vector"])

    Returns:
        Tuple of (rids[int64], vectors[float32])
    """
    cols = columns or ["rid", "vector"]
    tbl = pq.read_table(vectors_path, columns=cols)

    # Extract rids
    rid = tbl["rid"].combine_chunks().to_numpy(zero_copy_only=False)
    rid = rid.astype(np.int64, copy=False)

    # Extract vectors - FixedSizeListArray's .values is a flat Float32Array
    vec_arr = tbl["vector"].combine_chunks()
    flat = vec_arr.values.to_numpy(zero_copy_only=False)
    flat = flat.astype(np.float32, copy=False)
    X = flat.reshape(-1, dim)

    return rid, X


def _topk_merge(
    best_d: np.ndarray,
    best_i: np.ndarray,
    new_d: np.ndarray,
    new_i: np.ndarray,
    k: int,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Merge two top-k result sets, keeping smallest distances.

    Args:
        best_d, best_i: Current best distances and indices
        new_d, new_i: New candidate distances and indices
        k: Number of results to keep

    Returns:
        Merged (distances, indices) arrays of length k
    """
    d = np.concatenate([best_d, new_d])
    i = np.concatenate([best_i, new_i])

    # Use argpartition for O(n) selection
    n = len(d)
    if n <= k:
        idx = np.argsort(d)
        return d[idx], i[idx]

    idx = np.argpartition(d, k)[:k]
    ord_idx = idx[np.argsort(d[idx])]
    return d[ord_idx], i[ord_idx]


class ParquetEmbeddingStore(EmbeddingStore):
    """
    Parquet-based embedding store with zero-copy reads and scalable search.

    On-disk layout:
        embeddings/<space>/
            vectors.parquet   # rid:int64, vector:fixed_size_list(float32, dim)
            space.json        # Metadata snapshot
            index.faiss       # Optional FAISS index
            index.json        # Index metadata
    """

    def __init__(self, storage_path: Path):
        """
        Open an embedding store from a directory.

        Args:
            storage_path: Path to embeddings/<space>/ directory
        """
        self._path = Path(storage_path)
        self._vectors_path = self._path / "vectors.parquet"
        self._space_json_path = self._path / "space.json"
        self._index_path = self._path / "index.faiss"
        self._index_json_path = self._path / "index.json"

        # Load or infer metadata
        self._meta = self._load_meta()

        # Lazy-loaded resources
        self._faiss_index = None
        self._index_meta: dict = {}

    def _load_meta(self) -> EmbeddingSpaceMeta:
        """Load metadata from space.json or infer from parquet."""
        # Try space.json first (portable)
        if self._space_json_path.exists():
            with open(self._space_json_path) as f:
                data = json.load(f)
            return EmbeddingSpaceMeta.from_dict(data)

        # Infer from parquet file
        if not self._vectors_path.exists():
            raise FileNotFoundError(f"No vectors.parquet found at {self._path}")

        # Read schema to get dimension
        schema = pq.read_schema(self._vectors_path)
        vec_field = schema.field("vector")

        # FixedSizeListType has list_size attribute
        if hasattr(vec_field.type, "list_size"):
            dim = vec_field.type.list_size
        else:
            # Fallback: read first row
            tbl = pq.read_table(self._vectors_path, columns=["vector"])
            if len(tbl) > 0:
                dim = len(tbl["vector"][0].as_py())
            else:
                dim = 0

        # Get row count from parquet metadata
        pf = pq.ParquetFile(self._vectors_path)
        row_count = pf.metadata.num_rows

        # Detect if normalized by checking norms
        normalized = self._detect_normalized(dim)

        return EmbeddingSpaceMeta(
            dataset_id="",
            version_hash="",
            space=self._path.name,
            provider="unknown",
            model="unknown",
            vector_kind="float32",
            dimension=dim,
            metric="cosine",
            normalized=normalized,
            row_count=row_count,
            status="ready",
        )

    def _detect_normalized(self, dim: int, sample_size: int = 100) -> bool:
        """Detect if vectors are L2-normalized by sampling."""
        if dim == 0:
            return False

        try:
            # Read sample
            tbl = pq.read_table(self._vectors_path, columns=["vector"])
            n = min(sample_size, len(tbl))
            if n == 0:
                return False

            vec_arr = tbl["vector"].slice(0, n).combine_chunks()
            flat = vec_arr.values.to_numpy(zero_copy_only=False).astype(np.float32)
            X = flat.reshape(-1, dim)

            # Check norms
            norms = np.linalg.norm(X, axis=1)
            return bool(np.allclose(norms, 1.0, atol=1e-4))
        except Exception:
            return False

    def _load_faiss_index(self):
        """Lazy-load FAISS index if available."""
        if self._faiss_index is not None:
            return self._faiss_index

        if not self._index_path.exists():
            return None

        try:
            import faiss
            self._faiss_index = faiss.read_index(str(self._index_path))

            # Load index metadata
            if self._index_json_path.exists():
                with open(self._index_json_path) as f:
                    self._index_meta = json.load(f)

            return self._faiss_index
        except ImportError:
            logger.warning("FAISS not installed, falling back to brute force search")
            return None
        except Exception as e:
            logger.warning(f"Failed to load FAISS index: {e}")
            return None

    def meta(self) -> EmbeddingSpaceMeta:
        """Get metadata for this embedding space."""
        return self._meta

    def get_vectors(self, rids: List[int]) -> np.ndarray:
        """
        Get vectors for specific row IDs using DuckDB filtering.

        Uses DuckDB for efficient filtering with ARRAY_POSITION to preserve order.
        """
        if not rids:
            return np.array([], dtype=np.float32).reshape(0, self._meta.dimension)

        # Use DuckDB for efficient filtering
        try:
            import duckdb

            query = f"""
            SELECT rid, vector
            FROM read_parquet('{self._vectors_path}')
            WHERE rid IN (SELECT UNNEST(?))
            ORDER BY ARRAY_POSITION(?, rid)
            """
            result = duckdb.execute(query, [rids, rids]).fetchdf()

            if len(result) == 0:
                return np.array([], dtype=np.float32).reshape(0, self._meta.dimension)

            # Convert vectors
            vecs = np.array(result["vector"].tolist(), dtype=np.float32)
            return vecs

        except Exception as e:
            logger.warning(f"DuckDB filtering failed: {e}, falling back to full scan")
            # Fallback: load all and filter
            all_rids, all_vecs = _read_vectors_fast(
                self._vectors_path, self._meta.dimension
            )
            rid_to_idx = {int(r): i for i, r in enumerate(all_rids)}
            indices = [rid_to_idx[r] for r in rids if r in rid_to_idx]
            return all_vecs[indices]

    def iter_vectors(
        self,
        batch_rows: int = 200_000,
        columns: Optional[List[str]] = None,
    ) -> Iterable[VectorBatch]:
        """
        Iterate over vectors in batches using PyArrow dataset scanning.

        This enables processing arbitrarily large embedding spaces
        without loading everything into RAM.
        """
        dim = self._meta.dimension
        cols = columns or ["rid", "vector"]

        # Use PyArrow dataset for batched reading
        dataset = ds.dataset(str(self._vectors_path), format="parquet")

        for batch in dataset.to_batches(columns=cols, batch_size=batch_rows):
            # Extract rids
            rid_col = batch.column(batch.schema.get_field_index("rid"))
            rid = rid_col.to_numpy(zero_copy_only=False).astype(np.int64, copy=False)

            # Extract vectors
            vec_col = batch.column(batch.schema.get_field_index("vector"))

            # For RecordBatch, the column is already a single array
            # (not ChunkedArray like Table), but handle both cases
            if hasattr(vec_col, "combine_chunks"):
                vec_col = vec_col.combine_chunks()

            flat = vec_col.values.to_numpy(zero_copy_only=False)
            flat = flat.astype(np.float32, copy=False)
            X = flat.reshape(-1, dim)

            yield FloatBatch(rids=rid, vectors=X)

    def all_vectors(self) -> np.ndarray:
        """Load all vectors into RAM."""
        _, X = _read_vectors_fast(self._vectors_path, self._meta.dimension)
        return X

    def all_rids(self) -> np.ndarray:
        """Get all row IDs."""
        rids, _ = _read_vectors_fast(self._vectors_path, self._meta.dimension)
        return rids

    def search(
        self,
        query: np.ndarray,
        top_k: int = 10,
        metric: Optional[str] = None,
    ) -> List[SearchResult]:
        """
        Search for similar vectors using the best available method.

        Strategy:
        1. FAISS index if present and metric matches
        2. Brute force in RAM if data fits
        3. Chunked brute force for large spaces
        """
        query = np.asarray(query, dtype=np.float32).ravel()
        use_metric: Metric = metric or self._meta.metric  # type: ignore

        # Validate dimension
        if len(query) != self._meta.dimension:
            raise ValueError(
                f"Query dimension {len(query)} != space dimension {self._meta.dimension}"
            )

        # 1. Try FAISS index
        index = self._load_faiss_index()
        if index is not None:
            # Check if metric matches
            index_metric = self._index_meta.get("metric", self._meta.metric)
            if index_metric == use_metric:
                return self._search_faiss(query, top_k, use_metric)
            else:
                logger.debug(
                    f"Index metric {index_metric} != requested {use_metric}, "
                    "using brute force"
                )

        # 2. Check if data fits in RAM for brute force
        estimated_bytes = self._meta.row_count * self._meta.dimension * 4
        if estimated_bytes <= BRUTE_FORCE_MAX_BYTES:
            return self._search_brute_force(query, top_k, use_metric)

        # 3. Chunked brute force for large spaces
        return self._search_chunked(query, top_k, use_metric)

    def _search_faiss(
        self,
        query: np.ndarray,
        top_k: int,
        metric: Metric,
    ) -> List[SearchResult]:
        """Search using FAISS index."""
        index = self._faiss_index
        if index is None:
            raise RuntimeError("FAISS index not loaded")

        # Normalize query for cosine similarity (index uses inner product)
        if metric == "cosine":
            query = query / (np.linalg.norm(query) + 1e-8)

        # FAISS search
        query_2d = query.reshape(1, -1).astype(np.float32)
        scores, indices = index.search(query_2d, top_k)

        # Load rids for mapping indices -> actual rids
        all_rids = self.all_rids()

        results = []
        for idx, score in zip(indices[0], scores[0]):
            if idx < 0 or idx >= len(all_rids):
                continue

            rid = int(all_rids[idx])

            # Convert FAISS score to distance
            if metric == "cosine":
                # IndexFlatIP returns inner product (similarity)
                distance = 1.0 - float(score)
            else:
                # IndexFlatL2 returns squared L2 distance
                distance = float(score) ** 0.5

            results.append(SearchResult(
                rid=rid,
                distance=distance,
                score=1.0 / (1.0 + distance),
            ))

        return results

    def _search_brute_force(
        self,
        query: np.ndarray,
        top_k: int,
        metric: Metric,
    ) -> List[SearchResult]:
        """Brute force search with all vectors in RAM."""
        rids, X = _read_vectors_fast(self._vectors_path, self._meta.dimension)

        # Compute distances
        distances = self._compute_distances(query, X, metric)

        # Get top-k
        k = min(top_k, len(distances))
        top_indices = np.argpartition(distances, k - 1)[:k]
        top_indices = top_indices[np.argsort(distances[top_indices])]

        results = []
        for idx in top_indices:
            d = float(distances[idx])
            results.append(SearchResult(
                rid=int(rids[idx]),
                distance=d,
                score=1.0 / (1.0 + d),
            ))

        return results

    def _search_chunked(
        self,
        query: np.ndarray,
        top_k: int,
        metric: Metric,
        batch_rows: int = 200_000,
    ) -> List[SearchResult]:
        """
        Chunked brute force search for large spaces.

        Processes vectors in batches to avoid OOM.
        Supports both float and binary vectors.
        """
        # Handle binary metrics
        if metric in ("hamming", "jaccard"):
            return self._search_chunked_binary(query, top_k, metric, batch_rows)

        # Normalize query for cosine
        if metric == "cosine":
            query = query / (np.linalg.norm(query) + 1e-8)

        # Initialize best results
        best_d = np.full(top_k, np.inf, dtype=np.float32)
        best_r = np.full(top_k, -1, dtype=np.int64)

        for batch in self.iter_vectors(batch_rows=batch_rows):
            X = batch.vectors
            rids = batch.rids

            # Compute distances for this batch
            if metric == "cosine":
                # If vectors are normalized, just use inner product
                if self._meta.normalized:
                    sims = X @ query
                else:
                    X_norm = X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)
                    sims = X_norm @ query
                d = (1.0 - sims).astype(np.float32)
            elif metric == "euclidean":
                d = np.linalg.norm(X - query, axis=1).astype(np.float32)
            elif metric == "dot":
                # Higher dot product = more similar, so negate
                d = (-X @ query).astype(np.float32)
            else:
                # Default to euclidean
                d = np.linalg.norm(X - query, axis=1).astype(np.float32)

            # Get top-k from this batch
            k = min(top_k, len(d))
            if k == 0:
                continue

            idx = np.argpartition(d, k - 1)[:k]
            cand_d = d[idx]
            cand_r = rids[idx]

            # Merge with current best
            best_d, best_r = _topk_merge(best_d, best_r, cand_d, cand_r, top_k)

        # Build results
        results = []
        for r, d in zip(best_r, best_d):
            if r < 0:
                continue
            results.append(SearchResult(
                rid=int(r),
                distance=float(d),
                score=1.0 / (1.0 + float(d)),
            ))

        return results

    def _search_chunked_binary(
        self,
        query: np.ndarray,
        top_k: int,
        metric: Metric,
        batch_rows: int = 200_000,
    ) -> List[SearchResult]:
        """
        Chunked brute force search for binary vectors using Hamming distance.
        """
        # Ensure query is uint8 packed bits
        query = np.asarray(query, dtype=np.uint8).ravel()

        # Initialize best results
        best_d = np.full(top_k, np.inf, dtype=np.float32)
        best_r = np.full(top_k, -1, dtype=np.int64)

        for batch in self.iter_vectors(batch_rows=batch_rows):
            X = batch.vectors  # uint8 (N, nbytes)
            rids = batch.rids

            # Compute Hamming distance using XOR and popcount
            xor = np.bitwise_xor(X, query)
            # Count bits set in each byte
            d = np.zeros(len(X), dtype=np.float32)
            for i in range(xor.shape[1]):
                # Use lookup table for popcount
                d += _popcount_table[xor[:, i]]

            if metric == "jaccard":
                # Jaccard distance = hamming / (bits_set_a + bits_set_b - hamming)
                # For now, just use Hamming as approximation
                pass

            # Get top-k from this batch
            k = min(top_k, len(d))
            if k == 0:
                continue

            idx = np.argpartition(d, k - 1)[:k]
            cand_d = d[idx]
            cand_r = rids[idx]

            # Merge with current best
            best_d, best_r = _topk_merge(best_d, best_r, cand_d, cand_r, top_k)

        # Build results
        results = []
        for r, d in zip(best_r, best_d):
            if r < 0:
                continue
            results.append(SearchResult(
                rid=int(r),
                distance=float(d),
                score=1.0 / (1.0 + float(d)),
            ))

        return results

    def _compute_distances(
        self,
        query: np.ndarray,
        X: np.ndarray,
        metric: Metric,
    ) -> np.ndarray:
        """Compute distances between query and all vectors."""
        if metric == "cosine":
            # Normalize
            q_norm = query / (np.linalg.norm(query) + 1e-8)
            if self._meta.normalized:
                X_norm = X
            else:
                X_norm = X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)
            sims = X_norm @ q_norm
            return 1.0 - sims

        elif metric == "euclidean":
            return np.linalg.norm(X - query, axis=1)

        elif metric == "dot":
            # Higher = more similar, so negate for distance
            return -X @ query

        else:
            # Default to euclidean
            return np.linalg.norm(X - query, axis=1)

    def close(self) -> None:
        """Release resources."""
        self._faiss_index = None


def open_embedding_store(
    storage_path: Path | str,
) -> ParquetEmbeddingStore:
    """
    Open an embedding store from a directory.

    Args:
        storage_path: Path to embeddings/<space>/ directory

    Returns:
        ParquetEmbeddingStore instance

    Examples:
        >>> store = open_embedding_store("/path/to/embeddings/minilm")
        >>> results = store.search(query_vector, top_k=10)
    """
    return ParquetEmbeddingStore(Path(storage_path))
