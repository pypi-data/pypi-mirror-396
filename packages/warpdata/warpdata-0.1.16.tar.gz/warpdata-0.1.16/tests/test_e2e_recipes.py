"""
End-to-end tests for recipes API.

Tests cover:
- Recipe registration and listing
- Running recipes to produce datasets
- Integration with materialize and embeddings
- Error handling
"""
import pytest
from pathlib import Path
from typing import List

import warpdata as wd
from warpdata.api.recipes import (
    register_recipe,
    list_recipes,
    run_recipe,
    RecipeContext,
    reset_recipes,
)


class TestRecipeRegistration:
    """Test recipe registration and listing."""

    def test_register_and_list_recipe(self, temp_home):
        """Test registering a recipe and listing it."""
        reset_recipes()

        def simple_recipe(ctx: RecipeContext) -> List[Path]:
            return []

        register_recipe("test_recipe", simple_recipe)

        recipes = list_recipes()
        assert "test_recipe" in recipes

    def test_list_multiple_recipes(self, temp_home):
        """Test listing multiple recipes."""
        reset_recipes()

        def recipe1(ctx: RecipeContext) -> List[Path]:
            return []

        def recipe2(ctx: RecipeContext) -> List[Path]:
            return []

        register_recipe("recipe_a", recipe1)
        register_recipe("recipe_b", recipe2)

        recipes = list_recipes()
        assert len(recipes) == 2
        assert "recipe_a" in recipes
        assert "recipe_b" in recipes
        # Should be sorted
        assert recipes == sorted(recipes)


class TestRecipeExecution:
    """Test running recipes."""

    def test_run_simple_recipe(self, temp_home, tmp_path):
        """Test running a basic recipe that creates a Parquet file."""
        reset_recipes()

        def simple_recipe(ctx: RecipeContext) -> List[Path]:
            # Create a simple table with DuckDB
            relation = ctx.engine.conn.sql("""
                SELECT
                    i AS id,
                    'item_' || i AS name,
                    i * 10 AS value
                FROM generate_series(1, 100) AS t(i)
            """)

            out_path = ctx.work_dir / "data.parquet"
            ctx.write_parquet(relation, out_path)
            return [out_path]

        register_recipe("simple", simple_recipe)

        version = run_recipe("simple", "warpdata://test/simple-data")

        # Verify dataset was registered
        assert version is not None
        datasets = wd.list_datasets(workspace="test")
        assert len(datasets) == 1
        assert datasets[0]["name"] == "simple-data"

        # Verify we can load the data
        data = wd.load("warpdata://test/simple-data", as_format="pandas")
        assert len(data) == 100
        assert "id" in data.columns
        assert "name" in data.columns
        assert "value" in data.columns

    def test_run_recipe_with_download(self, temp_home, tmp_path):
        """Test recipe that downloads a source file."""
        reset_recipes()

        # Create a local CSV file to act as a source
        source_csv = tmp_path / "source.csv"
        source_csv.write_text("id,name,score\n1,Alice,95\n2,Bob,87\n3,Charlie,92\n")

        def download_recipe(ctx: RecipeContext, source_url: str) -> List[Path]:
            # Download the source
            local_path = ctx.download(source_url)

            # Load and transform with DuckDB
            relation = ctx.engine.conn.read_csv(str(local_path), header=True)
            transformed = ctx.engine.conn.sql("""
                SELECT
                    id,
                    UPPER(name) AS name_upper,
                    score,
                    CASE WHEN score >= 90 THEN 'A' ELSE 'B' END AS grade
                FROM relation
            """)

            out_path = ctx.work_dir / "transformed.parquet"
            ctx.write_parquet(transformed, out_path)
            return [out_path]

        register_recipe("download_transform", download_recipe)

        version = run_recipe(
            "download_transform",
            "warpdata://test/scores",
            source_url=f"file://{source_csv}",
        )

        # Verify the transformed data
        data = wd.load("warpdata://test/scores", as_format="pandas")
        assert len(data) == 3
        assert "name_upper" in data.columns
        assert "grade" in data.columns
        assert data["name_upper"].tolist() == ["ALICE", "BOB", "CHARLIE"]

    def test_run_recipe_with_multiple_outputs(self, temp_home):
        """Test recipe that produces multiple partitioned files."""
        reset_recipes()

        def partitioned_recipe(ctx: RecipeContext) -> List[Path]:
            # Create data with categories
            relation = ctx.engine.conn.sql("""
                SELECT
                    i AS id,
                    CASE
                        WHEN i <= 30 THEN 'A'
                        WHEN i <= 60 THEN 'B'
                        ELSE 'C'
                    END AS category,
                    i * 10 AS value
                FROM generate_series(1, 90) AS t(i)
            """)

            # Write partitioned outputs
            outputs = []
            for cat in ["A", "B", "C"]:
                out_path = ctx.work_dir / f"category_{cat}.parquet"
                partition = ctx.engine.conn.sql(f"""
                    SELECT * FROM relation WHERE category = '{cat}'
                """)
                ctx.write_parquet(partition, out_path)
                outputs.append(out_path)

            return outputs

        register_recipe("partitioned", partitioned_recipe)

        version = run_recipe("partitioned", "warpdata://test/partitioned-data")

        # Verify all partitions are loaded
        data = wd.load("warpdata://test/partitioned-data", as_format="pandas")
        assert len(data) == 90
        assert set(data["category"].unique()) == {"A", "B", "C"}

        # Verify info shows multiple resources
        info = wd.dataset_info("warpdata://test/partitioned-data")
        assert len(info["manifest"]["resources"]) == 3


class TestRecipeWithMaterialize:
    """Test running recipes with materialization."""

    def test_run_recipe_with_materialize(self, temp_home):
        """Test recipe with automatic materialization."""
        reset_recipes()

        def basic_recipe(ctx: RecipeContext) -> List[Path]:
            relation = ctx.engine.conn.sql("""
                SELECT i AS id, 'text_' || i AS text
                FROM generate_series(1, 50) AS t(i)
            """)
            out_path = ctx.work_dir / "data.parquet"
            ctx.write_parquet(relation, out_path)
            return [out_path]

        register_recipe("basic", basic_recipe)

        version = run_recipe("basic", "warpdata://test/basic-mat", with_materialize=True)

        # Verify materialized file exists
        info = wd.dataset_info("warpdata://test/basic-mat")
        from warpdata.core.cache import get_cache

        cache = get_cache()
        ds_dir = cache.get_dataset_cache_dir(
            "test", "basic-mat", info["version_hash"]
        )
        mat_path = ds_dir / "materialized.parquet"
        assert mat_path.exists()

        # Verify rid column exists
        data = wd.load(str(mat_path), as_format="pandas")
        assert "rid" in data.columns


class TestRecipeWithEmbeddings:
    """Test running recipes with embeddings."""

    def test_run_recipe_with_embeddings(self, temp_home):
        """Test recipe with automatic embedding generation."""
        reset_recipes()

        def text_recipe(ctx: RecipeContext) -> List[Path]:
            relation = ctx.engine.conn.sql("""
                SELECT
                    i AS id,
                    'This is sample text number ' || i AS text
                FROM generate_series(1, 20) AS t(i)
            """)
            out_path = ctx.work_dir / "text_data.parquet"
            ctx.write_parquet(relation, out_path)
            return [out_path]

        register_recipe("text_data", text_recipe)

        embeddings_config = {
            "provider": "numpy",
            "space": "test-space",
            "source": {"columns": ["text"]},
            "dimension": 128,
        }

        version = run_recipe(
            "text_data",
            "warpdata://test/text-with-embeddings",
            with_materialize=True,  # Required for embeddings
            embeddings=embeddings_config,
        )

        # Verify embeddings were added
        spaces = wd.list_embeddings("warpdata://test/text-with-embeddings")
        assert len(spaces) == 1
        assert spaces[0]["space_name"] == "test-space"
        assert spaces[0]["dimension"] == 128

        # Verify we can search
        results = wd.search_embeddings(
            "warpdata://test/text-with-embeddings",
            space="test-space",
            query="sample text",
            top_k=5,
        )
        assert len(results) == 5


class TestRecipeErrorHandling:
    """Test error handling in recipes."""

    def test_run_nonexistent_recipe(self, temp_home):
        """Test running a recipe that doesn't exist."""
        reset_recipes()

        with pytest.raises(ValueError, match="Recipe 'nonexistent' not found"):
            run_recipe("nonexistent", "warpdata://test/fail")

    def test_recipe_with_no_outputs(self, temp_home):
        """Test recipe that produces no output files."""
        reset_recipes()

        def empty_recipe(ctx: RecipeContext) -> List[Path]:
            return []

        register_recipe("empty", empty_recipe)

        with pytest.raises(ValueError, match="Recipe produced no outputs"):
            run_recipe("empty", "warpdata://test/empty-fail")

    def test_recipe_with_invalid_source(self, temp_home):
        """Test recipe that tries to download nonexistent source."""
        reset_recipes()

        def bad_download_recipe(ctx: RecipeContext) -> List[Path]:
            # Try to download a nonexistent file
            ctx.download("file:///nonexistent/file.csv")
            return []

        register_recipe("bad_download", bad_download_recipe)

        with pytest.raises(Exception):  # Should raise FileNotFoundError or similar
            run_recipe("bad_download", "warpdata://test/bad")

    def test_recipe_with_custom_schema(self, temp_home):
        """Test passing custom schema to run_recipe."""
        reset_recipes()

        def simple_recipe(ctx: RecipeContext) -> List[Path]:
            relation = ctx.engine.conn.sql("""
                SELECT i AS id, 'value' AS text
                FROM generate_series(1, 10) AS t(i)
            """)
            out_path = ctx.work_dir / "data.parquet"
            ctx.write_parquet(relation, out_path)
            return [out_path]

        register_recipe("with_schema", simple_recipe)

        custom_schema = {"id": "BIGINT", "text": "VARCHAR"}

        version = run_recipe(
            "with_schema",
            "warpdata://test/with-schema",
            schema=custom_schema,
        )

        info = wd.dataset_info("warpdata://test/with-schema")
        assert info["manifest"]["schema"] == custom_schema


class TestRecipeContext:
    """Test RecipeContext helper functionality."""

    def test_recipe_context_initialization(self, temp_home):
        """Test RecipeContext initializes correctly."""
        ctx = RecipeContext("warpdata://test/my-dataset")

        assert ctx.dataset_id == "warpdata://test/my-dataset"
        assert ctx.uri.workspace == "test"
        assert ctx.uri.name == "my-dataset"
        assert ctx.work_dir is not None
        assert ctx.work_dir.exists()

    def test_recipe_context_custom_work_dir(self, temp_home, tmp_path):
        """Test RecipeContext with custom work directory."""
        custom_dir = tmp_path / "custom_work"
        ctx = RecipeContext("warpdata://test/my-dataset", work_dir=custom_dir)

        assert ctx.work_dir == custom_dir
        assert ctx.work_dir.exists()
