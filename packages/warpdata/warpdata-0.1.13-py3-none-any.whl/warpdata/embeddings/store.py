"""
Abstract embedding store interface.

Defines the contract for embedding storage backends.
Implementations can use Parquet, Lance, DuckDB VSS, etc.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Iterable, List, Optional
import numpy as np

from .types import EmbeddingSpaceMeta, VectorBatch, SearchResult


class EmbeddingStore(ABC):
    """
    Abstract interface for embedding storage and search.

    This isolates the embedding system from specific storage backends,
    making it easy to swap implementations (Parquet, Lance, DuckDB VSS, etc.).
    """

    @abstractmethod
    def meta(self) -> EmbeddingSpaceMeta:
        """
        Get metadata for this embedding space.

        Returns:
            EmbeddingSpaceMeta with dimension, metric, row_count, etc.
        """
        ...

    @abstractmethod
    def get_vectors(self, rids: List[int]) -> np.ndarray:
        """
        Get vectors for specific row IDs.

        Args:
            rids: List of row IDs to retrieve

        Returns:
            np.ndarray of shape (len(rids), dimension) in rid order

        Note:
            For binary vectors, returns uint8 packed bits.
        """
        ...

    @abstractmethod
    def iter_vectors(
        self,
        batch_rows: int = 200_000,
        columns: Optional[List[str]] = None,
    ) -> Iterable[VectorBatch]:
        """
        Iterate over vectors in batches without loading all into RAM.

        This is the key method for scalable operations on large spaces.
        Uses zero-copy Arrow buffer reads where possible.

        Args:
            batch_rows: Number of rows per batch
            columns: Optional column filter (default: ["rid", "vector"])

        Yields:
            VectorBatch (FloatBatch or BinaryBatch) with rids and vectors
        """
        ...

    @abstractmethod
    def search(
        self,
        query: np.ndarray,
        top_k: int = 10,
        metric: Optional[str] = None,
    ) -> List[SearchResult]:
        """
        Search for similar vectors.

        Uses the best available method:
        1. FAISS index if present
        2. Brute force in RAM if data fits
        3. Chunked brute force scan for large spaces

        Args:
            query: Query vector (1D array)
            top_k: Number of results to return
            metric: Override metric (default: use space's metric)

        Returns:
            List of SearchResult ordered by distance (ascending)
        """
        ...

    @abstractmethod
    def all_vectors(self) -> np.ndarray:
        """
        Load all vectors into RAM (use with caution for large spaces).

        Returns:
            np.ndarray of shape (row_count, dimension)

        Raises:
            MemoryError: If vectors don't fit in RAM
        """
        ...

    @abstractmethod
    def all_rids(self) -> np.ndarray:
        """
        Get all row IDs.

        Returns:
            np.ndarray of int64 row IDs
        """
        ...

    def close(self) -> None:
        """Close any open resources."""
        pass

    def __enter__(self) -> "EmbeddingStore":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()
