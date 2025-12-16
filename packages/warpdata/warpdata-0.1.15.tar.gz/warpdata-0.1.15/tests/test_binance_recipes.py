import os
from pathlib import Path
import tempfile
import pandas as pd

from warpdata.api.recipes import RecipeContext


def _dummy_exchange_info():
    return {
        "timezone": "UTC",
        "serverTime": 1694061154503,
        "symbols": [
            {
                "symbol": "BTCUSDT",
                "status": "TRADING",
                "baseAsset": "BTC",
                "quoteAsset": "USDT",
                "isSpotTradingAllowed": True,
            },
            {
                "symbol": "ETHUSDT",
                "status": "TRADING",
                "baseAsset": "ETH",
                "quoteAsset": "USDT",
                "isSpotTradingAllowed": True,
            },
        ]
    }


def _dummy_klines():
    # Two klines for BTCUSDT 1m
    return [
        [1499040000000, "0.01634790", "0.80000000", "0.01575800", "0.01577100", "148976.11427815", 1499040059999, "2434.19055334", 308, "1756.87402397", "28.46694368", "0"],
        [1499040060000, "0.01577100", "0.02000000", "0.01000000", "0.01800000", "1000.00000000", 1499040119999, "15.00000000", 10, "500.00000000", "7.50000000", "0"],
    ]


def test_binance_symbols_recipe_writes_parquet(tmp_path: Path):
    from warpdata.recipes.binance_symbols import binance_symbols

    # Arrange
    ctx = RecipeContext("warpdata://test/binance/symbols", work_dir=tmp_path)

    # Act
    out = binance_symbols(ctx, symbol_status="TRADING", fetch_fn=lambda url, params: _dummy_exchange_info())

    # Assert
    out_file = tmp_path / "binance_symbols.parquet"
    assert out_file.exists(), "Expected Parquet output file to be written"
    df = pd.read_parquet(out_file)
    assert {"symbol", "base_asset", "quote_asset", "status"}.issubset(df.columns)
    assert set(df["symbol"]) == {"BTCUSDT", "ETHUSDT"}


def test_binance_klines_recipe_basic_transform(tmp_path: Path):
    from warpdata.recipes.binance_klines import binance_klines

    # Arrange
    ctx = RecipeContext("warpdata://test/binance/klines", work_dir=tmp_path)

    # Fake fetcher that ignores URL/params and returns dummy klines
    def fake_fetch(url, params):
        return _dummy_klines()

    # Act
    out = binance_klines(
        ctx,
        symbols=["BTCUSDT"],
        interval="1m",
        start_time=1499040000000,
        end_time=1499040120000,
        fetch_fn=fake_fetch,
    )

    # Assert
    out_file = tmp_path / "binance_klines_1m.parquet"
    assert out_file.exists(), "Expected Klines Parquet output file"
    df = pd.read_parquet(out_file)
    required = {"open_time", "close_time", "symbol", "interval", "open", "high", "low", "close", "volume", "trades"}
    assert required.issubset(df.columns)
    assert len(df) == 2
    assert df["symbol"].unique().tolist() == ["BTCUSDT"]


def test_binance_symbol_map_recipe(tmp_path: Path):
    from warpdata.recipes.binance_symbol_map import binance_symbol_map

    # Build a symbols dataframe similar to exchangeInfo
    sym_df = pd.DataFrame([
        {"symbol": "BTCUSDT", "status": "TRADING", "base_asset": "BTC", "quote_asset": "USDT"},
        {"symbol": "ETHUSDT", "status": "TRADING", "base_asset": "ETH", "quote_asset": "USDT"},
        {"symbol": "BNBBTC",  "status": "TRADING", "base_asset": "BNB", "quote_asset": "BTC"},
    ])

    ctx = RecipeContext("warpdata://test/binance/symbol-map", work_dir=tmp_path)

    out = binance_symbol_map(ctx, load_symbols_fn=lambda: sym_df)

    out_file = tmp_path / "binance_symbol_map.parquet"
    assert out_file.exists(), "Expected symbol_map Parquet output"
    df = pd.read_parquet(out_file)
    assert {"symbol", "base_asset", "quote_asset", "coin_id"}.issubset(df.columns)
    m = dict(zip(df["symbol"], df["coin_id"]))
    assert m["BTCUSDT"] == "bitcoin"
    assert m["ETHUSDT"] == "ethereum"
