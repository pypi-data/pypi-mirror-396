import string
from pathlib import Path

from warpdata.modules import get_module


def _assert_fp(fp: str):
    assert isinstance(fp, str) and len(fp) == 64 and all(c in string.hexdigits for c in fp)


def _pick_string_col(tbl, fallback: str | None = None):
    import pyarrow as pa
    if fallback and fallback in tbl.column_names:
        return fallback
    for name, field in zip(tbl.column_names, tbl.schema):
        try:
            if pa.types.is_string(field.type) or pa.types.is_large_string(field.type):
                return name
        except Exception:
            continue
    return tbl.column_names[0]


def _e2e_mod(mod_id: str, prefer: str | None, query: str):
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
    col = _pick_string_col(tbl, prefer)

    # Fingerprint
    _assert_fp(mod.fingerprint())

    # Embeddings
    space = f"e2e-np-{mod_id.split('.')[-1]}"
    try:
        emb_path = mod.add_embeddings(
            space=space,
            provider="numpy",
            source={"columns": [col]},
            dimension=8,
        )
        assert Path(emb_path).exists()
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


def test_arxiv_papers_module():
    # Prefer abstract or title if present
    _e2e_mod("warp.dataset.arxiv_papers", prefer="abstract", query="neural")


def test_code_mbpp_module():
    _e2e_mod("warp.dataset.mbpp", prefer="text", query="function")

