"""
Base structures and utilities for complex recipes.

Provides RecipeOutput for recipes that create multiple datasets,
embeddings, and documentation.
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Any, Optional


@dataclass
class EmbeddingConfig:
    """
    Configuration for creating an embedding space.

    Attributes:
        space: Embedding space name
        provider: Provider ('numpy', 'sentence-transformers', 'openai')
        model: Model name (provider-specific)
        source: Source config (e.g., {'columns': ['text']})
        dimension: Embedding dimension (optional, inferred if not provided)
        distance_metric: Distance metric ('cosine', 'euclidean', 'dot')
        filter_sql: Optional SQL WHERE clause to filter data before embedding
        provider_kwargs: Additional provider-specific arguments
    """
    space: str
    provider: str
    source: Dict[str, Any]
    model: Optional[str] = None
    dimension: Optional[int] = None
    distance_metric: str = "cosine"
    filter_sql: Optional[str] = None
    provider_kwargs: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for run_recipe()."""
        result = {
            "space": self.space,
            "provider": self.provider,
            "source": self.source,
            "distance_metric": self.distance_metric,
        }
        if self.model:
            result["model"] = self.model
        if self.dimension:
            result["dimension"] = self.dimension
        if self.provider_kwargs:
            result.update(self.provider_kwargs)
        return result


@dataclass
class SubDataset:
    """
    Configuration for a sub-dataset with different schema or modality.

    ⚠️ WARNING: Only use subdatasets when absolutely necessary!

    Use subdatasets ONLY when:
    1. Different schema - e.g., COCO images table (image_id, path, width) vs
       captions table (image_id, caption_id, caption_text)
    2. Different modality - e.g., ArXiv PDFs vs extracted text vs metadata
    3. Multi-stage pipelines - intermediate results to keep separately

    DO NOT use subdatasets for:
    - Simple filtering (e.g., "male" vs "female" in CelebA) - just filter at
      query time: df[df['Male']] instead of creating physical subdatasets
    - Any case where data has same schema - wastes disk space with duplicates

    Attributes:
        name: Sub-dataset name (suffix after main dataset name)
        files: List of Parquet file paths
        description: Human-readable description
        filter_sql: SQL WHERE clause used to create this subset (for reference only)
        metadata: Additional metadata
    """
    name: str
    files: List[Path]
    description: str = ""
    filter_sql: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RecipeOutput:
    """
    Output from a complex recipe that creates multiple datasets.

    This allows recipes to create:
    - Main dataset
    - Multiple sub-datasets (ONLY if different schema/modality - see SubDataset docs)
    - Documentation files
    - Multiple embedding spaces
    - Custom metadata

    Examples of valid subdataset usage:
        # GOOD: Different schemas
        RecipeOutput(
            main=[images_parquet],
            subdatasets={
                'captions': SubDataset(name='captions', files=[captions_parquet]),
                'annotations': SubDataset(name='annotations', files=[annotations_parquet])
            }
        )

        # BAD: Same schema, just filtered (use query-time filtering instead!)
        RecipeOutput(
            main=[all_images_parquet],
            subdatasets={'male': SubDataset(...)}  # ❌ Wastes space - filter at query time!
        )

    Attributes:
        main: List of Parquet files for main dataset
        subdatasets: Dict of sub-dataset name -> SubDataset (use sparingly!)
        docs: Dict of filename -> content for documentation
        embeddings: List of embedding configurations
        metadata: Custom metadata for the dataset
        raw_data: List of raw data paths for provenance tracking (images, audio, PDFs, etc.)
    """
    main: List[Path]
    subdatasets: Dict[str, SubDataset] = field(default_factory=dict)
    docs: Dict[str, str] = field(default_factory=dict)
    embeddings: List[EmbeddingConfig] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    raw_data: List[Path] = field(default_factory=list)


def is_recipe_output(result: Any) -> bool:
    """Check if recipe result is RecipeOutput or simple List[Path]."""
    return isinstance(result, RecipeOutput)


def normalize_recipe_result(result) -> RecipeOutput:
    """
    Normalize recipe result to RecipeOutput.

    If recipe returns List[Path], wrap it in RecipeOutput.
    If recipe returns RecipeOutput, return as-is.

    Args:
        result: Recipe return value

    Returns:
        RecipeOutput instance
    """
    if isinstance(result, RecipeOutput):
        return result
    elif isinstance(result, list):
        # Legacy format: List[Path]
        return RecipeOutput(main=result)
    else:
        raise ValueError(
            f"Recipe must return RecipeOutput or List[Path], got {type(result)}"
        )
