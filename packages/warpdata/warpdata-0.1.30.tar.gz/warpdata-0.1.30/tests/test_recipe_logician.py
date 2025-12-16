"""
Tests for logician recipe with FOL symbolization via pysymbolizer.
"""
import tempfile
import json
from pathlib import Path
import pytest
import pandas as pd

# Skip if pysymbolizer with FOL support not available
pytest.importorskip("pysymbolizer")

import warpdata as wd


class TestLogicianRecipe:
    """Test logician recipe with FOL symbolization."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Reset recipes before each test."""
        wd.reset_recipes()
        from warpdata.recipes import register_builtin_recipes
        register_builtin_recipes()
        yield
        wd.reset_recipes()
        from warpdata.recipes import register_builtin_recipes
        register_builtin_recipes()

    def test_logician_recipe_registered(self):
        """Test that logician recipe is registered."""
        recipes = wd.list_recipes()
        assert "logician" in recipes

    def test_pysymbolizer_fol_parsing(self):
        """Test pysymbolizer can parse FOL formulas."""
        try:
            from pysymbolizer.parsers.logician import parse_logician
        except ImportError:
            pytest.skip("pysymbolizer FOL parser not available")

        # Test simple quantifier
        expr = parse_logician("forall x: P(x)")
        assert expr is not None

        # Test complex formula
        expr = parse_logician("forall x: P(x) -> Q(x)")
        assert expr is not None

        # Test existential
        expr = parse_logician("exists y: R(y)")
        assert expr is not None

    def test_extract_formulas(self):
        """Test formula extraction from text."""
        from warpdata.recipes.logician import _extract_formulas_from_text

        # Single formula
        text = "forall x: P(x) -> Q(x)"
        formulas = _extract_formulas_from_text(text)
        assert len(formulas) >= 1
        assert "forall" in formulas[0].lower()

        # Multiple formulas
        text = "forall x: P(x). exists y: Q(y). Can we infer?"
        formulas = _extract_formulas_from_text(text)
        assert len(formulas) >= 2

        # Mixed text
        text = "Consider: forall x: P(x) -> Q(x). Therefore exists y: R(y)."
        formulas = _extract_formulas_from_text(text)
        assert len(formulas) >= 2

    def test_count_quantifiers(self):
        """Test quantifier counting."""
        from warpdata.recipes.logician import _count_quantifiers

        text = "forall x: P(x). exists y: Q(y). forall z: R(z)."
        n_forall, n_exists = _count_quantifiers(text)
        assert n_forall == 2
        assert n_exists == 1

    def test_logician_with_mock_data(self, tmp_path):
        """Test logician recipe with mock parquet data."""
        # Create mock data matching logician dataset structure
        mock_data = pd.DataFrame([
            {
                "instruction": "What can be inferred from: forall x: P(x) -> Q(x). P(a). Respond using formal logic.",
                "response": "Q(a) can be inferred via universal modus ponens.",
                "source": "LogicInference_OA"
            },
            {
                "instruction": "Consider: forall x: R(x) or S(x). Can we infer exists x: R(x)?",
                "response": "That contradicts the premises. Therefore the answer is no.",
                "source": "LogicInference_OA"
            },
            {
                "instruction": "A person has 10 apples. Based on the above, label the following as true or false: The person has 5 apples.",
                "response": "False.",
                "source": "EQUATE"
            },
            {
                "instruction": "All dogs are animals. Translate to first-order logic.",
                "response": "forall x: Dog(x) -> Animal(x)",
                "source": "FOLIO"
            }
        ])

        # Save as parquet
        mock_path = tmp_path / "train.parquet"
        mock_data.to_parquet(mock_path)

        from warpdata.api.recipes import RecipeContext
        from warpdata.recipes.logician import logician

        work_dir = tmp_path / "work"
        work_dir.mkdir()

        ctx = RecipeContext(
            dataset_id="warpdata://logic/logician-test",
            work_dir=work_dir,
        )

        # Monkey-patch download to return local file
        def mock_download(url):
            return mock_path
        ctx.download = mock_download

        # Run recipe with symbolization
        result = logician(
            ctx,
            repo_id="euclaise/logician",
            splits=("train",),
            symbolize=True,
            codebook_m=16
        )

        # Verify result structure
        assert result.main is not None
        assert len(result.main) == 1
        assert result.subdatasets is not None
        assert "formulas" in result.subdatasets

        # Load and verify main dataset
        main_rel = ctx.engine.conn.read_parquet(str(result.main[0]))
        main_df = main_rel.df()

        assert len(main_df) == 4
        assert "id" in main_df.columns
        assert "instruction" in main_df.columns
        assert "response" in main_df.columns
        assert "source" in main_df.columns
        assert "n_formulas" in main_df.columns
        assert "n_forall" in main_df.columns
        assert "n_exists" in main_df.columns

        # Check quantifier counts
        assert main_df["n_forall"].sum() > 0
        assert main_df["n_exists"].sum() >= 0

        # Load and verify formulas subdataset
        formulas_path = result.subdatasets["formulas"].files[0]
        formulas_rel = ctx.engine.conn.read_parquet(str(formulas_path))
        formulas_df = formulas_rel.df()

        assert len(formulas_df) > 0
        assert "id" in formulas_df.columns
        assert "formula_idx" in formulas_df.columns
        assert "formula" in formulas_df.columns
        assert "formula_source" in formulas_df.columns
        assert "tokens_json" in formulas_df.columns
        assert "bits_hex" in formulas_df.columns

        # Check that symbolization worked for at least some formulas
        valid_tokens = formulas_df["tokens_json"].notna().sum()
        assert valid_tokens > 0, "No formulas were successfully symbolized"

    def test_logician_without_symbolization(self, tmp_path):
        """Test logician recipe with symbolize=False."""
        mock_data = pd.DataFrame([
            {
                "instruction": "forall x: P(x)",
                "response": "Q(a)",
                "source": "LogicInference_OA"
            }
        ])

        mock_path = tmp_path / "train.parquet"
        mock_data.to_parquet(mock_path)

        from warpdata.api.recipes import RecipeContext
        from warpdata.recipes.logician import logician

        work_dir = tmp_path / "work"
        work_dir.mkdir()

        ctx = RecipeContext(
            dataset_id="warpdata://logic/logician-nosym",
            work_dir=work_dir,
        )

        def mock_download(url):
            return mock_path
        ctx.download = mock_download

        # Run recipe without symbolization
        result = logician(
            ctx,
            splits=("train",),
            symbolize=False
        )

        # Verify main dataset exists
        assert result.main is not None
        main_rel = ctx.engine.conn.read_parquet(str(result.main[0]))
        main_df = main_rel.df()
        assert len(main_df) == 1

        # Formulas subdataset should exist but without tokens/bits
        if "formulas" in result.subdatasets:
            formulas_path = result.subdatasets["formulas"].files[0]
            formulas_rel = ctx.engine.conn.read_parquet(str(formulas_path))
            formulas_df = formulas_rel.df()
            # All tokens/bits should be null
            assert formulas_df["tokens_json"].isna().all()
            assert formulas_df["bits_hex"].isna().all()

    def test_source_subdatasets(self, tmp_path):
        """Test that source-based subdatasets are created."""
        mock_data = pd.DataFrame([
            {"instruction": "test1", "response": "resp1", "source": "LogicInference_OA"},
            {"instruction": "test2", "response": "resp2", "source": "EQUATE"},
            {"instruction": "test3", "response": "resp3", "source": "FOLIO"},
        ])

        mock_path = tmp_path / "train.parquet"
        mock_data.to_parquet(mock_path)

        from warpdata.api.recipes import RecipeContext
        from warpdata.recipes.logician import logician

        work_dir = tmp_path / "work"
        work_dir.mkdir()

        ctx = RecipeContext(
            dataset_id="warpdata://logic/logician-sources",
            work_dir=work_dir,
        )

        def mock_download(url):
            return mock_path
        ctx.download = mock_download

        result = logician(ctx, splits=("train",), symbolize=False)

        # Check subdatasets exist
        assert "logicinferenceoa" in result.subdatasets
        assert "equate" in result.subdatasets
        assert "folio" in result.subdatasets

    def test_symbolize_formula(self):
        """Test formula symbolization."""
        try:
            from pysymbolizer import adapter_lmode_from_corpus, L_DOM
            from pysymbolizer.parsers.logician import parse_logician
            from warpdata.recipes.logician import _symbolize_formula
        except ImportError:
            pytest.skip("pysymbolizer FOL support not available")

        # Build adapter
        corpus = [
            parse_logician("forall x: P(x)"),
            parse_logician("exists y: Q(y)"),
        ]
        adapter = adapter_lmode_from_corpus(corpus, m=16, domain=L_DOM)

        # Symbolize
        tokens_json, bits_hex = _symbolize_formula("forall x: P(x)", adapter)

        assert tokens_json is not None
        assert bits_hex is not None

        # Verify tokens are valid JSON
        tokens = json.loads(tokens_json)
        assert isinstance(tokens, list)
        assert len(tokens) > 0

        # Verify bits are hex
        assert all(c in '0123456789abcdef' for c in bits_hex)
