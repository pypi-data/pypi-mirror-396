"""
Test registry read-only access for sandboxed/restricted environments.
"""
import os
import pytest
import sqlite3
import tempfile
from pathlib import Path
from warpdata.core.registry import Registry
import warpdata as wd


def test_readonly_registry_list_embeddings():
    """Test that list_embeddings works on read-only database."""
    # Create a temporary registry with some data
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "registry.db"

        # Create and populate registry
        reg = Registry(db_path)
        reg.register_dataset(
            workspace="test",
            name="papers",
            version_hash="abc123",
            manifest={
                "schema": {"id": "INTEGER", "text": "VARCHAR"},
                "resources": [],
                "format": "parquet"
            }
        )
        reg.register_embedding_space(
            workspace="test",
            name="papers",
            version_hash="abc123",
            space_name="test-embeddings",
            provider="sentence-transformers",
            model="test-model",
            dimension=384,
            distance_metric="cosine",
            storage_path="/tmp/embeddings"
        )

        # Make database read-only
        os.chmod(db_path, 0o444)

        # Create new registry instance pointing to read-only DB
        readonly_reg = Registry(db_path)

        # This should work without writes
        spaces = readonly_reg.list_embedding_spaces("test", "papers", "abc123")
        assert len(spaces) == 1
        assert spaces[0]["space_name"] == "test-embeddings"
        assert spaces[0]["model"] == "test-model"
        assert spaces[0]["dimension"] == 384


def test_readonly_registry_get_dataset_version():
    """Test that get_dataset_version works on read-only database."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "registry.db"

        # Create and populate registry
        reg = Registry(db_path)
        reg.register_dataset(
            workspace="test",
            name="dataset",
            version_hash="xyz789",
            manifest={
                "schema": {"col": "VARCHAR"},
                "resources": [],
                "format": "parquet"
            }
        )

        # Make database read-only
        os.chmod(db_path, 0o444)

        # Create new registry instance pointing to read-only DB
        readonly_reg = Registry(db_path)

        # This should work without writes
        version = readonly_reg.get_dataset_version("test", "dataset", "latest")
        assert version is not None
        assert version["version_hash"] == "xyz789"


def test_readonly_registry_get_manifest():
    """Test that get_manifest works on read-only database."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "registry.db"

        # Create and populate registry
        reg = Registry(db_path)
        manifest = {
            "schema": {"id": "INTEGER"},
            "resources": [{"uri": "file:///test.parquet"}],
            "format": "parquet"
        }
        reg.register_dataset(
            workspace="test",
            name="data",
            version_hash="def456",
            manifest=manifest
        )

        # Make database read-only
        os.chmod(db_path, 0o444)

        # Create new registry instance pointing to read-only DB
        readonly_reg = Registry(db_path)

        # This should work without writes
        retrieved = readonly_reg.get_manifest("test", "data", "def456")
        assert retrieved is not None
        assert retrieved["schema"]["id"] == "INTEGER"
        assert len(retrieved["resources"]) == 1


def test_readonly_api_list_embeddings():
    """Test that wd.list_embeddings() works with read-only registry."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "registry.db"

        # Create and populate registry
        reg = Registry(db_path)
        reg.register_dataset(
            workspace="arxiv",
            name="papers",
            version_hash="test123",
            manifest={
                "schema": {"title": "VARCHAR", "abstract": "VARCHAR"},
                "resources": [],
                "format": "parquet"
            }
        )
        reg.register_embedding_space(
            workspace="arxiv",
            name="papers",
            version_hash="test123",
            space_name="abstract-embeddinggemma-300m",
            provider="sentence-transformers",
            model="google/embeddinggemma-300m",
            dimension=768,
            distance_metric="cosine",
            storage_path="/tmp/embeddings/abstract"
        )
        reg.register_embedding_space(
            workspace="arxiv",
            name="papers",
            version_hash="test123",
            space_name="title-embeddinggemma-300m",
            provider="sentence-transformers",
            model="google/embeddinggemma-300m",
            dimension=768,
            distance_metric="cosine",
            storage_path="/tmp/embeddings/title"
        )

        # Make database read-only
        os.chmod(db_path, 0o444)

        # Force registry reset and point to read-only DB
        from warpdata.core import registry as reg_module
        reg_module._global_registry = Registry(db_path)

        # This should work without writes (simulates sandbox environment)
        spaces = wd.list_embeddings("warpdata://arxiv/papers")
        assert len(spaces) == 2

        space_names = [s["space_name"] for s in spaces]
        assert "abstract-embeddinggemma-300m" in space_names
        assert "title-embeddinggemma-300m" in space_names

        # Verify full metadata is returned
        for space in spaces:
            assert "space_name" in space
            assert "provider" in space
            assert "model" in space
            assert "dimension" in space
            assert space["model"] == "google/embeddinggemma-300m"
            assert space["dimension"] == 768
