"""
DuckDB-based registry for dataset metadata.

Stores:
- Dataset definitions
- Version manifests
- Storage paths to .duckdb files
"""
import duckdb
import json
import threading
from pathlib import Path
from typing import Optional, Dict, Any, List

from .config import get_config
from .utils import ensure_dir


class Registry:
    """
    DuckDB-based registry for dataset management.

    This replaces the previous SQLite-based registry with a unified
    DuckDB solution that matches our data storage format.
    """

    def __init__(self, db_path: Optional[Path] = None, read_only: bool = False):
        """
        Initialize registry.

        Args:
            db_path: Path to DuckDB database (uses config if not provided)
            read_only: If True, open in read-only mode (no locking for reads)
        """
        if db_path is None:
            # Change extension from .db to .duckdb
            db_path = get_config().registry_db.with_suffix(".duckdb")

        self.db_path = Path(db_path)
        self.read_only = read_only

        if not read_only:
            ensure_dir(self.db_path.parent)

        # Persistent connection for the registry
        self.conn = duckdb.connect(str(self.db_path), read_only=read_only)

        # Only init tables for write connections
        if not read_only:
            self._init_db()

    def _init_db(self):
        """Initialize registry tables."""
        # Datasets table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS datasets (
                workspace VARCHAR,
                name VARCHAR,
                latest_version VARCHAR,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (workspace, name)
            )
        """)

        # Versions table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS versions (
                workspace VARCHAR,
                name VARCHAR,
                version_hash VARCHAR,
                manifest_json VARCHAR,
                storage_path VARCHAR,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (workspace, name, version_hash)
            )
        """)

        # Embeddings spaces table with extended metadata
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS embeddings_spaces (
                workspace VARCHAR,
                name VARCHAR,
                version_hash VARCHAR,
                space_name VARCHAR,
                provider VARCHAR,
                model VARCHAR,
                dimension INTEGER,
                distance_metric VARCHAR DEFAULT 'cosine',
                storage_path VARCHAR,
                -- Extended metadata (v2)
                row_count BIGINT,
                vector_kind VARCHAR DEFAULT 'float32',
                normalized BOOLEAN DEFAULT FALSE,
                index_type VARCHAR,
                index_params VARCHAR,
                status VARCHAR DEFAULT 'ready',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (workspace, name, version_hash, space_name)
            )
        """)

        # Raw data sources table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS raw_data_sources (
                workspace VARCHAR,
                name VARCHAR,
                version_hash VARCHAR,
                source_type VARCHAR,         -- 'file', 'directory', 'url'
                source_path VARCHAR,         -- local path or original URL
                size BIGINT,                 -- bytes (for dirs: computed total)
                content_hash VARCHAR,        -- optional (if uploaded to CAS)
                metadata_json VARCHAR,       -- JSON string, optional
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (workspace, name, version_hash, source_path)
            )
        """)

        # Migrate existing tables to add new columns if missing
        self._migrate_embeddings_schema()

    def _migrate_embeddings_schema(self):
        """Add new columns to embeddings_spaces if missing (v1 -> v2 migration)."""
        # Get current columns
        try:
            cols = self.conn.execute("""
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'embeddings_spaces'
            """).fetchall()
            existing = {c[0] for c in cols}
        except Exception:
            return  # Table doesn't exist yet

        # New columns to add
        migrations = [
            ("row_count", "BIGINT"),
            ("vector_kind", "VARCHAR DEFAULT 'float32'"),
            ("normalized", "BOOLEAN DEFAULT FALSE"),
            ("index_type", "VARCHAR"),
            ("index_params", "VARCHAR"),
            ("status", "VARCHAR DEFAULT 'ready'"),
            ("updated_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
        ]

        for col_name, col_type in migrations:
            if col_name not in existing:
                try:
                    self.conn.execute(f"""
                        ALTER TABLE embeddings_spaces ADD COLUMN {col_name} {col_type}
                    """)
                except Exception:
                    pass  # Column might already exist

    def register_dataset(
        self,
        workspace: str,
        name: str,
        version_hash: str,
        manifest: Dict[str, Any],
        storage_path: Optional[str] = None,
    ) -> str:
        """
        Register a dataset version.

        Args:
            workspace: Workspace name
            name: Dataset name
            version_hash: Content-based version hash
            manifest: Version manifest (schema, resources, etc.)
            storage_path: Path to the .duckdb file (if ingested)

        Returns:
            Version hash
        """
        manifest_json = json.dumps(manifest)

        # 1. Upsert Dataset
        self.conn.execute("""
            INSERT INTO datasets (workspace, name, latest_version, updated_at)
            VALUES (?, ?, ?, now())
            ON CONFLICT (workspace, name) DO UPDATE SET
                latest_version = excluded.latest_version,
                updated_at = now()
        """, [workspace, name, version_hash])

        # 2. Insert Version
        self.conn.execute("""
            INSERT INTO versions (workspace, name, version_hash, manifest_json, storage_path)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT (workspace, name, version_hash) DO UPDATE SET
                manifest_json = excluded.manifest_json,
                storage_path = excluded.storage_path
        """, [workspace, name, version_hash, manifest_json, storage_path])

        return version_hash

    def get_dataset_version(
        self, workspace: str, name: str, version: str = "latest"
    ) -> Optional[Dict[str, Any]]:
        """
        Get information about a dataset version.

        Args:
            workspace: Workspace name
            name: Dataset name
            version: Version (hash or 'latest')

        Returns:
            Dataset version info, or None if not found
        """
        if version == "latest":
            row = self.conn.execute("""
                SELECT latest_version as version_hash, created_at, updated_at
                FROM datasets
                WHERE workspace = ? AND name = ?
            """, [workspace, name]).fetchone()
        else:
            row = self.conn.execute("""
                SELECT version_hash, created_at
                FROM versions
                WHERE workspace = ? AND name = ? AND version_hash = ?
            """, [workspace, name, version]).fetchone()

        if row is None:
            return None

        cols = [c[0] for c in self.conn.description]
        return dict(zip(cols, row))

    def get_dataset_path(
        self, workspace: str, name: str, version: str = "latest"
    ) -> Optional[str]:
        """
        Get the local path to the dataset's .duckdb file.

        Args:
            workspace: Workspace name
            name: Dataset name
            version: Version (hash or 'latest')

        Returns:
            Path to .duckdb file, or None if not found/ingested
        """
        if version == "latest":
            res = self.conn.execute("""
                SELECT v.storage_path
                FROM datasets d
                JOIN versions v ON d.workspace = v.workspace
                               AND d.name = v.name
                               AND d.latest_version = v.version_hash
                WHERE d.workspace = ? AND d.name = ?
            """, [workspace, name]).fetchone()
        else:
            res = self.conn.execute("""
                SELECT storage_path FROM versions
                WHERE workspace = ? AND name = ? AND version_hash = ?
            """, [workspace, name, version]).fetchone()

        return res[0] if res else None

    def get_manifest(
        self, workspace: str, name: str, version_hash: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get the manifest for a dataset version.

        Args:
            workspace: Workspace name
            name: Dataset name
            version_hash: Version hash

        Returns:
            Manifest dictionary, or None if not found
        """
        row = self.conn.execute("""
            SELECT manifest_json
            FROM versions
            WHERE workspace = ? AND name = ? AND version_hash = ?
        """, [workspace, name, version_hash]).fetchone()

        if row is None:
            return None

        return json.loads(row[0])

    def list_datasets(self, workspace: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all registered datasets.

        Args:
            workspace: Filter by workspace (optional)

        Returns:
            List of dataset info dictionaries
        """
        if workspace:
            rows = self.conn.execute("""
                SELECT workspace, name, latest_version, created_at, updated_at
                FROM datasets
                WHERE workspace = ?
                ORDER BY workspace, name
            """, [workspace]).fetchall()
        else:
            rows = self.conn.execute("""
                SELECT workspace, name, latest_version, created_at, updated_at
                FROM datasets
                ORDER BY workspace, name
            """).fetchall()

        cols = [c[0] for c in self.conn.description]
        return [dict(zip(cols, row)) for row in rows]

    def remove_dataset(self, workspace: str, name: str, version_hash: Optional[str] = None):
        """
        Remove a dataset or specific version from the registry.

        Args:
            workspace: Workspace name
            name: Dataset name
            version_hash: Optional version to remove (removes all if not specified)
        """
        if version_hash:
            # Remove specific version
            self.conn.execute("""
                DELETE FROM versions
                WHERE workspace = ? AND name = ? AND version_hash = ?
            """, [workspace, name, version_hash])

            # Check if there are other versions
            remaining = self.conn.execute("""
                SELECT COUNT(*) as count FROM versions
                WHERE workspace = ? AND name = ?
            """, [workspace, name]).fetchone()

            if remaining[0] == 0:
                # No more versions, remove dataset entry
                self.conn.execute("""
                    DELETE FROM datasets WHERE workspace = ? AND name = ?
                """, [workspace, name])
            else:
                # Update latest_version to most recent remaining version
                latest = self.conn.execute("""
                    SELECT version_hash FROM versions
                    WHERE workspace = ? AND name = ?
                    ORDER BY created_at DESC LIMIT 1
                """, [workspace, name]).fetchone()

                if latest:
                    self.conn.execute("""
                        UPDATE datasets
                        SET latest_version = ?, updated_at = now()
                        WHERE workspace = ? AND name = ?
                    """, [latest[0], workspace, name])
        else:
            # Remove all versions
            self.conn.execute("""
                DELETE FROM versions WHERE workspace = ? AND name = ?
            """, [workspace, name])
            self.conn.execute("""
                DELETE FROM datasets WHERE workspace = ? AND name = ?
            """, [workspace, name])

    def register_embedding_space(
        self,
        workspace: str,
        name: str,
        version_hash: str,
        space_name: str,
        provider: str,
        model: str,
        dimension: int,
        distance_metric: str,
        storage_path: str,
        # Extended metadata (v2)
        row_count: Optional[int] = None,
        vector_kind: str = "float32",
        normalized: bool = False,
        index_type: Optional[str] = None,
        index_params: Optional[Dict[str, Any]] = None,
        status: str = "ready",
    ):
        """
        Register an embedding space for a dataset version.

        Args:
            workspace: Workspace name
            name: Dataset name
            version_hash: Dataset version hash
            space_name: Embedding space name
            provider: Embedding provider (e.g., 'sentence-transformers')
            model: Model name
            dimension: Vector dimension
            distance_metric: Distance metric ('cosine', 'euclidean', 'dot')
            storage_path: Path to embeddings directory
            row_count: Number of vectors (optional)
            vector_kind: Vector type ('float32', 'float16', 'binary')
            normalized: Whether vectors are L2-normalized
            index_type: FAISS index type (optional)
            index_params: Index parameters as dict (optional)
            status: Space status ('ready', 'building', 'missing', 'failed')
        """
        index_params_json = json.dumps(index_params) if index_params else None

        self.conn.execute("""
            INSERT INTO embeddings_spaces
            (workspace, name, version_hash, space_name, provider, model,
             dimension, distance_metric, storage_path,
             row_count, vector_kind, normalized, index_type, index_params, status, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, now())
            ON CONFLICT (workspace, name, version_hash, space_name) DO UPDATE SET
                provider = excluded.provider,
                model = excluded.model,
                dimension = excluded.dimension,
                distance_metric = excluded.distance_metric,
                storage_path = excluded.storage_path,
                row_count = excluded.row_count,
                vector_kind = excluded.vector_kind,
                normalized = excluded.normalized,
                index_type = excluded.index_type,
                index_params = excluded.index_params,
                status = excluded.status,
                updated_at = now()
        """, [workspace, name, version_hash, space_name, provider, model,
              dimension, distance_metric, storage_path,
              row_count, vector_kind, normalized, index_type, index_params_json, status])

    def list_embedding_spaces(
        self, workspace: str, name: str, version_hash: str
    ) -> List[Dict[str, Any]]:
        """List all embedding spaces for a dataset version."""
        rows = self.conn.execute("""
            SELECT space_name, provider, model, dimension, distance_metric,
                   storage_path, row_count, vector_kind, normalized,
                   index_type, index_params, status, created_at, updated_at
            FROM embeddings_spaces
            WHERE workspace = ? AND name = ? AND version_hash = ?
            ORDER BY created_at
        """, [workspace, name, version_hash]).fetchall()

        cols = [c[0] for c in self.conn.description]
        results = []
        for row in rows:
            d = dict(zip(cols, row))
            # Parse index_params JSON
            if d.get("index_params"):
                try:
                    d["index_params"] = json.loads(d["index_params"])
                except (json.JSONDecodeError, TypeError):
                    d["index_params"] = {}
            results.append(d)
        return results

    def get_embedding_space(
        self, workspace: str, name: str, version_hash: str, space_name: str
    ) -> Optional[Dict[str, Any]]:
        """Get a single embedding space row."""
        row = self.conn.execute("""
            SELECT space_name, provider, model, dimension, distance_metric,
                   storage_path, row_count, vector_kind, normalized,
                   index_type, index_params, status, created_at, updated_at
            FROM embeddings_spaces
            WHERE workspace = ? AND name = ? AND version_hash = ? AND space_name = ?
            LIMIT 1
        """, [workspace, name, version_hash, space_name]).fetchone()

        if row is None:
            return None

        cols = [c[0] for c in self.conn.description]
        d = dict(zip(cols, row))
        # Parse index_params JSON
        if d.get("index_params"):
            try:
                d["index_params"] = json.loads(d["index_params"])
            except (json.JSONDecodeError, TypeError):
                d["index_params"] = {}
        return d

    def remove_embedding_space(
        self, workspace: str, name: str, version_hash: str, space_name: str
    ) -> None:
        """Delete an embedding space registration."""
        self.conn.execute("""
            DELETE FROM embeddings_spaces
            WHERE workspace = ? AND name = ? AND version_hash = ? AND space_name = ?
        """, [workspace, name, version_hash, space_name])

    def list_embedding_spaces_for_dataset(
        self, workspace: str, name: str
    ) -> List[Dict[str, Any]]:
        """List embedding spaces across all versions for a dataset."""
        rows = self.conn.execute("""
            SELECT version_hash, space_name, provider, model, dimension,
                   distance_metric, storage_path, row_count, vector_kind, normalized,
                   index_type, index_params, status, created_at, updated_at
            FROM embeddings_spaces
            WHERE workspace = ? AND name = ?
            ORDER BY created_at
        """, [workspace, name]).fetchall()

        cols = [c[0] for c in self.conn.description]
        results = []
        for row in rows:
            d = dict(zip(cols, row))
            # Parse index_params JSON
            if d.get("index_params"):
                try:
                    d["index_params"] = json.loads(d["index_params"])
                except (json.JSONDecodeError, TypeError):
                    d["index_params"] = {}
            results.append(d)
        return results

    def update_embedding_space_status(
        self,
        workspace: str,
        name: str,
        version_hash: str,
        space_name: str,
        status: str,
        row_count: Optional[int] = None,
        index_type: Optional[str] = None,
        index_params: Optional[Dict[str, Any]] = None,
    ):
        """Update embedding space status and metadata."""
        updates = ["status = ?", "updated_at = now()"]
        params = [status]

        if row_count is not None:
            updates.append("row_count = ?")
            params.append(row_count)

        if index_type is not None:
            updates.append("index_type = ?")
            params.append(index_type)

        if index_params is not None:
            updates.append("index_params = ?")
            params.append(json.dumps(index_params))

        params.extend([workspace, name, version_hash, space_name])

        self.conn.execute(f"""
            UPDATE embeddings_spaces
            SET {', '.join(updates)}
            WHERE workspace = ? AND name = ? AND version_hash = ? AND space_name = ?
        """, params)

    # -------------------------------------------------------------------------
    # Raw Data Sources
    # -------------------------------------------------------------------------

    def register_raw_data_source(
        self,
        workspace: str,
        name: str,
        version_hash: str,
        source_type: str,
        source_path: str,
        size: Optional[int] = None,
        content_hash: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Register a raw data source for a dataset version.

        Args:
            workspace: Workspace name
            name: Dataset name
            version_hash: Dataset version hash
            source_type: Type of source ('file', 'directory', 'url')
            source_path: Local path or URL
            size: Size in bytes (optional)
            content_hash: Content hash if uploaded to CAS (optional)
            metadata: Additional metadata dict (optional)
        """
        self.conn.execute("""
            INSERT INTO raw_data_sources
                (workspace, name, version_hash, source_type, source_path, size, content_hash, metadata_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (workspace, name, version_hash, source_path) DO UPDATE SET
                source_type = excluded.source_type,
                size = excluded.size,
                content_hash = excluded.content_hash,
                metadata_json = excluded.metadata_json
        """, [
            workspace, name, version_hash,
            source_type, source_path,
            size,
            content_hash,
            json.dumps(metadata or {}) if metadata is not None else None,
        ])

    def list_raw_data_sources(
        self, workspace: str, name: str, version_hash: str
    ) -> List[Dict[str, Any]]:
        """
        List raw data sources for a dataset version.

        Args:
            workspace: Workspace name
            name: Dataset name
            version_hash: Dataset version hash

        Returns:
            List of raw data source dictionaries
        """
        rows = self.conn.execute("""
            SELECT source_type, source_path, size, content_hash, metadata_json, created_at
            FROM raw_data_sources
            WHERE workspace = ? AND name = ? AND version_hash = ?
            ORDER BY created_at
        """, [workspace, name, version_hash]).fetchall()

        cols = [c[0] for c in self.conn.description]
        out = []
        for row in rows:
            d = dict(zip(cols, row))
            d["metadata"] = json.loads(d["metadata_json"]) if d.get("metadata_json") else {}
            out.append(d)
        return out

    def remove_raw_data_sources(
        self, workspace: str, name: str, version_hash: str
    ) -> None:
        """
        Remove all raw data sources for a dataset version.

        Args:
            workspace: Workspace name
            name: Dataset name
            version_hash: Dataset version hash
        """
        self.conn.execute("""
            DELETE FROM raw_data_sources
            WHERE workspace = ? AND name = ? AND version_hash = ?
        """, [workspace, name, version_hash])

    def update_raw_data_source(
        self,
        workspace: str,
        name: str,
        version_hash: str,
        source_path: str,
        content_hash: Optional[str] = None,
        size: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Update a raw data source entry (e.g., after uploading to CAS).

        Args:
            workspace: Workspace name
            name: Dataset name
            version_hash: Dataset version hash
            source_path: Source path to update
            content_hash: New content hash (optional)
            size: Updated size (optional)
            metadata: Updated metadata (optional)
        """
        updates = []
        params = []

        if content_hash is not None:
            updates.append("content_hash = ?")
            params.append(content_hash)

        if size is not None:
            updates.append("size = ?")
            params.append(size)

        if metadata is not None:
            updates.append("metadata_json = ?")
            params.append(json.dumps(metadata))

        if not updates:
            return

        params.extend([workspace, name, version_hash, source_path])
        self.conn.execute(f"""
            UPDATE raw_data_sources
            SET {', '.join(updates)}
            WHERE workspace = ? AND name = ? AND version_hash = ? AND source_path = ?
        """, params)

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()


# Global registry instances with thread-safe initialization
_global_registry: Optional[Registry] = None
_global_registry_ro: Optional[Registry] = None
_registry_lock = threading.Lock()


def get_registry() -> Registry:
    """
    Get the global registry instance (read-write).

    Thread-safe: uses double-checked locking pattern.
    Use this only for write operations (register_dataset, remove_dataset).

    Returns:
        Registry instance with write access
    """
    global _global_registry

    if _global_registry is None:
        with _registry_lock:
            # Double-check after acquiring lock
            if _global_registry is None:
                _global_registry = Registry(read_only=False)

    return _global_registry


def get_registry_readonly() -> Registry:
    """
    Get a read-only registry instance.

    Thread-safe and doesn't block other processes.
    Use this for read operations (list_datasets, get_dataset_path, load, etc.).

    Returns:
        Registry instance with read-only access
    """
    global _global_registry_ro

    if _global_registry_ro is None:
        with _registry_lock:
            if _global_registry_ro is None:
                _global_registry_ro = Registry(read_only=True)

    return _global_registry_ro


def reset_registry():
    """Reset the global registry (useful for testing)."""
    global _global_registry, _global_registry_ro
    with _registry_lock:
        if _global_registry is not None:
            _global_registry.close()
        _global_registry = None
        if _global_registry_ro is not None:
            _global_registry_ro.close()
        _global_registry_ro = None
