"""
End-to-end tests for embeddings and vector search.
"""
from pathlib import Path

import pytest
import numpy as np

import warpdata as wd


class TestEmbeddingsBasic:
    """Test basic embeddings functionality."""

    def test_add_embeddings_numpy_provider(self, temp_home: Path, sample_text_data: Path):
        """Test adding embeddings using numpy provider (for testing)."""
        # Register dataset
        wd.register_dataset("warpdata://test/texts", resources=[f"file://{sample_text_data}"])

        # Materialize to get rid column
        materialized = wd.materialize("warpdata://test/texts")

        # Add embeddings with numpy provider (simple random vectors for testing)
        wd.add_embeddings(
            "warpdata://test/texts",
            space="test-embeddings",
            provider="numpy",  # Simple test provider
            source={"columns": ["text"]},
            dimension=128,
        )

        # Should not raise an error
        assert True

    def test_list_embeddings(self, temp_home: Path, sample_text_data: Path):
        """Test listing available embedding spaces."""
        # Register and add embeddings
        wd.register_dataset("warpdata://test/texts2", resources=[f"file://{sample_text_data}"])
        wd.materialize("warpdata://test/texts2")

        wd.add_embeddings(
            "warpdata://test/texts2",
            space="space1",
            provider="numpy",
            source={"columns": ["text"]},
            dimension=64,
        )

        wd.add_embeddings(
            "warpdata://test/texts2",
            space="space2",
            provider="numpy",
            source={"columns": ["text"]},
            dimension=128,
        )

        # List embeddings
        spaces = wd.list_embeddings("warpdata://test/texts2")

        assert len(spaces) == 2
        assert any(s["space_name"] == "space1" for s in spaces)
        assert any(s["space_name"] == "space2" for s in spaces)

    def test_search_embeddings(self, temp_home: Path, sample_text_data: Path):
        """Test searching embeddings."""
        # Setup
        wd.register_dataset("warpdata://test/search", resources=[f"file://{sample_text_data}"])
        wd.materialize("warpdata://test/search")

        wd.add_embeddings(
            "warpdata://test/search",
            space="test-space",
            provider="numpy",
            source={"columns": ["text"]},
            dimension=128,
        )

        # Search with a query vector
        query_vector = np.random.rand(128).tolist()
        results = wd.search_embeddings(
            "warpdata://test/search", space="test-space", query=query_vector, top_k=3
        )

        # Should return top 3 results
        assert len(results) <= 3
        assert all("rid" in r for r in results)
        assert all("score" in r or "distance" in r for r in results)

    def test_join_results(self, temp_home: Path, sample_text_data: Path):
        """Test joining search results back to original data."""
        # Setup
        wd.register_dataset("warpdata://test/join", resources=[f"file://{sample_text_data}"])
        wd.materialize("warpdata://test/join")

        wd.add_embeddings(
            "warpdata://test/join",
            space="test-space",
            provider="numpy",
            source={"columns": ["text"]},
            dimension=64,
        )

        # Search
        query_vector = np.random.rand(64).tolist()
        results = wd.search_embeddings(
            "warpdata://test/join", space="test-space", query=query_vector, top_k=2
        )

        # Extract rids
        rids = [r["rid"] for r in results]

        # Join back to original data
        joined = wd.join_results(
            "warpdata://test/join", rids=rids, columns=["text", "label"], as_format="pandas"
        )

        # Should get a dataframe with the requested columns
        assert len(joined) == len(rids)
        assert "text" in joined.columns
        assert "label" in joined.columns


@pytest.mark.skipif(
    not pytest.importorskip("sentence_transformers", reason="sentence-transformers not installed"),
    reason="sentence-transformers not installed",
)
class TestEmbeddingsSentenceTransformers:
    """Test embeddings with sentence-transformers provider."""

    def test_add_embeddings_sentence_transformers(self, temp_home: Path, sample_text_data: Path):
        """Test adding embeddings using sentence-transformers."""
        # Register dataset
        wd.register_dataset("warpdata://test/st-texts", resources=[f"file://{sample_text_data}"])
        wd.materialize("warpdata://test/st-texts")

        # Add embeddings with sentence-transformers
        wd.add_embeddings(
            "warpdata://test/st-texts",
            space="st-embeddings",
            provider="sentence-transformers",
            model="all-MiniLM-L6-v2",  # Small, fast model for testing
            source={"columns": ["text"]},
        )

        # Verify embeddings were created
        spaces = wd.list_embeddings("warpdata://test/st-texts")
        assert len(spaces) == 1
        assert spaces[0]["space_name"] == "st-embeddings"
        assert spaces[0]["provider"] == "sentence-transformers"

    def test_search_with_text_query(self, temp_home: Path, sample_text_data: Path):
        """Test searching with a text query (automatically embeds the query)."""
        # Setup
        wd.register_dataset("warpdata://test/st-search", resources=[f"file://{sample_text_data}"])
        wd.materialize("warpdata://test/st-search")

        wd.add_embeddings(
            "warpdata://test/st-search",
            space="st-space",
            provider="sentence-transformers",
            model="all-MiniLM-L6-v2",
            source={"columns": ["text"]},
        )

        # Search with a text query
        results = wd.search_embeddings(
            "warpdata://test/st-search",
            space="st-space",
            query="machine learning and AI",  # Text query
            top_k=2,
        )

        assert len(results) <= 2
        assert all("rid" in r for r in results)


class TestEmbeddingsErrorHandling:
    """Test error handling in embeddings."""

    def test_add_embeddings_without_rid(self, temp_home: Path, sample_text_data: Path):
        """Test that adding embeddings auto-materializes if not already materialized."""
        # Register but don't manually materialize
        wd.register_dataset("warpdata://test/no-rid", resources=[f"file://{sample_text_data}"])

        # Add embeddings should auto-materialize
        wd.add_embeddings(
            "warpdata://test/no-rid",
            space="auto-mat",
            provider="numpy",
            source={"columns": ["text"]},
            dimension=64,
        )

        # Should succeed - embeddings were added
        spaces = wd.list_embeddings("warpdata://test/no-rid")
        assert len(spaces) == 1
        assert spaces[0]["space_name"] == "auto-mat"

    def test_search_nonexistent_space(self, temp_home: Path, sample_text_data: Path):
        """Test searching in a non-existent embedding space."""
        wd.register_dataset("warpdata://test/no-space", resources=[f"file://{sample_text_data}"])
        wd.materialize("warpdata://test/no-space")

        # Try to search without adding embeddings
        with pytest.raises(Exception):
            wd.search_embeddings(
                "warpdata://test/no-space",
                space="nonexistent",
                query=np.random.rand(64).tolist(),
                top_k=5,
            )

    def test_join_invalid_rids(self, temp_home: Path, sample_text_data: Path):
        """Test joining with invalid rids."""
        wd.register_dataset("warpdata://test/bad-rids", resources=[f"file://{sample_text_data}"])
        wd.materialize("warpdata://test/bad-rids")

        # Try to join with rids that don't exist
        joined = wd.join_results(
            "warpdata://test/bad-rids",
            rids=[9999, 10000],  # Non-existent rids
            columns=["text"],
            as_format="pandas",
        )

        # Should return empty dataframe
        assert len(joined) == 0
