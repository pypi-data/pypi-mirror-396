"""
Registry for dataset metadata.

Uses SQLite with WAL mode for concurrent access.
Auto-migrates from DuckDB if needed.
"""
# Auto-migrate from DuckDB to SQLite on first import
from .migrate_registry import auto_migrate_if_needed

try:
    auto_migrate_if_needed()
except Exception as e:
    print(f"Warning: Registry migration check failed: {e}")

# Re-export everything from SQLite registry
from .registry_sqlite import (
    Registry,
    get_registry,
    get_registry_readonly,
    reset_registry,
)

__all__ = [
    'Registry',
    'get_registry',
    'get_registry_readonly',
    'reset_registry',
]
