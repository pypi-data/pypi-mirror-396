"""
Embeddings store abstraction for warpdata.

Provides a scalable, zero-copy interface for embedding storage and search.

Key features:
- Zero-copy Arrow buffer reads (no to_pylist())
- Chunked iteration for arbitrarily large spaces
- Scalable search: FAISS index -> brute force -> chunked scan
- Support for float32, float16, binary vectors
- HNSW/IVF index policy for optimal performance
- L2 normalization on write for cosine spaces
"""
from .types import (
    VectorKind,
    Metric,
    IndexType,
    EmbeddingSpaceMeta,
    FloatBatch,
    BinaryBatch,
    VectorBatch,
    SearchResult,
)
from .store import EmbeddingStore
from .parquet_store import ParquetEmbeddingStore, open_embedding_store
from .writer import EmbeddingWriter, write_embeddings
from .indexer import build_index, select_index_type, remove_index

__all__ = [
    # Types
    "VectorKind",
    "Metric",
    "IndexType",
    "EmbeddingSpaceMeta",
    "FloatBatch",
    "BinaryBatch",
    "VectorBatch",
    "SearchResult",
    # Store
    "EmbeddingStore",
    "ParquetEmbeddingStore",
    "open_embedding_store",
    # Writer
    "EmbeddingWriter",
    "write_embeddings",
    # Indexer
    "build_index",
    "select_index_type",
    "remove_index",
]
