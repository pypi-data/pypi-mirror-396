"""
Lazy loaders for vision datasets (images).

Provides efficient lazy loading of images from path columns.
"""
from pathlib import Path
from typing import Union, List, Optional, Tuple
import pandas as pd


class ImageColumn:
    """
    Lazy image loader for path columns.

    Loads images on-demand when indexed, avoiding memory overhead
    of loading all images upfront.

    Examples:
        >>> import warpdata as wd
        >>> from warpdata.loaders import ImageColumn
        >>>
        >>> df = wd.load("warpdata://vision/celeba", as_format="pandas")
        >>> images = ImageColumn(df['image_path'])
        >>>
        >>> # Load single image
        >>> img = images[0]  # PIL.Image
        >>> img.show()
        >>>
        >>> # Load batch
        >>> batch = images[0:10]  # List of PIL.Image
        >>>
        >>> # Iterate
        >>> for img in images[:5]:
        ...     print(img.size)
    """

    def __init__(self, paths: Union[pd.Series, List[str], List[Path]]):
        """
        Initialize lazy image loader.

        Args:
            paths: Series or list of image file paths
        """
        if isinstance(paths, pd.Series):
            self.paths = paths.tolist()
        else:
            self.paths = [Path(p) if not isinstance(p, Path) else p for p in paths]

    def __len__(self):
        """Return number of images."""
        return len(self.paths)

    def __getitem__(self, idx):
        """
        Load image(s) at index.

        Args:
            idx: int or slice

        Returns:
            PIL.Image for int index, List[PIL.Image] for slice
        """
        try:
            from PIL import Image
        except ImportError:
            raise ImportError(
                "Pillow is required for image loading. "
                "Install with: pip install Pillow"
            )

        if isinstance(idx, slice):
            # Batch loading
            paths = self.paths[idx]
            return [Image.open(p) for p in paths]
        else:
            # Single image
            return Image.open(self.paths[idx])

    def load(self, idx: Union[int, slice]):
        """
        Alias for __getitem__ for explicit loading.

        Args:
            idx: Index or slice

        Returns:
            PIL.Image or List[PIL.Image]
        """
        return self[idx]

    def load_batch(self, indices: List[int]):
        """
        Load multiple images by index list.

        Args:
            indices: List of indices to load

        Returns:
            List[PIL.Image]
        """
        try:
            from PIL import Image
        except ImportError:
            raise ImportError(
                "Pillow is required for image loading. "
                "Install with: pip install Pillow"
            )

        return [Image.open(self.paths[i]) for i in indices]

    def to_array(self, idx: Union[int, slice], size: Optional[Tuple[int, int]] = None):
        """
        Load image(s) as numpy arrays.

        Args:
            idx: Index or slice
            size: Optional (width, height) to resize images

        Returns:
            np.ndarray for single image, List[np.ndarray] for batch
        """
        import numpy as np

        images = self[idx]

        if isinstance(idx, slice):
            # Batch
            arrays = []
            for img in images:
                if size:
                    img = img.resize(size)
                arrays.append(np.array(img))
            return arrays
        else:
            # Single
            if size:
                images = images.resize(size)
            return np.array(images)


def load_image_column(paths: Union[pd.Series, List[str]]) -> ImageColumn:
    """
    Create lazy image loader from path column.

    Args:
        paths: Series or list of image paths

    Returns:
        ImageColumn lazy loader

    Examples:
        >>> from warpdata.loaders import load_image_column
        >>>
        >>> df = wd.load("warpdata://vision/celeba")
        >>> images = load_image_column(df['image_path'])
        >>>
        >>> # Load first image
        >>> img = images[0]
        >>> img.show()
        >>>
        >>> # Load batch as arrays
        >>> arrays = images.to_array(slice(0, 10), size=(224, 224))
    """
    return ImageColumn(paths)
