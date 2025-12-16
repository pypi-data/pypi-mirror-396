"""
End-to-end tests for dataset registration and management.
"""
from pathlib import Path

import pytest
import duckdb

import warpdata as wd


class TestDatasetRegistration:
    """Test registering datasets in the local registry."""

    def test_register_single_file_dataset(self, temp_home: Path, temp_data_dir: Path):
        """Test registering a dataset from a single file."""
        parquet_path = temp_data_dir / "sample.parquet"

        # Register the dataset
        version = wd.register_dataset(
            "warpdata://test/my-dataset", resources=[f"file://{parquet_path}"]
        )

        # Version should be a hash
        assert version is not None
        assert isinstance(version, str)
        assert len(version) > 0

    def test_register_multiple_files_dataset(self, temp_home: Path, temp_data_dir: Path):
        """Test registering a dataset from multiple partitioned files."""
        partitions_dir = temp_data_dir / "partitioned"

        # Get all parquet files
        parquet_files = list(partitions_dir.glob("*.parquet"))
        resources = [f"file://{p}" for p in parquet_files]

        version = wd.register_dataset(
            "warpdata://test/partitioned-data", resources=resources
        )

        assert version is not None

    def test_load_registered_dataset(self, temp_home: Path, temp_data_dir: Path):
        """Test loading a registered dataset."""
        parquet_path = temp_data_dir / "sample.parquet"

        # Register
        version = wd.register_dataset(
            "warpdata://test/load-test", resources=[f"file://{parquet_path}"]
        )

        # Load by dataset ID (latest version)
        result = wd.load("warpdata://test/load-test")

        assert isinstance(result, duckdb.DuckDBPyRelation)
        df = result.df()
        assert len(df) == 5

    def test_load_specific_version(self, temp_home: Path, temp_data_dir: Path):
        """Test loading a specific version of a dataset."""
        parquet_path = temp_data_dir / "sample.parquet"

        # Register
        version = wd.register_dataset(
            "warpdata://test/versioned", resources=[f"file://{parquet_path}"]
        )

        # Load with explicit version
        result = wd.load(f"warpdata://test/versioned@{version}")

        df = result.df()
        assert len(df) == 5

    def test_load_with_latest_tag(self, temp_home: Path, temp_data_dir: Path):
        """Test loading with explicit @latest tag."""
        parquet_path = temp_data_dir / "sample.parquet"

        # Register
        wd.register_dataset("warpdata://test/latest-test", resources=[f"file://{parquet_path}"])

        # Load with @latest
        result = wd.load("warpdata://test/latest-test@latest")

        df = result.df()
        assert len(df) == 5


class TestDatasetManagement:
    """Test dataset management operations."""

    def test_list_datasets(self, temp_home: Path, temp_data_dir: Path):
        """Test listing all registered datasets."""
        parquet_path = temp_data_dir / "sample.parquet"

        # Register a few datasets
        wd.register_dataset("warpdata://nlp/dataset1", resources=[f"file://{parquet_path}"])
        wd.register_dataset("warpdata://nlp/dataset2", resources=[f"file://{parquet_path}"])
        wd.register_dataset("warpdata://vision/dataset3", resources=[f"file://{parquet_path}"])

        # List all datasets
        datasets = wd.list_datasets()

        assert len(datasets) >= 3
        assert any(d["name"] == "dataset1" for d in datasets)
        assert any(d["name"] == "dataset2" for d in datasets)
        assert any(d["workspace"] == "vision" for d in datasets)

    def test_list_datasets_by_workspace(self, temp_home: Path, temp_data_dir: Path):
        """Test listing datasets filtered by workspace."""
        parquet_path = temp_data_dir / "sample.parquet"

        # Register datasets in different workspaces
        wd.register_dataset("warpdata://nlp/ds1", resources=[f"file://{parquet_path}"])
        wd.register_dataset("warpdata://nlp/ds2", resources=[f"file://{parquet_path}"])
        wd.register_dataset("warpdata://vision/ds3", resources=[f"file://{parquet_path}"])

        # List only NLP datasets
        nlp_datasets = wd.list_datasets(workspace="nlp")

        assert len(nlp_datasets) >= 2
        assert all(d["workspace"] == "nlp" for d in nlp_datasets)

    def test_dataset_info(self, temp_home: Path, temp_data_dir: Path):
        """Test getting detailed info about a dataset."""
        parquet_path = temp_data_dir / "sample.parquet"

        version = wd.register_dataset(
            "warpdata://test/info-test", resources=[f"file://{parquet_path}"]
        )

        # Get dataset info
        info = wd.dataset_info("warpdata://test/info-test")

        assert info is not None
        assert "workspace" in info
        assert "name" in info
        assert "version_hash" in info
        assert "manifest" in info

        # Check manifest content
        manifest = info["manifest"]
        assert "resources" in manifest
        assert len(manifest["resources"]) == 1


class TestDatasetMaterialization:
    """Test materializing datasets with row IDs."""

    def test_materialize_dataset(self, temp_home: Path, temp_data_dir: Path):
        """Test materializing a dataset to create a local copy with rid."""
        parquet_path = temp_data_dir / "sample.parquet"

        # Register dataset
        wd.register_dataset("warpdata://test/materialize", resources=[f"file://{parquet_path}"])

        # Materialize it
        materialized_path = wd.materialize("warpdata://test/materialize")

        # Check that file was created
        assert materialized_path.exists()
        assert materialized_path.suffix == ".parquet"

        # Load the materialized file and check for rid column
        result = wd.load(str(materialized_path))
        df = result.df()

        # Should have rid column
        assert "rid" in df.columns

        # RID should be monotonically increasing from 0
        assert list(df["rid"]) == list(range(len(df)))

    def test_materialize_preserves_data(self, temp_home: Path, temp_data_dir: Path):
        """Test that materialization preserves original data."""
        parquet_path = temp_data_dir / "sample.parquet"

        # Get original data
        original = wd.load(f"file://{parquet_path}").df()

        # Register and materialize
        wd.register_dataset("warpdata://test/preserve", resources=[f"file://{parquet_path}"])
        materialized_path = wd.materialize("warpdata://test/preserve")

        # Load materialized data
        materialized = wd.load(str(materialized_path)).df()

        # Remove rid column for comparison
        materialized_without_rid = materialized.drop("rid", axis=1)

        # Data should be the same (except for rid)
        assert len(original) == len(materialized_without_rid)
        assert list(original.columns) == list(materialized_without_rid.columns)


class TestVersionImmutability:
    """Test that dataset versions are immutable."""

    def test_same_resources_same_version(self, temp_home: Path, temp_data_dir: Path):
        """Test that registering the same resources produces the same version."""
        parquet_path = temp_data_dir / "sample.parquet"

        # Register twice
        version1 = wd.register_dataset(
            "warpdata://test/immutable1", resources=[f"file://{parquet_path}"]
        )
        version2 = wd.register_dataset(
            "warpdata://test/immutable1", resources=[f"file://{parquet_path}"]
        )

        # Should get the same version hash
        assert version1 == version2

    def test_different_resources_different_version(self, temp_home: Path, temp_data_dir: Path):
        """Test that different resources produce different versions."""
        parquet_path = temp_data_dir / "sample.parquet"
        csv_path = temp_data_dir / "sample.csv"

        # Register with different resources
        version1 = wd.register_dataset(
            "warpdata://test/diff1", resources=[f"file://{parquet_path}"]
        )
        version2 = wd.register_dataset(
            "warpdata://test/diff1", resources=[f"file://{csv_path}"]
        )

        # Should get different version hashes
        assert version1 != version2


class TestErrorHandling:
    """Test error handling in registration."""

    def test_register_nonexistent_file(self, temp_home: Path):
        """Test registering a dataset with nonexistent files."""
        with pytest.raises(Exception):
            wd.register_dataset(
                "warpdata://test/bad", resources=["file:///nonexistent/file.parquet"]
            )

    def test_load_unregistered_dataset(self, temp_home: Path):
        """Test loading a dataset that doesn't exist."""
        with pytest.raises(Exception):
            wd.load("warpdata://test/doesnotexist")

    def test_info_on_nonexistent_dataset(self, temp_home: Path):
        """Test getting info on nonexistent dataset."""
        with pytest.raises(Exception):
            wd.dataset_info("warpdata://test/missing")
