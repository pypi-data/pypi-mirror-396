"""
Migrate registry from DuckDB to SQLite.

Run this once to migrate existing data.
"""
import json
from pathlib import Path


def migrate_duckdb_to_sqlite(duckdb_path: Path, sqlite_path: Path) -> dict:
    """
    Migrate registry data from DuckDB to SQLite.

    Args:
        duckdb_path: Path to existing DuckDB registry
        sqlite_path: Path for new SQLite registry

    Returns:
        dict with migration stats
    """
    import duckdb
    from .registry_sqlite import Registry as SQLiteRegistry

    stats = {
        'datasets': 0,
        'versions': 0,
        'embeddings_spaces': 0,
        'raw_data_sources': 0,
    }

    if not duckdb_path.exists():
        print(f"No DuckDB registry found at {duckdb_path}")
        return stats

    # Connect to DuckDB (read-only)
    duck_conn = duckdb.connect(str(duckdb_path), read_only=True)

    # Create new SQLite registry
    sqlite_reg = SQLiteRegistry(db_path=sqlite_path, read_only=False)

    try:
        # Migrate datasets
        try:
            rows = duck_conn.execute("SELECT * FROM datasets").fetchall()
            cols = [c[0] for c in duck_conn.description]
            for row in rows:
                data = dict(zip(cols, row))
                sqlite_reg.conn.execute("""
                    INSERT OR REPLACE INTO datasets (workspace, name, latest_version, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                """, [data['workspace'], data['name'], data['latest_version'],
                      str(data.get('created_at', '')), str(data.get('updated_at', ''))])
                stats['datasets'] += 1
        except Exception as e:
            print(f"Warning migrating datasets: {e}")

        # Migrate versions
        try:
            rows = duck_conn.execute("SELECT * FROM versions").fetchall()
            cols = [c[0] for c in duck_conn.description]
            for row in rows:
                data = dict(zip(cols, row))
                sqlite_reg.conn.execute("""
                    INSERT OR REPLACE INTO versions (workspace, name, version_hash, manifest_json, storage_path, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, [data['workspace'], data['name'], data['version_hash'],
                      data.get('manifest_json'), data.get('storage_path'),
                      str(data.get('created_at', ''))])
                stats['versions'] += 1
        except Exception as e:
            print(f"Warning migrating versions: {e}")

        # Migrate embeddings_spaces
        try:
            rows = duck_conn.execute("SELECT * FROM embeddings_spaces").fetchall()
            cols = [c[0] for c in duck_conn.description]
            for row in rows:
                data = dict(zip(cols, row))
                sqlite_reg.conn.execute("""
                    INSERT OR REPLACE INTO embeddings_spaces
                    (workspace, name, version_hash, space_name, provider, model, dimension,
                     distance_metric, storage_path, row_count, vector_kind, normalized,
                     index_type, index_params, status, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, [data['workspace'], data['name'], data['version_hash'], data['space_name'],
                      data.get('provider'), data.get('model'), data.get('dimension'),
                      data.get('distance_metric', 'cosine'), data.get('storage_path'),
                      data.get('row_count'), data.get('vector_kind', 'float32'),
                      int(data.get('normalized', False)), data.get('index_type'),
                      data.get('index_params'), data.get('status', 'ready'),
                      str(data.get('created_at', '')), str(data.get('updated_at', ''))])
                stats['embeddings_spaces'] += 1
        except Exception as e:
            print(f"Warning migrating embeddings_spaces: {e}")

        # Migrate raw_data_sources
        try:
            rows = duck_conn.execute("SELECT * FROM raw_data_sources").fetchall()
            cols = [c[0] for c in duck_conn.description]
            for row in rows:
                data = dict(zip(cols, row))
                sqlite_reg.conn.execute("""
                    INSERT OR REPLACE INTO raw_data_sources
                    (workspace, name, version_hash, source_type, source_path, size, content_hash, metadata_json, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, [data['workspace'], data['name'], data['version_hash'],
                      data.get('source_type'), data.get('source_path'), data.get('size'),
                      data.get('content_hash'), data.get('metadata_json'),
                      str(data.get('created_at', ''))])
                stats['raw_data_sources'] += 1
        except Exception as e:
            print(f"Warning migrating raw_data_sources: {e}")

        sqlite_reg.conn.commit()

    finally:
        duck_conn.close()
        sqlite_reg.close()

    return stats


def auto_migrate_if_needed():
    """Auto-migrate from DuckDB to SQLite if DuckDB exists but SQLite doesn't."""
    from .config import get_config

    config = get_config()
    duckdb_path = config.registry_db.with_suffix(".duckdb")
    sqlite_path = config.registry_db.with_suffix(".sqlite")

    if duckdb_path.exists() and not sqlite_path.exists():
        print(f"Migrating registry from DuckDB to SQLite...")
        stats = migrate_duckdb_to_sqlite(duckdb_path, sqlite_path)
        print(f"  Migrated: {stats['datasets']} datasets, {stats['versions']} versions, "
              f"{stats['raw_data_sources']} raw data sources")

        # Rename old DuckDB file
        backup_path = duckdb_path.with_suffix(".duckdb.bak")
        duckdb_path.rename(backup_path)
        print(f"  Old registry backed up to: {backup_path}")

        return True

    return False


if __name__ == "__main__":
    auto_migrate_if_needed()
