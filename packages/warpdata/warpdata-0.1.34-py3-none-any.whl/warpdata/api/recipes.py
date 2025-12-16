"""
Recipes API for warpdata.

Provides a simple framework for creating reusable data pipelines that:
- Download/resolve sources (via cache and fsspec)
- Transform data with DuckDB (SQL or Python)
- Write normalized Parquet files
- Register results as versioned datasets
- Create sub-datasets (filtered views)
- Generate multiple embedding spaces
- Write documentation (notes.md, README.md, schema.json)
- Optionally materialize and add embeddings

Recipes can return List[Path] (simple) or RecipeOutput (advanced).
"""
from pathlib import Path
from typing import Callable, Dict, Any, List, Optional, Union

from ..core.cache import get_cache
from ..core.uris import parse_uri
from ..core.utils import ensure_dir
from ..engine.duck import get_engine
from .management import register_dataset

# Import recipe output structures
from ..recipes.base import (
    RecipeOutput,
    SubDataset,
    EmbeddingConfig,
    normalize_recipe_result,
)

# In-memory registry for recipe callables
_RECIPES: Dict[str, Callable[..., Union[List[Path], RecipeOutput]]] = {}


class RecipeContext:
    """
    Context object passed to recipe functions.

    Provides helpers for:
    - Downloading sources (any fsspec protocol)
    - Writing Parquet outputs
    - Accessing DuckDB engine
    - Managing work directory
    """

    def __init__(self, dataset_id: str, work_dir: Optional[Path] = None):
        """
        Initialize recipe context.

        Args:
            dataset_id: Target dataset ID (e.g., 'warpdata://workspace/name')
            work_dir: Working directory for outputs (defaults to dataset cache dir)
        """
        self.dataset_id = dataset_id
        self.uri = parse_uri(dataset_id)
        self.cache = get_cache()
        self.engine = get_engine()

        # Where normalized outputs go (local)
        # Keep under dataset cache for simplicity and cleanup locality
        if work_dir is None:
            # Use a "recipes" subdirectory in the dataset cache
            ds_dir = self.cache.get_dataset_cache_dir(
                self.uri.workspace, self.uri.name, "recipes"
            )
            self.work_dir = ensure_dir(ds_dir)
        else:
            self.work_dir = ensure_dir(work_dir)

    def download(self, source: str) -> Path:
        """
        Download a source file to local cache.

        Uses fsspec + cache; supports s3://, http(s)://, hf://, file://, etc.

        Args:
            source: Source URI to download

        Returns:
            Path to local cached file
        """
        return self.cache.get(source)

    def write_parquet(self, relation, out_path: Path):
        """
        Write a DuckDB relation to Parquet file.

        Args:
            relation: DuckDB relation object
            out_path: Output path for Parquet file
        """
        out_path.parent.mkdir(parents=True, exist_ok=True)
        # Use DuckDB's COPY to write efficiently
        self.engine.conn.execute(
            f"COPY (SELECT * FROM relation) TO '{out_path}' (FORMAT PARQUET)"
        )

    def write_documentation(self, filename: str, content: str):
        """
        Write documentation file to dataset directory.

        Files are written to work_dir/docs/ and will be accessible
        after dataset registration.

        Args:
            filename: Documentation filename (e.g., 'notes.md', 'README.md')
            content: File content

        Examples:
            >>> ctx.write_documentation('notes.md', '# Dataset Notes\\n...')
            >>> ctx.write_documentation('schema.json', json.dumps(schema))
        """
        docs_dir = self.work_dir / "docs"
        docs_dir.mkdir(parents=True, exist_ok=True)

        doc_path = docs_dir / filename
        doc_path.write_text(content, encoding='utf-8')

    def filter_and_write(
        self,
        relation,
        out_path: Path,
        filter_sql: Optional[str] = None
    ) -> Path:
        """
        Filter a relation and write to Parquet.

        Args:
            relation: DuckDB relation to filter
            out_path: Output path for filtered data
            filter_sql: SQL WHERE clause (without WHERE keyword)

        Returns:
            Path to written file

        Examples:
            >>> ctx.filter_and_write(
            ...     main_data,
            ...     ctx.work_dir / "dmt_only.parquet",
            ...     filter_sql="condition = 'DMT'"
            ... )
        """
        if filter_sql:
            filtered = self.engine.conn.sql(f"""
                SELECT * FROM relation WHERE {filter_sql}
            """)
        else:
            filtered = relation

        self.write_parquet(filtered, out_path)
        return out_path


def register_recipe(name: str, fn: Callable[..., List[Path]]):
    """
    Register a recipe function.

    A recipe function should have signature:
        fn(ctx: RecipeContext, **options) -> List[Path]

    Args:
        name: Recipe name (used for lookup)
        fn: Recipe callable that returns list of output Parquet paths
    """
    _RECIPES[name] = fn


def list_recipes() -> List[str]:
    """
    List all registered recipes.

    Returns:
        Sorted list of recipe names
    """
    return sorted(_RECIPES.keys())


def run_recipe(
    name: str,
    dataset_id: str,
    with_materialize: bool = False,
    embeddings: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None,
    schema: Optional[Dict[str, str]] = None,
    work_dir: Optional[Path] = None,
    **options,
) -> Union[str, Dict[str, Any]]:
    """
    Run a recipe to create a dataset (and optionally sub-datasets).

    Args:
        name: Recipe name
        dataset_id: Target dataset ID (e.g., 'warpdata://workspace/name')
        with_materialize: If True, materialize dataset after creation
        embeddings: Optional embeddings config (single dict or list of dicts):
            {
                "provider": "sentence-transformers",
                "model": "all-MiniLM-L6-v2",
                "space": "default",
                "source": {"columns": ["text"]},
                "dimension": 384,  # optional
                "distance_metric": "cosine"  # optional
            }
        schema: Optional schema dict (column -> type)
        work_dir: Optional working directory for recipe outputs
        **options: Additional options passed to recipe function

    Returns:
        If recipe returns simple List[Path]: version hash (str)
        If recipe returns RecipeOutput: dict with:
            {
                'main': version_hash,
                'subdatasets': {name: version_hash},
                'docs': {filename: path}
            }

    Raises:
        ValueError: If recipe not found or produces no outputs

    Examples:
        >>> import warpdata as wd

        >>> # Simple recipe
        >>> version = wd.run_recipe("wine_quality", "warpdata://uci/wine")

        >>> # Complex recipe with sub-datasets
        >>> result = wd.run_recipe("dmt_brains", "warpdata://neuro/dmt",
        ...                        data_dir="./data/dmt_brains")
        >>> print(result['subdatasets'])  # {'dmt-only': 'hash...', ...}
    """
    if name not in _RECIPES:
        available = list_recipes()
        raise ValueError(
            f"Recipe '{name}' not found. Available: {available}"
        )

    # Create context
    ctx = RecipeContext(dataset_id, work_dir=work_dir)

    # Execute recipe
    result = _RECIPES[name](ctx, **options)

    # Normalize to RecipeOutput
    recipe_output = normalize_recipe_result(result)

    if not recipe_output.main:
        raise ValueError("Recipe produced no outputs")

    # Register main dataset
    resources = [f"file://{p}" for p in recipe_output.main]

    # Prepare raw data paths (convert to strings)
    raw_data_paths = [str(p) for p in recipe_output.raw_data] if recipe_output.raw_data else None

    main_version = register_dataset(
        dataset_id,
        resources=resources,
        schema=schema,
        metadata={
            "recipe": name,
            "options": options,
            **recipe_output.metadata
        },
        raw_data=raw_data_paths,
    )

    # Register sub-datasets (DEPRECATED)
    subdataset_versions = {}
    if recipe_output.subdatasets:
        import warnings
        warnings.warn(
            "Subdatasets are deprecated. Consider using separate datasets or "
            "query-time filtering instead. Subdataset registration will be skipped.",
            DeprecationWarning,
            stacklevel=2
        )

    # Note: materialize is no longer needed since data is ingested into DuckDB
    # Note: embeddings are deprecated in v2 - use external vector DB instead

    # Return version hash
    return main_version


def reset_recipes():
    """
    Reset the recipe registry.

    Useful for testing to ensure clean state.
    """
    global _RECIPES
    _RECIPES = {}
