import io
import zipfile
from pathlib import Path
from unittest.mock import patch

import pandas as pd

from scripts.download_binance_vision import (
    _months_range,
    build_vision_urls,
    download_urls,
    curate_funding_rate,
    curate_klines,
)


def make_zip_csv(name: str, df: pd.DataFrame) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        inner = io.StringIO()
        df.to_csv(inner, index=False)
        zf.writestr(name, inner.getvalue())
    return buf.getvalue()


def test_months_range_inclusive():
    months = _months_range("2024-01", "2024-03")
    assert months == [("2024","01"),("2024","02"),("2024","03")]


def test_build_urls_funding_um():
    urls = build_vision_urls(asset="um", data_type="fundingRate", symbols=["BTCUSDT"], months=[("2024","01")])
    assert urls[0].endswith("/data/futures/um/monthly/fundingRate/BTCUSDT/BTCUSDT-fundingRate-2024-01.zip")


def test_download_and_curate_funding(tmp_path, monkeypatch):
    # Mock urlopen to return a zip with one CSV row
    df = pd.DataFrame({"symbol":["BTCUSDT"],"fundingRate":[0.001],"fundingTime":[1704067200000]})
    payload = make_zip_csv("BTCUSDT-fundingRate-2024-01.csv", df)

    def fake_urlopen(req, timeout=30.0):
        class Resp:
            def __enter__(self):
                return io.BytesIO(payload)
            def __exit__(self, exc_type, exc, tb):
                return False
            def read(self):
                return payload
        return Resp()

    with patch("urllib.request.urlopen", fake_urlopen):
        files = download_urls([
            "https://data.binance.vision/data/futures/um/monthly/fundingRate/BTCUSDT/BTCUSDT-fundingRate-2024-01.zip"
        ], tmp_path)
        assert len(files) == 1

    # Curate
    out_ds = "warpdata://crypto/test-funding-vision"
    out_file = curate_funding_rate(tmp_path, out_ds)
    assert Path(out_file).exists()
    df2 = pd.read_parquet(out_file)
    assert set(["symbol","funding_rate","funding_time"]).issubset(df2.columns)
    assert (df2["symbol"] == "BTCUSDT").any()


def test_curate_klines_from_zip(tmp_path):
    # Create a zip with a minimal kline CSV (no header)
    df = pd.DataFrame([[1704067200000, 100, 110, 90, 105, 1.23, 1704070800000, 130.0, 10, 0.5, 60.0]],
                      columns=list(range(11)))
    payload = make_zip_csv("BTCUSDT-1h-2024-01.csv", df)
    z = tmp_path/"BTCUSDT-1h-2024-01.zip"
    z.write_bytes(payload)

    out_ds = "warpdata://crypto/test-klines-vision"
    out_file = curate_klines(tmp_path, interval="1h", out_dataset=out_ds)
    assert Path(out_file).exists()
    df2 = pd.read_parquet(out_file)
    assert set(["open_time","open","high","low","close","symbol","interval"]).issubset(df2.columns)
    assert (df2["symbol"] == "BTCUSDT").any()

