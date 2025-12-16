import string
from pathlib import Path

from warpdata.modules import get_module
import warpdata as wd


def _assert_fp(fp: str):
    assert isinstance(fp, str) and len(fp) == 64 and all(c in string.hexdigits for c in fp)


def _schema_keys(schema: dict) -> list[str]:
    # schema in manifests is a mapping col->type
    if isinstance(schema, dict):
        return list(schema.keys())
    cols = schema.get("columns") if isinstance(schema, dict) else None
    if isinstance(cols, dict):
        return list(cols.keys())
    if isinstance(cols, list):
        return [c.get("name") if isinstance(c, dict) else str(c) for c in cols]
    return []


def _assert_schema_present(mod, relation_columns: list[str]):
    schema = mod.get_schema()
    keys = [k for k in _schema_keys(schema) if k]
    missing = [k for k in keys if k not in relation_columns]
    assert not missing, f"Missing columns: {missing}"


def test_vision_celeba_attrs_schema_and_embeddings(tmp_path):
    mod = get_module("warp.dataset.celeba_attrs")
    out = mod.prepare(split="e2e", cache_dir=tmp_path)
    assert (out / "materialized.parquet").exists()
    rel = mod.load(format="duckdb")
    _assert_schema_present(mod, rel.columns)
    _assert_fp(mod.fingerprint())
    # embed on a string column (image_path)
    space = "np8"
    try:
        p = mod.add_embeddings(space=space, provider="numpy", source={"columns": ["image_path"]}, dimension=8)
        assert Path(p).exists()
        rs = mod.search_embeddings(space=space, query="img", top_k=3)
        assert isinstance(rs, list)
    finally:
        mod.destroy_embeddings(space=space, delete_files=True)


def test_video_dream1k_schema_and_embeddings(tmp_path):
    mod = get_module("warp.dataset.dream1k")
    out = mod.prepare(split="e2e", cache_dir=tmp_path)
    assert (out / "materialized.parquet").exists()
    rel = mod.load(format="duckdb")
    _assert_schema_present(mod, rel.columns)
    _assert_fp(mod.fingerprint())
    space = "np8"
    try:
        p = mod.add_embeddings(space=space, provider="numpy", source={"columns": ["description"]}, dimension=8)
        assert Path(p).exists()
        rs = mod.search_embeddings(space=space, query="video", top_k=3)
        assert isinstance(rs, list)
    finally:
        mod.destroy_embeddings(space=space, delete_files=True)


def test_video_dream1k_events_schema(tmp_path):
    mod = get_module("warp.dataset.dream1k_events")
    out = mod.prepare(split="e2e", cache_dir=tmp_path)
    assert (out / "materialized.parquet").exists()
    rel = mod.load(format="duckdb")
    _assert_schema_present(mod, rel.columns)
    _assert_fp(mod.fingerprint())


def test_neuro_dmt_brains_schema_and_embeddings(tmp_path):
    mod = get_module("warp.dataset.dmt_brains")
    out = mod.prepare(split="e2e", cache_dir=tmp_path)
    assert (out / "materialized.parquet").exists()
    rel = mod.load(format="duckdb")
    _assert_schema_present(mod, rel.columns)
    _assert_fp(mod.fingerprint())
    space = "np8"
    try:
        p = mod.add_embeddings(space=space, provider="numpy", source={"columns": ["subject_id"]}, dimension=8)
        assert Path(p).exists()
        rs = mod.search_embeddings(space=space, query="S", top_k=3)
        assert isinstance(rs, list)
    finally:
        mod.destroy_embeddings(space=space, delete_files=True)


def _assert_schema_only(mod_id: str, prefer_col: str | None = None):
    mod = get_module(mod_id)
    out = mod.prepare(split="e2e")
    assert (out / "materialized.parquet").exists()
    rel = mod.load(format="duckdb")
    _assert_schema_present(mod, rel.columns)
    _assert_fp(mod.fingerprint())


def test_math_hendrycks_schema():
    _assert_schema_only("warp.dataset.math_hendrycks")


def test_mathvision_schema():
    _assert_schema_only("warp.dataset.mathvision")


def test_mathvista_schema():
    _assert_schema_only("warp.dataset.mathvista")


def test_mathx100k_schema():
    _assert_schema_only("warp.dataset.mathx_100k")


def test_numina_lean_schema():
    _assert_schema_only("warp.dataset.numina_lean")

