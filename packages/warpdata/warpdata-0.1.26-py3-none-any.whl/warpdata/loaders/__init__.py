"""
Binary data loaders for images and audio.

Provides lazy loading utilities for binary data referenced by paths in datasets.
Reduces memory usage and provides consistent interfaces across modalities.
"""
from .vision import ImageColumn, load_image_column
from .audio import AudioColumn, load_audio_column

__all__ = [
    "ImageColumn",
    "AudioColumn",
    "load_image_column",
    "load_audio_column",
]
