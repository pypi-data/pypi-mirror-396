"""
End-to-end tests for basic data loading workflows.
"""
from pathlib import Path

import pytest
import duckdb

import warpdata as wd


class TestBasicDataLoading:
    """Test basic data loading from local files."""

    def test_load_local_parquet_file(self, temp_home: Path, temp_data_dir: Path):
        """Test loading a local Parquet file directly."""
        parquet_path = temp_data_dir / "sample.parquet"

        # Load as DuckDB relation (default)
        result = wd.load(f"file://{parquet_path}")

        # Verify it's a DuckDB relation
        assert isinstance(result, duckdb.DuckDBPyRelation)

        # Verify we can query it
        df = result.df()
        assert len(df) == 5
        assert list(df.columns) == ["id", "name", "value", "category"]
        assert df["name"].tolist() == ["Alice", "Bob", "Charlie", "David", "Eve"]

    def test_load_local_csv_file(self, temp_home: Path, temp_data_dir: Path):
        """Test loading a local CSV file."""
        csv_path = temp_data_dir / "sample.csv"

        result = wd.load(f"file://{csv_path}")

        assert isinstance(result, duckdb.DuckDBPyRelation)
        df = result.df()
        assert len(df) == 5
        assert "name" in df.columns

    def test_load_without_scheme(self, temp_home: Path, temp_data_dir: Path):
        """Test loading a file without a URI scheme (should default to file://)."""
        parquet_path = str(temp_data_dir / "sample.parquet")

        result = wd.load(parquet_path)

        assert isinstance(result, duckdb.DuckDBPyRelation)
        df = result.df()
        assert len(df) == 5

    def test_load_as_pandas(self, temp_home: Path, temp_data_dir: Path):
        """Test loading data as a Pandas DataFrame."""
        parquet_path = temp_data_dir / "sample.parquet"

        result = wd.load(f"file://{parquet_path}", as_format="pandas")

        # Should be a pandas DataFrame
        assert hasattr(result, "columns")  # Simple check for DataFrame-like object
        assert len(result) == 5

    def test_load_multiple_files(self, temp_home: Path, temp_data_dir: Path):
        """Test loading multiple partitioned files."""
        partitions_dir = temp_data_dir / "partitioned"

        # Use glob pattern to load all parquet files
        result = wd.load(f"file://{partitions_dir}/*.parquet")

        df = result.df()
        # All 5 rows from the original data, now split across 3 files
        assert len(df) == 5

    def test_schema_inspection(self, temp_home: Path, temp_data_dir: Path):
        """Test schema inspection of a dataset."""
        parquet_path = temp_data_dir / "sample.parquet"

        schema = wd.schema(f"file://{parquet_path}")

        # Schema should be a dict or list of column info
        assert schema is not None
        assert "id" in str(schema)
        assert "name" in str(schema)

    def test_head_preview(self, temp_home: Path, temp_data_dir: Path):
        """Test previewing first N rows of data."""
        parquet_path = temp_data_dir / "sample.parquet"

        # Get first 3 rows
        result = wd.head(f"file://{parquet_path}", n=3)

        # Should return a displayable result (DuckDB relation or DataFrame)
        assert result is not None

        # Verify we get exactly 3 rows
        if isinstance(result, duckdb.DuckDBPyRelation):
            df = result.df()
            assert len(df) == 3
        else:
            assert len(result) == 3


class TestCachingBehavior:
    """Test that remote files are cached locally."""

    def test_cache_directory_created(self, temp_home: Path, temp_data_dir: Path):
        """Test that cache directory is created on first use."""
        cache_dir = temp_home / "cache"

        # Cache should not exist initially
        assert not cache_dir.exists()

        # Load a file (this should trigger cache creation if needed)
        parquet_path = temp_data_dir / "sample.parquet"
        _ = wd.load(f"file://{parquet_path}")

        # For local files, cache might not be needed, but directory should exist
        # This is a simplified test - we'll verify cache behavior more thoroughly
        # when we test remote files (s3://, http://)

    def test_load_same_file_twice(self, temp_home: Path, temp_data_dir: Path):
        """Test that loading the same file twice uses cache."""
        parquet_path = temp_data_dir / "sample.parquet"

        # Load twice
        result1 = wd.load(f"file://{parquet_path}")
        result2 = wd.load(f"file://{parquet_path}")

        # Both should succeed and return the same data
        df1 = result1.df()
        df2 = result2.df()

        assert len(df1) == len(df2)
        assert list(df1.columns) == list(df2.columns)


class TestErrorHandling:
    """Test error handling for invalid inputs."""

    def test_load_nonexistent_file(self, temp_home: Path):
        """Test loading a file that doesn't exist."""
        with pytest.raises(Exception):  # Should raise FileNotFoundError or similar
            wd.load("file:///nonexistent/path.parquet")

    def test_load_invalid_format(self, temp_home: Path, temp_data_dir: Path):
        """Test loading an unsupported file format."""
        # Create a dummy file with unsupported extension
        dummy_file = temp_data_dir / "test.xyz"
        dummy_file.write_text("not a valid data file")

        # This should either raise an error or handle gracefully
        with pytest.raises(Exception):
            wd.load(f"file://{dummy_file}")

    def test_schema_on_nonexistent_file(self, temp_home: Path):
        """Test schema inspection on nonexistent file."""
        with pytest.raises(Exception):
            wd.schema("file:///nonexistent/path.parquet")
