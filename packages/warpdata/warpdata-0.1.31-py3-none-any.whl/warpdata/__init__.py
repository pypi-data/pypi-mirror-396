"""
warpdata: A High-Performance Pythonic Data SDK

A developer-first toolkit for accessing, versioning, and augmenting
datasets for analytics and machine learning.

Now powered by pure DuckDB for both storage and compute.
"""

__version__ = "0.1.31"

# Core data loading API
from .api.data import load, schema, head, resolve_paths

# Image dataset utilities
from .api.images import (
    is_image_dataset,
    get_image_columns,
    decode_image,
    decode_images_column,
    load_images,
    image_dataset_info,
)

# Dataset management API
from .api.management import (
    register_dataset,
    list_datasets,
    dataset_info,
    remove_dataset,
    verify_dataset,
    verify_datasets,
)

# Recipes API (simplified - no built-in recipes)
from .api.recipes import (
    register_recipe,
    list_recipes,
    run_recipe,
    reset_recipes,
    RecipeContext,
)

# Storage/provenance API
from .api.storage import get_raw_data_sources, backup_dataset, sync_to_cloud

# Streaming API
from .api.streaming import stream, stream_batch_dicts

# PyTorch integration (optional - requires torch)
try:
    from .pytorch import WarpDataset
except ImportError:
    WarpDataset = None  # torch not installed

# Register built-in recipes after imports are complete
try:
    from .recipes import register_builtin_recipes
    register_builtin_recipes()
except Exception:
    pass  # No built-in recipes in v2

# Re-export for convenience
__all__ = [
    # Data loading
    "load",
    "schema",
    "head",
    "resolve_paths",
    # Image utilities
    "is_image_dataset",
    "get_image_columns",
    "decode_image",
    "decode_images_column",
    "load_images",
    "image_dataset_info",
    # Management
    "register_dataset",
    "list_datasets",
    "dataset_info",
    "remove_dataset",
    "verify_dataset",
    "verify_datasets",
    # Recipes
    "register_recipe",
    "list_recipes",
    "run_recipe",
    "reset_recipes",
    "RecipeContext",
    # Storage/provenance
    "get_raw_data_sources",
    "backup_dataset",
    "sync_to_cloud",
    # Streaming
    "stream",
    "stream_batch_dicts",
    # PyTorch integration
    "WarpDataset",
    # Version
    "__version__",
]
