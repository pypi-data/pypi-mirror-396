"""
Tests for GSM8K recipe with pysymbolizer integration.
"""
import tempfile
import json
from pathlib import Path
import pytest

# Skip if pysymbolizer not available
pytest.importorskip("pysymbolizer")
pytest.importorskip("sympy")

import warpdata as wd


class TestGSM8KRecipe:
    """Test GSM8K recipe with symbolic encoding."""

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

    def test_gsm8k_recipe_registered(self):
        """Test that gsm8k recipe is registered."""
        recipes = wd.list_recipes()
        assert "gsm8k" in recipes

    def test_gsm8k_with_mock_data(self, tmp_path):
        """Test GSM8K recipe with mock JSONL data."""
        # Create mock GSM8K data
        mock_data_dir = tmp_path / "mock_gsm8k"
        mock_data_dir.mkdir()

        # Create train.jsonl with sample problems
        train_data = [
            {
                "question": "Janet's ducks lay 16 eggs per day. She eats three for breakfast every morning and bakes muffins for her friends every day with four. She sells the remainder at the farmers' market daily for $2 per fresh duck egg. How much in dollars does she make every day at the farmers' market?",
                "answer": "Janet sells 16 - 3 - 4 = <<16-3-4=9>>9 duck eggs a day.\nShe makes 9 * 2 = $<<9*2=18>>18 every day at the farmer's market.\n#### 18"
            },
            {
                "question": "A robe takes 2 bolts of blue fiber and half that much white fiber. How many bolts in total does it take?",
                "answer": "It takes 2/2=<<2/2=1>>1 bolt of white fiber\nSo the total amount of fabric is 2+1=<<2+1=3>>3 bolts of fabric\n#### 3"
            }
        ]

        train_path = mock_data_dir / "train.jsonl"
        with open(train_path, 'w') as f:
            for item in train_data:
                f.write(json.dumps(item) + '\n')

        # Create test.jsonl
        test_data = [
            {
                "question": "A baker makes 24 cupcakes. He sells half of them. How many are left?",
                "answer": "He sells 24/2 = <<24/2=12>>12 cupcakes.\nSo he has 24 - 12 = <<24-12=12>>12 left.\n#### 12"
            }
        ]

        test_path = mock_data_dir / "test.jsonl"
        with open(test_path, 'w') as f:
            for item in test_data:
                f.write(json.dumps(item) + '\n')

        # Use the recipe with local files instead of HF
        from warpdata.api.recipes import RecipeContext
        from warpdata.engine.duck import get_engine
        from warpdata.recipes.gsm8k import gsm8k

        work_dir = tmp_path / "work"
        work_dir.mkdir()

        ctx = RecipeContext(
            dataset_id="warpdata://math/gsm8k-test",
            work_dir=work_dir,
        )

        # Monkey-patch download to return local files
        original_download = ctx.download
        def mock_download(url):
            if "train.jsonl" in url:
                return train_path
            elif "test.jsonl" in url:
                return test_path
            return original_download(url)
        ctx.download = mock_download

        # Run recipe
        result = gsm8k(
            ctx,
            repo_id="openai/gsm8k",
            revision="main",
            splits=("train", "test"),
            symbolize=True,
            codebook_m=16
        )

        # Verify result structure
        assert result.main is not None
        assert len(result.main) == 1
        assert result.subdatasets is not None
        assert "steps" in result.subdatasets

        # Load and verify main dataset
        main_rel = ctx.engine.conn.read_parquet(str(result.main[0]))
        main_df = main_rel.df()

        assert len(main_df) == 3  # 2 train + 1 test
        assert "id" in main_df.columns
        assert "split" in main_df.columns
        assert "question" in main_df.columns
        assert "answer" in main_df.columns
        assert "final_answer_text" in main_df.columns
        assert "final_answer_value" in main_df.columns
        assert "n_exprs" in main_df.columns

        # Check final answers
        assert main_df[main_df["id"] == 0]["final_answer_value"].iloc[0] == 18
        assert main_df[main_df["id"] == 1]["final_answer_value"].iloc[0] == 3
        assert main_df[main_df["id"] == 2]["final_answer_value"].iloc[0] == 12

        # Load and verify steps subdataset
        steps_path = result.subdatasets["steps"].files[0]
        steps_rel = ctx.engine.conn.read_parquet(str(steps_path))
        steps_df = steps_rel.df()

        assert len(steps_df) > 0
        assert "id" in steps_df.columns
        assert "split" in steps_df.columns
        assert "step_idx" in steps_df.columns
        assert "expr" in steps_df.columns
        assert "result" in steps_df.columns
        assert "tokens_json" in steps_df.columns
        assert "bits_hex" in steps_df.columns

        # Check that expressions were extracted
        # First problem: 16-3-4=9, 9*2=18
        # Second problem: 2/2=1, 2+1=3
        # Third problem: 24/2=12, 24-12=12
        assert len(steps_df) >= 6

        # Check that symbolization worked (tokens_json should not be null for valid exprs)
        valid_tokens = steps_df["tokens_json"].notna().sum()
        assert valid_tokens > 0

    def test_gsm8k_without_symbolization(self, tmp_path):
        """Test GSM8K recipe with symbolize=False."""
        # Create minimal mock data
        mock_data_dir = tmp_path / "mock_gsm8k"
        mock_data_dir.mkdir()

        train_data = [
            {
                "question": "Test question?",
                "answer": "The answer is 5.\n#### 5"
            }
        ]

        train_path = mock_data_dir / "train.jsonl"
        with open(train_path, 'w') as f:
            for item in train_data:
                f.write(json.dumps(item) + '\n')

        from warpdata.api.recipes import RecipeContext
        from warpdata.engine.duck import get_engine
        from warpdata.recipes.gsm8k import gsm8k

        work_dir = tmp_path / "work"
        work_dir.mkdir()

        ctx = RecipeContext(
            dataset_id="warpdata://math/gsm8k-nosym",
            work_dir=work_dir,
        )

        # Monkey-patch download
        def mock_download(url):
            return train_path
        ctx.download = mock_download

        # Run recipe without symbolization
        result = gsm8k(
            ctx,
            repo_id="openai/gsm8k",
            splits=("train",),
            symbolize=False
        )

        # Verify main dataset exists
        assert result.main is not None
        main_rel = ctx.engine.conn.read_parquet(str(result.main[0]))
        main_df = main_rel.df()
        assert len(main_df) == 1
        assert main_df["final_answer_value"].iloc[0] == 5

    def test_extract_final_answer(self):
        """Test final answer extraction."""
        from warpdata.recipes.gsm8k import _extract_final_answer

        # Test standard format
        text, val = _extract_final_answer("So the answer is\n#### 42")
        assert text == "42"
        assert val == 42

        # Test decimal
        text, val = _extract_final_answer("#### 3.14")
        assert text == "3.14"
        assert val == 3.14

        # Test negative
        text, val = _extract_final_answer("#### -10")
        assert text == "-10"
        assert val == -10

        # Test no match
        text, val = _extract_final_answer("No answer here")
        assert text == ""
        assert val is None

    def test_extract_exprs(self):
        """Test expression extraction from answer text."""
        from warpdata.recipes.gsm8k import _extract_exprs

        answer = """
        Janet sells 16 - 3 - 4 = <<16-3-4=9>>9 duck eggs.
        She makes 9 * 2 = $<<9*2=18>>18.
        #### 18
        """

        exprs = _extract_exprs(answer)
        assert len(exprs) == 2
        assert exprs[0] == ("16-3-4", "9")
        assert exprs[1] == ("9*2", "18")

    def test_extract_exprs_division(self):
        """Test expression extraction with division."""
        from warpdata.recipes.gsm8k import _extract_exprs

        answer = "It takes 2/2=<<2/2=1>>1 bolt of white fiber\n#### 1"

        exprs = _extract_exprs(answer)
        assert len(exprs) == 1
        assert exprs[0] == ("2/2", "1")
