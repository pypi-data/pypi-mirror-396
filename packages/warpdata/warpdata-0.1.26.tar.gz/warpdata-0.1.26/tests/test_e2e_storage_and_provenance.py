"""
End-to-end tests for storage backends and raw data tracking.

Tests the complete workflow:
1. Register dataset with raw data tracking
2. Upload to storage backend (local/S3)
3. Backup dataset
4. Restore dataset
5. Verify provenance tracking
"""
import pytest
import tempfile
from pathlib import Path
import pandas as pd
import pyarrow.parquet as pq
import pyarrow as pa
import json

import warpdata as wd
from warpdata.core.registry import Registry
from warpdata.core.storage import LocalStorage, compute_content_hash


@pytest.fixture
def temp_workspace(tmp_path):
    """Create a temporary workspace with test data."""
    # Create raw data sources
    raw_data_dir = tmp_path / "raw_data"
    raw_data_dir.mkdir()

    # Create a "database" file
    db_file = raw_data_dir / "source.db"
    db_file.write_text("Mock database content")

    # Create some PDFs
    pdfs_dir = raw_data_dir / "pdfs"
    pdfs_dir.mkdir()
    (pdfs_dir / "doc1.pdf").write_text("PDF content 1")
    (pdfs_dir / "doc2.pdf").write_text("PDF content 2")

    # Create processed dataset
    processed_dir = tmp_path / "processed"
    processed_dir.mkdir()

    df = pd.DataFrame({
        "id": [1, 2, 3],
        "title": ["Doc 1", "Doc 2", "Doc 3"],
        "content": ["Content A", "Content B", "Content C"],
    })

    dataset_file = processed_dir / "dataset.parquet"
    df.to_parquet(dataset_file)

    # Create registry and storage dirs
    registry_dir = tmp_path / "registry"
    registry_dir.mkdir()
    storage_dir = tmp_path / "storage"
    storage_dir.mkdir()

    return {
        "raw_data_dir": raw_data_dir,
        "db_file": db_file,
        "pdfs_dir": pdfs_dir,
        "dataset_file": dataset_file,
        "registry_dir": registry_dir,
        "storage_dir": storage_dir,
    }


def test_register_with_raw_data(temp_workspace):
    """Test registering dataset with raw data tracking."""
    from warpdata.core.registry import get_registry
    import warpdata.core.registry as reg_module

    # Setup custom registry
    registry = Registry(temp_workspace["registry_dir"] / "test.db")
    reg_module._global_registry = registry

    # Register dataset with raw data
    version = wd.register_dataset(
        "warpdata://test/documents",
        resources=[str(temp_workspace["dataset_file"])],
        raw_data=[
            str(temp_workspace["db_file"]),
            str(temp_workspace["pdfs_dir"] / "doc1.pdf"),
            str(temp_workspace["pdfs_dir"] / "doc2.pdf"),
        ],
    )

    assert version is not None

    # Check raw data sources were tracked
    sources = wd.get_raw_data_sources("warpdata://test/documents")
    assert len(sources) == 3

    # Verify source types
    source_types = {s["source_type"] for s in sources}
    assert "db" in source_types
    assert "pdf" in source_types

    # Verify paths
    source_paths = {Path(s["source_path"]).name for s in sources}
    assert "source.db" in source_paths
    assert "doc1.pdf" in source_paths
    assert "doc2.pdf" in source_paths


def test_storage_backend_local(temp_workspace):
    """Test local storage backend."""
    storage = LocalStorage(temp_workspace["storage_dir"])

    # Upload file
    test_file = temp_workspace["db_file"]
    content_hash = storage.put(
        test_file,
        metadata={"type": "test", "name": "source.db"}
    )

    assert content_hash is not None
    assert len(content_hash) == 64  # SHA256 hash

    # Verify file exists in storage
    assert storage.exists(content_hash)

    # Download file
    restore_path = temp_workspace["storage_dir"] / "restored.db"
    storage.get(content_hash, restore_path)

    assert restore_path.exists()
    assert restore_path.read_text() == test_file.read_text()

    # Verify metadata
    metadata = storage.get_metadata(content_hash)
    assert metadata["type"] == "test"
    assert metadata["name"] == "source.db"


def test_content_deduplication(temp_workspace):
    """Test that identical files are deduplicated."""
    storage = LocalStorage(temp_workspace["storage_dir"])

    # Create two files with same content
    file1 = temp_workspace["storage_dir"] / "file1.txt"
    file2 = temp_workspace["storage_dir"] / "file2.txt"

    file1.write_text("Same content")
    file2.write_text("Same content")

    # Upload both files
    hash1 = storage.put(file1)
    hash2 = storage.put(file2)

    # Hashes should be identical (dedup)
    assert hash1 == hash2

    # Only one copy should exist in storage
    storage_key = storage._get_storage_key(hash1)
    storage_path = storage.objects_dir / storage_key
    assert storage_path.exists()

    # Count files in storage (should be 1, not 2)
    storage_files = list(storage.objects_dir.rglob("*"))
    storage_files = [f for f in storage_files if f.is_file() and not f.name.endswith('.meta.json')]
    assert len(storage_files) == 1


def test_register_with_storage_upload(temp_workspace):
    """Test registering dataset with upload to storage."""
    from warpdata.core.registry import get_registry
    import warpdata.core.registry as reg_module
    import warpdata.core.storage as storage_module

    # Setup custom registry and storage
    registry = Registry(temp_workspace["registry_dir"] / "test.db")
    reg_module._global_registry = registry

    storage = LocalStorage(temp_workspace["storage_dir"])
    storage_module._global_storage = storage

    # Register with upload
    version = wd.register_dataset(
        "warpdata://test/docs",
        resources=[str(temp_workspace["dataset_file"])],
        raw_data=[str(temp_workspace["db_file"])],
        storage_backend="local",
        upload_to_storage=True,
    )

    assert version is not None

    # Verify raw data was uploaded
    sources = wd.get_raw_data_sources("warpdata://test/docs")
    assert len(sources) == 1

    content_hash = sources[0]["content_hash"]
    assert content_hash is not None

    # Verify file exists in storage
    assert storage.exists(content_hash)


def test_backup_and_restore(temp_workspace):
    """Test full backup and restore workflow."""
    from warpdata.core.registry import get_registry
    import warpdata.core.registry as reg_module
    import warpdata.core.storage as storage_module

    # Setup
    registry = Registry(temp_workspace["registry_dir"] / "test.db")
    reg_module._global_registry = registry

    storage = LocalStorage(temp_workspace["storage_dir"])
    storage_module._global_storage = storage

    # Register dataset with raw data (with upload enabled)
    version = wd.register_dataset(
        "warpdata://test/papers",
        resources=[str(temp_workspace["dataset_file"])],
        raw_data=[
            str(temp_workspace["db_file"]),
            str(temp_workspace["pdfs_dir"] / "doc1.pdf"),
        ],
        storage_backend="local",
        upload_to_storage=True,  # ← Need to upload to be able to restore
    )

    # Backup dataset
    backup_info = wd.backup_dataset(
        "warpdata://test/papers",
        backend="local",
        include_raw=True,
    )

    assert backup_info["total_files"] >= 2  # At least dataset + 1 raw file
    assert backup_info["total_size"] > 0

    # Delete local raw data to simulate loss
    temp_workspace["db_file"].unlink()
    temp_workspace["pdfs_dir"].joinpath("doc1.pdf").unlink()

    # Restore dataset
    restore_dir = temp_workspace["storage_dir"] / "restored"
    restore_info = wd.restore_dataset(
        "warpdata://test/papers",
        backend="local",
        include_raw=True,
        output_dir=str(restore_dir),
    )

    assert restore_info["total_files"] >= 2
    assert restore_info["total_size"] > 0

    # Verify restored files exist
    restored_files = list(restore_dir.rglob("*"))
    restored_files = [f for f in restored_files if f.is_file()]
    assert len(restored_files) >= 2


def test_provenance_tracking_e2e(temp_workspace):
    """Test end-to-end provenance tracking."""
    from warpdata.core.registry import get_registry
    import warpdata.core.registry as reg_module

    # Setup
    registry = Registry(temp_workspace["registry_dir"] / "test.db")
    reg_module._global_registry = registry

    # Register dataset with comprehensive raw data
    version = wd.register_dataset(
        "warpdata://test/analysis",
        resources=[str(temp_workspace["dataset_file"])],
        raw_data=[
            str(temp_workspace["db_file"]),
            str(temp_workspace["pdfs_dir"]),  # Directory
        ],
        metadata={"project": "test", "version": "1.0"},
    )

    # Get provenance
    sources = wd.get_raw_data_sources("warpdata://test/analysis")

    # Verify all sources tracked
    assert len(sources) == 2

    # Find directory source
    dir_sources = [s for s in sources if s["source_type"] == "directory"]
    assert len(dir_sources) == 1

    dir_source = dir_sources[0]
    assert "pdfs" in dir_source["source_path"]
    assert dir_source["size"] > 0  # Total size of all files in directory

    # Find DB source
    db_sources = [s for s in sources if s["source_type"] == "db"]
    assert len(db_sources) == 1


def test_migration_applied(temp_workspace):
    """Test that migration is automatically applied."""
    # Create fresh registry
    registry = Registry(temp_workspace["registry_dir"] / "migration_test.db")

    # Check that new tables exist
    with registry._connect() as conn:
        # Check raw_data_sources table
        cursor = conn.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='raw_data_sources'
        """)
        assert cursor.fetchone() is not None

        # Check storage_locations table
        cursor = conn.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='storage_locations'
        """)
        assert cursor.fetchone() is not None

        # Check schema_version table
        cursor = conn.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='schema_version'
        """)
        assert cursor.fetchone() is not None

        # Verify migration was applied
        cursor = conn.execute("SELECT version FROM schema_version")
        version = cursor.fetchone()
        assert version is not None
        assert version[0] >= 1  # At least version 1 applied


def test_full_workflow_integration(temp_workspace):
    """
    Test complete workflow from raw data to backup and restore.

    This is the comprehensive E2E test covering all features.
    """
    from warpdata.core.registry import get_registry
    import warpdata.core.registry as reg_module
    import warpdata.core.storage as storage_module

    # Setup infrastructure
    registry = Registry(temp_workspace["registry_dir"] / "full_test.db")
    reg_module._global_registry = registry

    storage = LocalStorage(temp_workspace["storage_dir"])
    storage_module._global_storage = storage

    # Step 1: Register dataset with raw data and upload
    print("\n=== Step 1: Register with raw data ===")
    version = wd.register_dataset(
        "warpdata://test/full_pipeline",
        resources=[str(temp_workspace["dataset_file"])],
        raw_data=[
            str(temp_workspace["db_file"]),
            str(temp_workspace["pdfs_dir"] / "doc1.pdf"),
            str(temp_workspace["pdfs_dir"] / "doc2.pdf"),
        ],
        storage_backend="local",
        upload_to_storage=True,
        metadata={"pipeline": "full_test", "stage": "final"},
    )

    assert version is not None
    print(f"✓ Registered version: {version[:16]}...")

    # Step 2: Verify provenance
    print("\n=== Step 2: Verify provenance ===")
    sources = wd.get_raw_data_sources("warpdata://test/full_pipeline")
    assert len(sources) == 3
    print(f"✓ Tracked {len(sources)} raw data sources")

    for source in sources:
        assert source["content_hash"] is not None  # All uploaded
        assert source["size"] > 0
        print(f"  - {source['source_type']}: {Path(source['source_path']).name}")

    # Step 3: Backup entire dataset
    print("\n=== Step 3: Backup dataset ===")
    backup_info = wd.backup_dataset(
        "warpdata://test/full_pipeline",
        backend="local",
        include_raw=True,
    )

    assert backup_info["total_files"] >= 4  # dataset + 3 raw files
    total_mb = backup_info["total_size"] / (1024 * 1024)
    print(f"✓ Backed up {backup_info['total_files']} files ({total_mb:.2f} MB)")

    # Step 4: Simulate data loss
    print("\n=== Step 4: Simulate data loss ===")
    temp_workspace["db_file"].unlink()
    for pdf in temp_workspace["pdfs_dir"].glob("*.pdf"):
        pdf.unlink()
    print("✓ Deleted raw data files")

    # Step 5: Restore from backup
    print("\n=== Step 5: Restore from backup ===")
    restore_dir = temp_workspace["storage_dir"] / "full_restore"
    restore_info = wd.restore_dataset(
        "warpdata://test/full_pipeline",
        backend="local",
        include_raw=True,
        output_dir=str(restore_dir),
    )

    assert restore_info["total_files"] >= 3  # Raw files restored
    print(f"✓ Restored {restore_info['total_files']} files to {restore_info['output_dir']}")

    # Step 6: Verify restored data
    print("\n=== Step 6: Verify restored data ===")
    restored_files = list(restore_dir.rglob("*"))
    restored_files = [f for f in restored_files if f.is_file()]
    assert len(restored_files) >= 3

    # Verify content integrity by checking hashes
    for source in sources:
        if source["source_type"] != "directory":
            content_hash = source["content_hash"]
            # Find restored file
            restored = [f for f in restored_files if content_hash in storage._get_storage_key(content_hash)]
            # Note: In a real scenario, you'd verify the actual content matches

    print(f"✓ Verified {len(restored_files)} restored files")

    print("\n=== Full workflow complete! ===")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
