import string
from pathlib import Path

from warpdata.modules import get_module


def _assert_fp(fp: str):
    assert isinstance(fp, str)
    assert len(fp) == 64
    assert all(c in string.hexdigits for c in fp)


def _pick_string_column(tbl):
    import pyarrow as pa
    for name, field in zip(tbl.column_names, tbl.schema):
        try:
            if pa.types.is_string(field.type) or pa.types.is_large_string(field.type):
                return name
        except Exception:
            continue
    return tbl.column_names[0]


def _e2e_for_module(mod_id: str, preferred_col: str | None = None, query: str = "test"):
    mod = get_module(mod_id)

    # Schema
    schema = mod.get_schema()
    assert isinstance(schema, dict)

    # Prepare
    out = mod.prepare(split="e2e")
    assert (out / "materialized.parquet").exists()
    assert (out / "manifest.json").exists()

    # Load
    tbl = mod.load(format="arrow", limit=5)
    assert tbl.num_rows <= 5

    # Choose column to embed
    col = preferred_col or _pick_string_column(tbl)

    # Fingerprint
    _assert_fp(mod.fingerprint())

    # Embeddings: numpy, dimension small
    space = f"e2e-np-{mod_id.split('.')[-1]}"
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

        results = mod.search_embeddings(space=space, query=query, top_k=3)
        assert isinstance(results, list)
        if results:
            rids = [r["rid"] for r in results]
            df = mod.join_results(rids=rids, columns=["rid", col], as_format="pandas")
            assert df is not None
    finally:
        try:
            mod.destroy_embeddings(space=space, delete_files=True)
        except Exception:
            pass


def test_nlp_ag_news():
    _e2e_for_module("warp.dataset.ag_news", preferred_col="text", query="World news")


def test_nlp_imdb():
    _e2e_for_module("warp.dataset.imdb", preferred_col="text", query="great movie")


def test_nlp_openhermes():
    # conversations is nested; use source/category string columns
    _e2e_for_module("warp.dataset.openhermes", preferred_col="source", query="gpt")


def test_nlp_truthfulqa():
    _e2e_for_module("warp.dataset.truthfulqa", preferred_col="question", query="What is")


def test_nlp_yelp_polarity():
    _e2e_for_module("warp.dataset.yelp_polarity", preferred_col="text", query="good")


def test_eval_mmlu():
    _e2e_for_module("warp.dataset.mmlu", preferred_col="question", query="physics")

