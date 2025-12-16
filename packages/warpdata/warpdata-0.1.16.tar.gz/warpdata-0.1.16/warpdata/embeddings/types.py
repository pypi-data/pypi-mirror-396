"""
Type definitions for the embedding store.

Defines the canonical schema for embedding spaces and vector batches.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Literal, Union
import numpy as np


# Vector representation types
VectorKind = Literal["float32", "float16", "int8", "binary"]

# Distance/similarity metrics
Metric = Literal["cosine", "euclidean", "dot", "hamming", "jaccard"]

# Index types
IndexType = Literal["flat", "hnsw", "ivf_flat", "ivf_pq", "binary_flat", "binary_ivf"]


@dataclass
class EmbeddingSpaceMeta:
    """
    Metadata for an embedding space.

    This is the canonical contract for embedding space configuration.
    Stored in space.json for portability and in the registry for querying.
    """
    # Dataset identity
    dataset_id: str
    version_hash: str
    space: str

    # Provider info
    provider: str
    model: str

    # Vector properties
    vector_kind: VectorKind = "float32"
    dimension: int = 0  # For binary: number of bits
    metric: Metric = "cosine"
    normalized: bool = False  # True if vectors are L2-normalized on disk

    # Size info
    row_count: int = 0

    # Index info (optional)
    index_type: IndexType | None = None
    index_params: dict = field(default_factory=dict)

    # Status
    status: Literal["ready", "building", "missing", "failed"] = "ready"

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict."""
        return {
            "dataset_id": self.dataset_id,
            "version_hash": self.version_hash,
            "space": self.space,
            "provider": self.provider,
            "model": self.model,
            "vector_kind": self.vector_kind,
            "dimension": self.dimension,
            "metric": self.metric,
            "normalized": self.normalized,
            "row_count": self.row_count,
            "index_type": self.index_type,
            "index_params": self.index_params,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "EmbeddingSpaceMeta":
        """Create from dict (e.g., loaded from space.json)."""
        return cls(
            dataset_id=d.get("dataset_id", ""),
            version_hash=d.get("version_hash", ""),
            space=d.get("space", "default"),
            provider=d.get("provider", "unknown"),
            model=d.get("model", "unknown"),
            vector_kind=d.get("vector_kind", "float32"),
            dimension=d.get("dimension", 0),
            metric=d.get("metric", "cosine"),
            normalized=d.get("normalized", False),
            row_count=d.get("row_count", 0),
            index_type=d.get("index_type"),
            index_params=d.get("index_params", {}),
            status=d.get("status", "ready"),
        )


@dataclass
class FloatBatch:
    """
    A batch of float vectors (float32, float16, or int8 quantized).

    Used for iterating over embeddings without loading all into RAM.
    """
    rids: np.ndarray  # int64 row IDs
    vectors: np.ndarray  # float32/float16 shape (N, dim)

    def __len__(self) -> int:
        return len(self.rids)


@dataclass
class BinaryBatch:
    """
    A batch of binary (bit-packed) vectors.

    For Hamming/Jaccard distance with bitpacked embeddings.
    """
    rids: np.ndarray  # int64 row IDs
    vectors: np.ndarray  # uint8 shape (N, nbytes), packed bits
    nbits: int  # Total number of bits per vector

    def __len__(self) -> int:
        return len(self.rids)


# Union type for vector batches
VectorBatch = Union[FloatBatch, BinaryBatch]


@dataclass
class SearchResult:
    """A single search result."""
    rid: int
    distance: float
    score: float  # Normalized score (higher = more similar)

    def to_dict(self) -> dict:
        return {
            "rid": self.rid,
            "distance": self.distance,
            "score": self.score,
        }
