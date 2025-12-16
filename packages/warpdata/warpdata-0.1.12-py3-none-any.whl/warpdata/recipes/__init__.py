"""
Built-in recipes for warpdata.

This module previously contained many vendor-specific recipes (polygon, coingecko,
binance, arxiv, etc.) which have been moved to extracted_recipes/ to keep the
core library lightweight.

To add custom recipes, use warpdata.register_recipe() in your own code.
"""


def register_builtin_recipes():
    """
    No built-in recipes are registered by default to keep the core library lightweight.
    User-defined recipes should be registered in user code.
    """
    pass


__all__ = ["register_builtin_recipes"]
