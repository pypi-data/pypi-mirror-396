import string
from pathlib import Path

import warpdata as wd


def _assert_fingerprint(fp: str):
    assert isinstance(fp, str)
    assert len(fp) == 64
    assert all(c in string.hexdigits for c in fp)


def _pick_any_string_column(table):
    import pyarrow as pa
    for name, field in zip(table.column_names, table.schema):
        try:
            if pa.types.is_string(field.type) or pa.types.is_large_string(field.type):
                return name
        except Exception:
            continue
    # Fallback to first column
    return table.column_names[0]


def test_coco_modules_end_to_end(tmp_path):
    from warpdata.modules import get_module

    for mod_id in [
        "warp.dataset.coco",
        "warp.dataset.coco_train",
        "warp.dataset.coco_val",
    ]:
        mod = get_module(mod_id)

        # Schema
        schema = mod.get_schema()
        assert isinstance(schema, dict)

        # Prepare and check lockfile
        out = mod.prepare(split="e2e", cache_dir=tmp_path)
        assert (out / "materialized.parquet").exists()
        assert (out / "manifest.json").exists()

        # Load a small slice
        tbl = mod.load(format="arrow", limit=5)
        assert tbl.num_rows <= 5

        # Expect 'split' column and at least one string col we can embed
        assert "split" in tbl.column_names
        col = _pick_any_string_column(tbl)

        # Fingerprint
        _assert_fingerprint(mod.fingerprint())

        # Embeddings round-trip (numpy provider)
        space = f"e2e-np-coco-{mod_id.split('.')[-1]}"
        try:
            emb_path = mod.add_embeddings(
                space=space,
                provider="numpy",
                source={"columns": [col]},
                dimension=8,
            )
            assert Path(emb_path).exists()

            spaces = mod.list_embeddings()
            assert any(s["space_name"] == space for s in spaces)

            results = mod.search_embeddings(space=space, query="a photo", top_k=3)
            assert isinstance(results, list)
            if results:
                rids = [r["rid"] for r in results]
                df = mod.join_results(rids=rids, columns=["rid", col], as_format="pandas")
                assert not df.empty
                emb_tbl = mod.get_embeddings(space=space, rids=rids, as_format="arrow")
                assert set(["rid", "vector"]).issubset(set(emb_tbl.column_names))
        finally:
            try:
                mod.destroy_embeddings(space=space, delete_files=True)
            except Exception:
                pass


def test_imagenet_modules_end_to_end(tmp_path):
    from warpdata.modules import get_module

    for mod_id in [
        "warp.dataset.imagenet_1k",
        "warp.dataset.imagenet_1k_sample",
    ]:
        mod = get_module(mod_id)

        # Schema
        schema = mod.get_schema()
        assert isinstance(schema, dict)

        # Prepare
        out = mod.prepare(split="e2e", cache_dir=tmp_path)
        assert (out / "materialized.parquet").exists()
        assert (out / "manifest.json").exists()

        # Load
        tbl = mod.load(format="arrow", limit=5)
        assert tbl.num_rows <= 5
        # Expect label + split columns
        assert "split" in tbl.column_names
        # For embeddings, use a string column (split)
        col = "split"

        # Fingerprint
        _assert_fingerprint(mod.fingerprint())

        # Embeddings
        space = f"e2e-np-imnet-{mod_id.split('.')[-1]}"
        try:
            emb_path = mod.add_embeddings(
                space=space,
                provider="numpy",
                source={"columns": [col]},
                dimension=8,
            )
            assert Path(emb_path).exists()
            spaces = mod.list_embeddings()
            assert any(s["space_name"] == space for s in spaces)

            results = mod.search_embeddings(space=space, query="validation", top_k=3)
            assert isinstance(results, list)
            if results:
                rids = [r["rid"] for r in results]
                df = mod.join_results(rids=rids, columns=["rid", col], as_format="pandas")
                assert not df.empty
                emb_tbl = mod.get_embeddings(space=space, rids=rids, as_format="arrow")
                assert set(["rid", "vector"]).issubset(set(emb_tbl.column_names))
        finally:
            try:
                mod.destroy_embeddings(space=space, delete_files=True)
            except Exception:
                pass

