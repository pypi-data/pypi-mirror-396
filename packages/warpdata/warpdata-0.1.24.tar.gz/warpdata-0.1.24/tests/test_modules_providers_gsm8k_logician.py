import os
import random
import string
from pathlib import Path

import pytest

import warpdata as wd


def _rand_suffix(n: int = 6) -> str:
    return "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(n))


class TestDatasetModules:
    def test_forge_cli_available(self):
        # Sanity check that forge CLI is on PATH
        import subprocess
        out = subprocess.run(["forge", "--help"], capture_output=True, text=True)
        assert out.returncode == 0
        assert "Forge tools CLI" in out.stdout

    def test_gsm8k_module_end_to_end(self, tmp_path):
        from warpdata.modules.providers.gsm8k import GSM8KModule

        mod = GSM8KModule()
        assert mod.dataset_uri == "warpdata://math/gsm8k"

        # Schema
        schema = mod.get_schema()
        assert isinstance(schema, dict) and len(schema) > 0
        # Expect core columns
        assert "id" in schema
        assert "question" in schema

        # Prepare and load small slice
        mat_dir = mod.prepare()
        assert mat_dir.is_dir()
        assert (mat_dir / "materialized.parquet").exists()
        assert (mat_dir / "manifest.json").exists()

        tbl = mod.load(format="arrow", limit=5)
        assert tbl.num_rows <= 5
        assert "question" in tbl.column_names

        # Fingerprint
        fp = mod.fingerprint()
        assert isinstance(fp, str) and len(fp) == 64 and all(c in string.hexdigits for c in fp)

        # Embeddings: numpy (fast, offline) with small dimension
        space = f"test-np-{_rand_suffix()}"
        try:
            emb_path = mod.add_embeddings(
                space=space,
                provider="numpy",
                source={"columns": ["question"]},
                dimension=8,
                batch_size=256,
            )
            assert Path(emb_path).exists()

            spaces = mod.list_embeddings()
            assert any(s["space_name"] == space for s in spaces)

            # Search and join
            results = mod.search_embeddings(space=space, query="addition and subtraction", top_k=3)
            assert isinstance(results, list)
            if results:
                rids = [r["rid"] for r in results]
                joined = mod.join_results(rids=rids, columns=["rid", "question"], as_format="pandas")
                assert not joined.empty

                # get_embeddings
                emb_tbl = mod.get_embeddings(space=space, rids=rids, as_format="arrow")
                assert set(["rid", "vector"]).issubset(set(emb_tbl.column_names))
        finally:
            # Clean up the test embedding space
            try:
                mod.destroy_embeddings(space=space, delete_files=True)
            except Exception:
                pass

    def test_logician_module_end_to_end(self, tmp_path):
        from warpdata.modules.providers.logician import LogicianModule

        mod = LogicianModule()
        assert mod.dataset_uri == "warpdata://logic/logician"

        # Schema
        schema = mod.get_schema()
        assert isinstance(schema, dict) and len(schema) > 0
        assert "id" in schema
        assert "instruction" in schema

        # Prepare and load small slice
        mat_dir = mod.prepare()
        assert mat_dir.is_dir()
        assert (mat_dir / "materialized.parquet").exists()

        tbl = mod.load(format="arrow", limit=5)
        assert tbl.num_rows <= 5
        assert "instruction" in tbl.column_names

        # Fingerprint
        fp = mod.fingerprint()
        assert isinstance(fp, str) and len(fp) == 64 and all(c in string.hexdigits for c in fp)

        # Embeddings: numpy with small dimension to keep it light
        space = f"test-np-{_rand_suffix()}"
        try:
            emb_path = mod.add_embeddings(
                space=space,
                provider="numpy",
                source={"columns": ["instruction"]},
                dimension=8,
                batch_size=256,
            )
            assert Path(emb_path).exists()

            spaces = mod.list_embeddings()
            assert any(s["space_name"] == space for s in spaces)

            results = mod.search_embeddings(space=space, query="forall x P(x) -> Q(x)", top_k=3)
            assert isinstance(results, list)
            if results:
                rids = [r["rid"] for r in results]
                joined = mod.join_results(rids=rids, columns=["rid", "instruction"], as_format="pandas")
                assert not joined.empty

                emb_tbl = mod.get_embeddings(space=space, rids=rids, as_format="arrow")
                assert set(["rid", "vector"]).issubset(set(emb_tbl.column_names))
        finally:
            try:
                mod.destroy_embeddings(space=space, delete_files=True)
            except Exception:
                pass

    def _pick_any_column(self, table):
        # Prefer string-like columns for embeddings; else fallback to first column
        import pyarrow as pa
        for name, field in zip(table.column_names, table.schema):
            try:
                if pa.types.is_string(field.type) or pa.types.is_large_string(field.type):
                    return name
            except Exception:
                continue
        return table.column_names[0]

    def test_gsm8k_symbolized_module_end_to_end(self):
        from warpdata.modules.providers.gsm8k_symbolized import GSM8KSymbolizedModule

        mod = GSM8KSymbolizedModule()
        assert mod.dataset_uri == "warpdata://math/gsm8k_symbolized"

        schema = mod.get_schema()
        assert isinstance(schema, dict) and len(schema) > 0
        assert "id" in schema

        mat_dir = mod.prepare()
        assert (mat_dir / "materialized.parquet").exists()

        tbl = mod.load(format="arrow", limit=5)
        assert tbl.num_rows <= 5

        fp = mod.fingerprint()
        import string as _s
        assert isinstance(fp, str) and len(fp) == 64 and all(c in _s.hexdigits for c in fp)

        space = f"test-np-{_rand_suffix()}"
        try:
            col = self._pick_any_column(tbl)
            emb_path = mod.add_embeddings(
                space=space,
                provider="numpy",
                source={"columns": [col]},
                dimension=8,
            )
            assert Path(emb_path).exists()

            spaces = mod.list_embeddings()
            assert any(s["space_name"] == space for s in spaces)

            results = mod.search_embeddings(space=space, query="test", top_k=3)
            assert isinstance(results, list)
            if results:
                rids = [r["rid"] for r in results]
                joined = mod.join_results(rids=rids, columns=["rid", col], as_format="pandas")
                assert not joined.empty

                emb_tbl = mod.get_embeddings(space=space, rids=rids, as_format="arrow")
                assert set(["rid", "vector"]).issubset(set(emb_tbl.column_names))
        finally:
            try:
                mod.destroy_embeddings(space=space, delete_files=True)
            except Exception:
                pass

    def test_gsm8k_symbolized_steps_module_end_to_end(self):
        from warpdata.modules.providers.gsm8k_symbolized_steps import GSM8KSymbolizedStepsModule

        mod = GSM8KSymbolizedStepsModule()
        assert mod.dataset_uri == "warpdata://math/gsm8k_symbolized-steps"

        schema = mod.get_schema()
        assert isinstance(schema, dict) and len(schema) > 0
        assert "id" in schema

        mat_dir = mod.prepare()
        assert (mat_dir / "materialized.parquet").exists()

        tbl = mod.load(format="arrow", limit=5)
        assert tbl.num_rows <= 5

        fp = mod.fingerprint()
        import string as _s
        assert isinstance(fp, str) and len(fp) == 64 and all(c in _s.hexdigits for c in fp)

        space = f"test-np-{_rand_suffix()}"
        try:
            col = self._pick_any_column(tbl)
            emb_path = mod.add_embeddings(
                space=space,
                provider="numpy",
                source={"columns": [col]},
                dimension=8,
            )
            assert Path(emb_path).exists()

            spaces = mod.list_embeddings()
            assert any(s["space_name"] == space for s in spaces)

            results = mod.search_embeddings(space=space, query="test", top_k=3)
            assert isinstance(results, list)
            if results:
                rids = [r["rid"] for r in results]
                joined = mod.join_results(rids=rids, columns=["rid", col], as_format="pandas")
                assert not joined.empty

                emb_tbl = mod.get_embeddings(space=space, rids=rids, as_format="arrow")
                assert set(["rid", "vector"]).issubset(set(emb_tbl.column_names))
        finally:
            try:
                mod.destroy_embeddings(space=space, delete_files=True)
            except Exception:
                pass
