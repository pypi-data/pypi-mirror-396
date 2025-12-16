import string
from pathlib import Path

from warpdata.modules import get_module


def _assert_fp(fp: str):
    assert isinstance(fp, str)
    assert len(fp) == 64
    assert all(c in string.hexdigits for c in fp)


def _pick_str(tbl, prefer: str | None = None):
    import pyarrow as pa
    if prefer and prefer in tbl.column_names:
        return prefer
    for name, field in zip(tbl.column_names, tbl.schema):
        try:
            if pa.types.is_string(field.type) or pa.types.is_large_string(field.type):
                return name
        except Exception:
            continue
    return tbl.column_names[0]


def _e2e(mod_id: str, prefer: str | None, query: str):
    mod = get_module(mod_id)

    schema = mod.get_schema()
    assert isinstance(schema, dict)

    out = mod.prepare(split="e2e")
    assert (out / "materialized.parquet").exists()
    assert (out / "manifest.json").exists()

    tbl = mod.load(format="arrow", limit=5)
    col = _pick_str(tbl, prefer)

    _assert_fp(mod.fingerprint())

    space = f"e2e-np-{mod_id.split('.')[-1]}"
    try:
        p = mod.add_embeddings(
            space=space,
            provider="numpy",
            source={"columns": [col]},
            dimension=8,
        )
        assert Path(p).exists()
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


def test_arc_arcagi():
    _e2e("warp.dataset.arcagi", prefer="task_id", query="0")


def test_arc_arcagi2():
    _e2e("warp.dataset.arcagi2", prefer="task_id", query="0")

