"""
Embedding writer with normalization and space.json generation.

Handles:
- L2 normalization for cosine spaces on write
- Efficient Parquet writing with FixedSizeList
- space.json metadata generation
"""
from __future__ import annotations
import json
import logging
from pathlib import Path
from typing import Iterator, Optional, Tuple
import numpy as np

import pyarrow as pa
import pyarrow.parquet as pq

from .types import EmbeddingSpaceMeta, Metric, VectorKind

logger = logging.getLogger(__name__)


class EmbeddingWriter:
    """
    Efficient writer for embedding vectors.

    Handles:
    - L2 normalization for cosine spaces
    - Batched Parquet writing with FixedSizeList
    - space.json metadata generation
    """

    def __init__(
        self,
        output_dir: Path,
        dimension: int,
        metric: Metric = "cosine",
        vector_kind: VectorKind = "float32",
        normalize_cosine: bool = True,
        compression: str = "snappy",
    ):
        """
        Initialize embedding writer.

        Args:
            output_dir: Directory to write embeddings/<space>/
            dimension: Vector dimension
            metric: Distance metric
            vector_kind: Vector representation type
            normalize_cosine: L2-normalize vectors for cosine metric
            compression: Parquet compression codec
        """
        self._output_dir = Path(output_dir)
        self._output_dir.mkdir(parents=True, exist_ok=True)

        self._dimension = dimension
        self._metric = metric
        self._vector_kind = vector_kind
        self._normalize = normalize_cosine and metric == "cosine"
        self._compression = compression

        self._vectors_path = self._output_dir / "vectors.parquet"
        self._writer: Optional[pq.ParquetWriter] = None
        self._row_count = 0

        # Build schema
        self._schema = self._build_schema()

    def _build_schema(self) -> pa.Schema:
        """Build Arrow schema for vectors file."""
        if self._vector_kind == "float32":
            vec_type = pa.list_(pa.float32(), self._dimension)
        elif self._vector_kind == "float16":
            vec_type = pa.list_(pa.float16(), self._dimension)
        elif self._vector_kind == "binary":
            # Binary vectors stored as fixed-size binary
            nbytes = (self._dimension + 7) // 8
            vec_type = pa.binary(nbytes)
        else:
            vec_type = pa.list_(pa.float32(), self._dimension)

        return pa.schema([
            ("rid", pa.int64()),
            ("vector", vec_type),
        ])

    def write_batch(
        self,
        rids: np.ndarray,
        vectors: np.ndarray,
    ) -> int:
        """
        Write a batch of embeddings.

        Args:
            rids: Row IDs (int64)
            vectors: Embeddings (float32, shape [N, dim])

        Returns:
            Number of rows written
        """
        if len(rids) == 0:
            return 0

        # Ensure correct types
        rids = np.asarray(rids, dtype=np.int64)
        vectors = np.asarray(vectors, dtype=np.float32)

        # Normalize for cosine
        if self._normalize:
            norms = np.linalg.norm(vectors, axis=1, keepdims=True)
            vectors = vectors / (norms + 1e-8)

        # Build Arrow table
        flat_values = vectors.ravel()
        vectors_array = pa.FixedSizeListArray.from_arrays(
            pa.array(flat_values, type=pa.float32()),
            list_size=self._dimension,
        )

        table = pa.table({
            "rid": pa.array(rids, type=pa.int64()),
            "vector": vectors_array,
        })

        # Write
        if self._writer is None:
            self._writer = pq.ParquetWriter(
                self._vectors_path,
                self._schema,
                compression=self._compression,
            )

        self._writer.write_table(table)
        self._row_count += len(rids)

        return len(rids)

    def close(self) -> int:
        """
        Close the writer.

        Returns:
            Total rows written
        """
        if self._writer is not None:
            self._writer.close()
            self._writer = None

        return self._row_count

    def write_space_json(
        self,
        dataset_id: str,
        version_hash: str,
        space: str,
        provider: str,
        model: str,
        index_type: Optional[str] = None,
        index_params: Optional[dict] = None,
    ) -> Path:
        """
        Write space.json metadata file.

        Args:
            dataset_id: Dataset ID
            version_hash: Dataset version hash
            space: Space name
            provider: Embedding provider
            model: Model name
            index_type: Optional index type
            index_params: Optional index parameters

        Returns:
            Path to space.json
        """
        meta = EmbeddingSpaceMeta(
            dataset_id=dataset_id,
            version_hash=version_hash,
            space=space,
            provider=provider,
            model=model,
            vector_kind=self._vector_kind,
            dimension=self._dimension,
            metric=self._metric,
            normalized=self._normalize,
            row_count=self._row_count,
            index_type=index_type,
            index_params=index_params or {},
            status="ready",
        )

        space_json_path = self._output_dir / "space.json"
        with open(space_json_path, "w") as f:
            json.dump(meta.to_dict(), f, indent=2)

        return space_json_path

    def __enter__(self) -> "EmbeddingWriter":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()


def write_embeddings(
    output_dir: Path,
    rid_vec_iter: Iterator[Tuple[np.ndarray, np.ndarray]],
    dimension: int,
    metric: Metric = "cosine",
    normalize_cosine: bool = True,
    compression: str = "snappy",
) -> Tuple[Path, int]:
    """
    Write embeddings from an iterator.

    Args:
        output_dir: Output directory
        rid_vec_iter: Iterator yielding (rids, vectors) batches
        dimension: Vector dimension
        metric: Distance metric
        normalize_cosine: L2-normalize for cosine
        compression: Parquet compression

    Returns:
        Tuple of (vectors_path, row_count)
    """
    writer = EmbeddingWriter(
        output_dir=output_dir,
        dimension=dimension,
        metric=metric,
        normalize_cosine=normalize_cosine,
        compression=compression,
    )

    try:
        for rids, vectors in rid_vec_iter:
            writer.write_batch(rids, vectors)
    finally:
        row_count = writer.close()

    return output_dir / "vectors.parquet", row_count
