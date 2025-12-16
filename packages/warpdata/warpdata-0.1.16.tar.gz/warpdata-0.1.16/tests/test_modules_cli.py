import json
import subprocess
from pathlib import Path


def test_warp_module_schema_json():
    # Ensure CLI returns JSON schema for a known module
    proc = subprocess.run(["warp", "module", "schema", "--id", "warp.dataset.gsm8k", "--json"], capture_output=True, text=True)
    assert proc.returncode == 0
    data = json.loads(proc.stdout)
    assert isinstance(data, dict)


def test_warp_module_fetch(tmp_path):
    # Fetch to a temp cache dir to avoid polluting workspace
    cache_root = tmp_path / "cache"
    cache_root.mkdir()

    proc = subprocess.run([
        "warp", "module", "fetch",
        "--id", "warp.dataset.gsm8k",
        "--split", "cli",
        "--cache-dir", str(cache_root)
    ], capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr

    # Verify output file exists in Forge-friendly layout
    out_dir = cache_root / ".forgelab" / "state" / "datasets" / "warp.dataset.gsm8k" / "1.0.0" / "cli"
    assert (out_dir / "materialized.parquet").exists()
    assert (out_dir / "manifest.json").exists()

