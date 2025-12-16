"""
SQLite-based registry for dataset metadata.

Uses WAL mode for concurrent read/write access without locking issues.
This replaces the DuckDB registry which had single-writer lock problems.
"""
import sqlite3
import json
import threading
from pathlib import Path
from typing import Optional, Dict, Any, List
from contextlib import contextmanager

from .config import get_config
from .utils import ensure_dir


class Registry:
    """
    SQLite-based registry for dataset management.

    Uses WAL mode for better concurrency - multiple readers and one writer
    can operate simultaneously without blocking.
    """

    def __init__(self, db_path: Optional[Path] = None, read_only: bool = False):
        """
        Initialize registry.

        Args:
            db_path: Path to SQLite database (uses config if not provided)
            read_only: If True, open in read-only mode (ignored for SQLite WAL)
        """
        if db_path is None:
            db_path = get_config().registry_db.with_suffix(".sqlite")

        self.db_path = Path(db_path)
        self.read_only = read_only
        self._local = threading.local()

        if not read_only:
            ensure_dir(self.db_path.parent)
            # Initialize tables with a temporary connection
            with self._get_connection() as conn:
                self._init_db(conn)

    def _get_connection(self) -> sqlite3.Connection:
        """Get a thread-local database connection."""
        if not hasattr(self._local, 'conn') or self._local.conn is None:
            uri = f"file:{self.db_path}"
            if self.read_only:
                uri += "?mode=ro"

            self._local.conn = sqlite3.connect(
                uri if self.read_only else str(self.db_path),
                uri=self.read_only,
                check_same_thread=False,
                timeout=30.0
            )
            self._local.conn.row_factory = sqlite3.Row

            # Enable WAL mode for better concurrency
            if not self.read_only:
                self._local.conn.execute("PRAGMA journal_mode=WAL")
                self._local.conn.execute("PRAGMA synchronous=NORMAL")

        return self._local.conn

    @contextmanager
    def _transaction(self):
        """Context manager for transactions."""
        conn = self._get_connection()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise

    @property
    def conn(self):
        """Property for backward compatibility."""
        return self._get_connection()

    def _init_db(self, conn: sqlite3.Connection):
        """Initialize registry tables."""
        # Datasets table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS datasets (
                workspace TEXT,
                name TEXT,
                latest_version TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (workspace, name)
            )
        """)

        # Versions table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS versions (
                workspace TEXT,
                name TEXT,
                version_hash TEXT,
                manifest_json TEXT,
                storage_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (workspace, name, version_hash)
            )
        """)

        # Embeddings spaces table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS embeddings_spaces (
                workspace TEXT,
                name TEXT,
                version_hash TEXT,
                space_name TEXT,
                provider TEXT,
                model TEXT,
                dimension INTEGER,
                distance_metric TEXT DEFAULT 'cosine',
                storage_path TEXT,
                row_count INTEGER,
                vector_kind TEXT DEFAULT 'float32',
                normalized INTEGER DEFAULT 0,
                index_type TEXT,
                index_params TEXT,
                status TEXT DEFAULT 'ready',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (workspace, name, version_hash, space_name)
            )
        """)

        # Raw data sources table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS raw_data_sources (
                workspace TEXT,
                name TEXT,
                version_hash TEXT,
                source_type TEXT,
                source_path TEXT,
                size INTEGER,
                content_hash TEXT,
                metadata_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (workspace, name, version_hash, source_path)
            )
        """)

        conn.commit()

    def register_dataset(
        self,
        workspace: str,
        name: str,
        version_hash: str,
        manifest: Dict[str, Any],
        storage_path: Optional[str] = None,
    ) -> str:
        """Register a dataset version."""
        manifest_json = json.dumps(manifest)

        with self._transaction() as conn:
            # Upsert Dataset
            conn.execute("""
                INSERT INTO datasets (workspace, name, latest_version, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT (workspace, name) DO UPDATE SET
                    latest_version = excluded.latest_version,
                    updated_at = CURRENT_TIMESTAMP
            """, [workspace, name, version_hash])

            # Insert Version
            conn.execute("""
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
        """Get information about a dataset version."""
        conn = self._get_connection()

        if version == "latest":
            row = conn.execute("""
                SELECT latest_version as version_hash, created_at, updated_at
                FROM datasets
                WHERE workspace = ? AND name = ?
            """, [workspace, name]).fetchone()
        else:
            row = conn.execute("""
                SELECT version_hash, created_at
                FROM versions
                WHERE workspace = ? AND name = ? AND version_hash = ?
            """, [workspace, name, version]).fetchone()

        if row is None:
            return None

        return dict(row)

    def get_dataset_path(
        self, workspace: str, name: str, version: str = "latest"
    ) -> Optional[str]:
        """Get the local path to the dataset's storage."""
        conn = self._get_connection()

        if version == "latest":
            res = conn.execute("""
                SELECT v.storage_path
                FROM datasets d
                JOIN versions v ON d.workspace = v.workspace
                               AND d.name = v.name
                               AND d.latest_version = v.version_hash
                WHERE d.workspace = ? AND d.name = ?
            """, [workspace, name]).fetchone()
        else:
            res = conn.execute("""
                SELECT storage_path FROM versions
                WHERE workspace = ? AND name = ? AND version_hash = ?
            """, [workspace, name, version]).fetchone()

        return res[0] if res else None

    def get_manifest(
        self, workspace: str, name: str, version_hash: str
    ) -> Optional[Dict[str, Any]]:
        """Get the manifest for a dataset version."""
        conn = self._get_connection()

        row = conn.execute("""
            SELECT manifest_json
            FROM versions
            WHERE workspace = ? AND name = ? AND version_hash = ?
        """, [workspace, name, version_hash]).fetchone()

        if row is None:
            return None

        return json.loads(row[0])

    def list_datasets(self, workspace: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all registered datasets."""
        conn = self._get_connection()

        if workspace:
            rows = conn.execute("""
                SELECT workspace, name, latest_version, created_at, updated_at
                FROM datasets
                WHERE workspace = ?
                ORDER BY workspace, name
            """, [workspace]).fetchall()
        else:
            rows = conn.execute("""
                SELECT workspace, name, latest_version, created_at, updated_at
                FROM datasets
                ORDER BY workspace, name
            """).fetchall()

        return [dict(row) for row in rows]

    def remove_dataset(self, workspace: str, name: str, version_hash: Optional[str] = None):
        """Remove a dataset or specific version from the registry."""
        with self._transaction() as conn:
            if version_hash:
                # Remove specific version
                conn.execute("""
                    DELETE FROM versions
                    WHERE workspace = ? AND name = ? AND version_hash = ?
                """, [workspace, name, version_hash])

                # Remove associated raw data sources
                conn.execute("""
                    DELETE FROM raw_data_sources
                    WHERE workspace = ? AND name = ? AND version_hash = ?
                """, [workspace, name, version_hash])

                # Check if there are other versions
                remaining = conn.execute("""
                    SELECT COUNT(*) as count FROM versions
                    WHERE workspace = ? AND name = ?
                """, [workspace, name]).fetchone()

                if remaining[0] == 0:
                    conn.execute("""
                        DELETE FROM datasets WHERE workspace = ? AND name = ?
                    """, [workspace, name])
                else:
                    # Update latest_version
                    latest = conn.execute("""
                        SELECT version_hash FROM versions
                        WHERE workspace = ? AND name = ?
                        ORDER BY created_at DESC LIMIT 1
                    """, [workspace, name]).fetchone()

                    if latest:
                        conn.execute("""
                            UPDATE datasets SET latest_version = ?, updated_at = CURRENT_TIMESTAMP
                            WHERE workspace = ? AND name = ?
                        """, [latest[0], workspace, name])
            else:
                # Remove all versions
                conn.execute("""
                    DELETE FROM versions WHERE workspace = ? AND name = ?
                """, [workspace, name])
                conn.execute("""
                    DELETE FROM datasets WHERE workspace = ? AND name = ?
                """, [workspace, name])
                conn.execute("""
                    DELETE FROM raw_data_sources WHERE workspace = ? AND name = ?
                """, [workspace, name])
                conn.execute("""
                    DELETE FROM embeddings_spaces WHERE workspace = ? AND name = ?
                """, [workspace, name])

    def dataset_exists(self, workspace: str, name: str) -> bool:
        """Check if a dataset exists."""
        conn = self._get_connection()
        row = conn.execute("""
            SELECT 1 FROM datasets WHERE workspace = ? AND name = ?
        """, [workspace, name]).fetchone()
        return row is not None

    # Embeddings methods
    def register_embeddings_space(
        self,
        workspace: str,
        name: str,
        version_hash: str,
        space_name: str,
        provider: str,
        model: str,
        dimension: int,
        storage_path: str,
        distance_metric: str = "cosine",
        row_count: Optional[int] = None,
        vector_kind: str = "float32",
        normalized: bool = False,
        index_type: Optional[str] = None,
        index_params: Optional[Dict] = None,
    ) -> None:
        """Register an embeddings space."""
        with self._transaction() as conn:
            conn.execute("""
                INSERT INTO embeddings_spaces
                (workspace, name, version_hash, space_name, provider, model, dimension,
                 storage_path, distance_metric, row_count, vector_kind, normalized,
                 index_type, index_params, status, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'ready', CURRENT_TIMESTAMP)
                ON CONFLICT (workspace, name, version_hash, space_name) DO UPDATE SET
                    provider = excluded.provider,
                    model = excluded.model,
                    dimension = excluded.dimension,
                    storage_path = excluded.storage_path,
                    distance_metric = excluded.distance_metric,
                    row_count = excluded.row_count,
                    vector_kind = excluded.vector_kind,
                    normalized = excluded.normalized,
                    index_type = excluded.index_type,
                    index_params = excluded.index_params,
                    status = 'ready',
                    updated_at = CURRENT_TIMESTAMP
            """, [workspace, name, version_hash, space_name, provider, model, dimension,
                  storage_path, distance_metric, row_count, vector_kind, int(normalized),
                  index_type, json.dumps(index_params) if index_params else None])

    def get_embeddings_space(
        self, workspace: str, name: str, version_hash: str, space_name: str
    ) -> Optional[Dict[str, Any]]:
        """Get embeddings space info."""
        conn = self._get_connection()
        row = conn.execute("""
            SELECT * FROM embeddings_spaces
            WHERE workspace = ? AND name = ? AND version_hash = ? AND space_name = ?
        """, [workspace, name, version_hash, space_name]).fetchone()

        if row is None:
            return None

        result = dict(row)
        if result.get('index_params'):
            result['index_params'] = json.loads(result['index_params'])
        result['normalized'] = bool(result.get('normalized', 0))
        return result

    def list_embeddings_spaces(
        self, workspace: str, name: str, version_hash: str
    ) -> List[Dict[str, Any]]:
        """List all embeddings spaces for a dataset version."""
        conn = self._get_connection()
        rows = conn.execute("""
            SELECT * FROM embeddings_spaces
            WHERE workspace = ? AND name = ? AND version_hash = ?
        """, [workspace, name, version_hash]).fetchall()

        results = []
        for row in rows:
            r = dict(row)
            if r.get('index_params'):
                r['index_params'] = json.loads(r['index_params'])
            r['normalized'] = bool(r.get('normalized', 0))
            results.append(r)
        return results

    def remove_embeddings_space(
        self, workspace: str, name: str, version_hash: str, space_name: str
    ) -> None:
        """Remove an embeddings space."""
        with self._transaction() as conn:
            conn.execute("""
                DELETE FROM embeddings_spaces
                WHERE workspace = ? AND name = ? AND version_hash = ? AND space_name = ?
            """, [workspace, name, version_hash, space_name])

    # Raw data sources methods
    def add_raw_data_source(
        self,
        workspace: str,
        name: str,
        version_hash: str,
        source_type: str,
        source_path: str,
        size: Optional[int] = None,
        content_hash: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> None:
        """Add a raw data source for a dataset version."""
        with self._transaction() as conn:
            conn.execute("""
                INSERT INTO raw_data_sources
                (workspace, name, version_hash, source_type, source_path, size, content_hash, metadata_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT (workspace, name, version_hash, source_path) DO UPDATE SET
                    source_type = excluded.source_type,
                    size = excluded.size,
                    content_hash = excluded.content_hash,
                    metadata_json = excluded.metadata_json
            """, [workspace, name, version_hash, source_type, source_path, size,
                  content_hash, json.dumps(metadata) if metadata else None])

    def list_raw_data_sources(
        self, workspace: str, name: str, version_hash: str
    ) -> List[Dict[str, Any]]:
        """List raw data sources for a dataset version."""
        conn = self._get_connection()
        rows = conn.execute("""
            SELECT source_type, source_path, size, content_hash, metadata_json
            FROM raw_data_sources
            WHERE workspace = ? AND name = ? AND version_hash = ?
        """, [workspace, name, version_hash]).fetchall()

        results = []
        for row in rows:
            r = dict(row)
            if r.get('metadata_json'):
                r['metadata'] = json.loads(r['metadata_json'])
                del r['metadata_json']
            else:
                r['metadata'] = None
                if 'metadata_json' in r:
                    del r['metadata_json']
            results.append(r)
        return results

    def update_raw_data_source(
        self,
        workspace: str,
        name: str,
        version_hash: str,
        source_path: str,
        content_hash: Optional[str] = None,
        size: Optional[int] = None,
    ) -> None:
        """Update a raw data source."""
        updates = []
        params = []

        if content_hash is not None:
            updates.append("content_hash = ?")
            params.append(content_hash)
        if size is not None:
            updates.append("size = ?")
            params.append(size)

        if not updates:
            return

        params.extend([workspace, name, version_hash, source_path])

        with self._transaction() as conn:
            conn.execute(f"""
                UPDATE raw_data_sources
                SET {', '.join(updates)}
                WHERE workspace = ? AND name = ? AND version_hash = ? AND source_path = ?
            """, params)

    def close(self):
        """Close the database connection."""
        if hasattr(self._local, 'conn') and self._local.conn:
            self._local.conn.close()
            self._local.conn = None


# Global registry instances with thread-safe initialization
_global_registry: Optional[Registry] = None
_global_registry_ro: Optional[Registry] = None
_registry_lock = threading.Lock()


def get_registry() -> Registry:
    """Get the global registry instance (read-write)."""
    global _global_registry

    if _global_registry is None:
        with _registry_lock:
            if _global_registry is None:
                _global_registry = Registry(read_only=False)

    return _global_registry


def get_registry_readonly() -> Registry:
    """Get a read-only registry instance."""
    global _global_registry_ro

    if _global_registry_ro is None:
        with _registry_lock:
            if _global_registry_ro is None:
                # Ensure the database exists before opening in read-only mode
                # by creating it with a write connection first if needed
                from .config import get_config
                db_path = get_config().registry_db.with_suffix(".sqlite")
                if not db_path.exists():
                    # Create empty database with tables
                    _init_reg = Registry(read_only=False)
                    _init_reg.close()
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
