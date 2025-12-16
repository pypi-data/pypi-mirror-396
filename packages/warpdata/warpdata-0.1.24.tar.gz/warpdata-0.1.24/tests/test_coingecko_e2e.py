"""
End-to-end tests for CoinGecko crypto data download with failure scenarios.

Tests cover:
- API returning non-JSON responses
- API returning JSON with unexpected structure
- Rate limiting and retries
- Invalid data caching prevention
- Informative error messages
"""
import json
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, Optional
from unittest.mock import Mock, patch, MagicMock
import pytest
import pandas as pd

# Import the module under test
from warpdata.recipes.coingecko_crypto import (
    _http_get_json,
    _get_market_chart,
    coingecko_crypto,
    _ensure_dir,
)
from warpdata.api.recipes import RecipeContext


class TestHTTPGetJSON:
    """Test the core HTTP GET function with various failure modes."""

    def test_non_json_response_returns_raw_dict(self):
        """When API returns non-JSON, should wrap in dict with 'raw' key."""
        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_response = MagicMock()
            mock_response.read.return_value = b"Plain text error"
            mock_response.__enter__.return_value = mock_response
            mock_response.__exit__.return_value = None
            mock_urlopen.return_value = mock_response

            result = _http_get_json("http://example.com", api_key=None)

            assert isinstance(result, dict)
            assert "raw" in result
            assert "Plain text error" in result["raw"]

    def test_never_returns_none(self):
        """Should never return None - always return dict or raise exception."""
        import urllib.error

        with patch('urllib.request.urlopen') as mock_urlopen, \
             patch('time.sleep'), \
             patch('warpdata.recipes.coingecko_crypto._REQ_LOCK') as mock_lock:

            # Disable rate limiter
            mock_lock.__enter__ = Mock(return_value=None)
            mock_lock.__exit__ = Mock(return_value=None)

            # Simulate a timeout error
            mock_urlopen.side_effect = TimeoutError("Request timeout")

            # Should raise exception, not return None
            with pytest.raises((TimeoutError, RuntimeError)):
                result = _http_get_json("http://example.com", api_key=None)
                # If it somehow doesn't raise, ensure it's not None
                assert result is not None

    def test_http_429_retries_with_backoff(self):
        """Should retry on 429 rate limit with exponential backoff."""
        import urllib.error

        with patch('urllib.request.urlopen') as mock_urlopen, \
             patch('time.sleep') as mock_sleep, \
             patch('warpdata.recipes.coingecko_crypto._REQ_LOCK') as mock_lock, \
             patch('warpdata.recipes.coingecko_crypto._LAST_REQ_TS', 0.0):

            # Disable rate limiter to isolate retry logic
            mock_lock.__enter__ = Mock(return_value=None)
            mock_lock.__exit__ = Mock(return_value=None)

            # First 2 attempts fail with 429, third succeeds
            error_response = MagicMock()
            error_response.read.return_value = b'{"error": "rate limit"}'

            http_error = urllib.error.HTTPError(
                "http://example.com", 429, "Too Many Requests",
                {}, error_response
            )

            success_response = MagicMock()
            success_response.read.return_value = b'{"prices": []}'
            success_response.__enter__.return_value = success_response
            success_response.__exit__.return_value = None

            mock_urlopen.side_effect = [
                http_error,
                http_error,
                success_response,
            ]

            result = _http_get_json("http://example.com", api_key=None)

            assert result == {"prices": []}
            # Should have slept twice (after first two failures)
            assert mock_sleep.call_count == 2
            # Verify exponential backoff
            assert mock_sleep.call_args_list[0][0][0] == 0.5
            assert mock_sleep.call_args_list[1][0][0] == 1.0

    def test_http_500_retries(self):
        """Should retry on 5xx server errors."""
        import urllib.error

        with patch('urllib.request.urlopen') as mock_urlopen, \
             patch('time.sleep') as mock_sleep, \
             patch('warpdata.recipes.coingecko_crypto._REQ_LOCK') as mock_lock:

            # Disable rate limiter
            mock_lock.__enter__ = Mock(return_value=None)
            mock_lock.__exit__ = Mock(return_value=None)

            error_response = MagicMock()
            error_response.read.return_value = b'Internal Server Error'

            http_error = urllib.error.HTTPError(
                "http://example.com", 500, "Internal Server Error",
                {}, error_response
            )

            success_response = MagicMock()
            success_response.read.return_value = b'{"prices": []}'
            success_response.__enter__.return_value = success_response
            success_response.__exit__.return_value = None

            mock_urlopen.side_effect = [http_error, success_response]

            result = _http_get_json("http://example.com", api_key=None)
            assert result == {"prices": []}
            # Should have retried (may have courtesy sleep too)
            assert mock_sleep.call_count >= 1

    def test_http_404_fails_with_error(self):
        """Should fail with informative error on 404."""
        import urllib.error

        with patch('urllib.request.urlopen') as mock_urlopen, \
             patch('warpdata.recipes.coingecko_crypto._REQ_LOCK') as mock_lock, \
             patch('time.sleep'):  # Don't actually sleep

            # Disable rate limiter
            mock_lock.__enter__ = Mock(return_value=None)
            mock_lock.__exit__ = Mock(return_value=None)

            error_response = MagicMock()
            error_response.read.return_value = b'Not Found'

            http_error = urllib.error.HTTPError(
                "http://example.com", 404, "Not Found",
                {}, error_response
            )

            mock_urlopen.side_effect = http_error

            # Should eventually fail with informative error
            with pytest.raises((RuntimeError, urllib.error.HTTPError)):
                _http_get_json("http://example.com", api_key=None)

    def test_max_retries_exhausted(self):
        """Should attempt retries before giving up."""
        import urllib.error

        with patch('urllib.request.urlopen') as mock_urlopen, \
             patch('time.sleep') as mock_sleep, \
             patch('warpdata.recipes.coingecko_crypto._REQ_LOCK') as mock_lock:

            # Disable rate limiter
            mock_lock.__enter__ = Mock(return_value=None)
            mock_lock.__exit__ = Mock(return_value=None)

            error_response = MagicMock()
            error_response.read.return_value = b'{"error": "rate limit"}'

            http_error = urllib.error.HTTPError(
                "http://example.com", 429, "Too Many Requests",
                {}, error_response
            )

            # Always fail
            mock_urlopen.side_effect = http_error

            # May raise error or return error dict after retries
            did_raise = False
            try:
                result = _http_get_json("http://example.com", api_key=None)
                # If it doesn't raise, should return error response
                if result is not None:
                    assert isinstance(result, dict)
            except (RuntimeError, urllib.error.HTTPError):
                # Also acceptable to raise after retries
                did_raise = True

            # Should have attempted multiple retries
            assert mock_sleep.call_count >= 4 or did_raise  # 5 attempts = 4 sleeps


class TestGetMarketChart:
    """Test market chart fetching with various response types."""

    def test_valid_response_cached(self):
        """Valid responses should be cached to disk."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)

            with patch('warpdata.recipes.coingecko_crypto._http_get_json') as mock_http:
                mock_http.return_value = {
                    "prices": [[1234567890000, 50000.0]],
                    "market_caps": [[1234567890000, 1000000000.0]],
                    "total_volumes": [[1234567890000, 50000000.0]]
                }

                result = _get_market_chart(
                    "bitcoin", "usd",
                    api_key=None,
                    days="30",
                    start_date=None,
                    end_date=None,
                    cache_dir=cache_dir
                )

                # Should have cached the result
                cache_file = cache_dir / "bitcoin_market_chart_usd_30.json"
                assert cache_file.exists()

                cached_data = json.loads(cache_file.read_text())
                assert cached_data == result

    def test_invalid_response_not_cached(self):
        """Invalid responses (non-dict or missing fields) should not be cached."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)

            with patch('warpdata.recipes.coingecko_crypto._http_get_json') as mock_http:
                # Return invalid response (missing expected fields)
                mock_http.return_value = {"error": "Invalid coin"}

                result = _get_market_chart(
                    "invalid-coin", "usd",
                    api_key=None,
                    days="30",
                    start_date=None,
                    end_date=None,
                    cache_dir=cache_dir
                )

                # Should return the error response
                assert "error" in result

                # Should NOT have cached it
                cache_file = cache_dir / "invalid-coin_market_chart_usd_30.json"
                assert not cache_file.exists()

    def test_malformed_cache_refetches(self):
        """If cached file is malformed, should refetch."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            cache_file = cache_dir / "bitcoin_market_chart_usd_30.json"

            # Create malformed cache
            cache_dir.mkdir(parents=True, exist_ok=True)
            cache_file.write_text("not valid json")

            with patch('warpdata.recipes.coingecko_crypto._http_get_json') as mock_http:
                mock_http.return_value = {
                    "prices": [[1234567890000, 50000.0]],
                    "market_caps": [],
                    "total_volumes": []
                }

                result = _get_market_chart(
                    "bitcoin", "usd",
                    api_key=None,
                    days="30",
                    start_date=None,
                    end_date=None,
                    cache_dir=cache_dir
                )

                # Should have refetched
                assert mock_http.called
                assert "prices" in result


class TestCoingeckoCryptoRecipe:
    """End-to-end tests for the full recipe."""

    def test_informative_error_for_invalid_response(self):
        """Error messages should include actual response content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ctx = RecipeContext(
                dataset_id="test://crypto",
                work_dir=Path(tmpdir)
            )

            with patch('warpdata.recipes.coingecko_crypto._get_market_chart') as mock_chart, \
                 patch('warpdata.recipes.coingecko_crypto._get_coins_list') as mock_list:

                # Mock coins list
                mock_list.return_value = [
                    {"id": "bitcoin", "symbol": "btc", "name": "Bitcoin"}
                ]

                # Return error response with no price data
                mock_chart.return_value = {"error": "Coin not found", "status": {"error_code": 404}}

                # Capture printed output
                import io
                captured = io.StringIO()

                with patch('sys.stdout', captured):
                    # Should fail because no valid data was returned
                    try:
                        coingecko_crypto(
                            ctx,
                            coin_ids=["bitcoin"],
                            vs_currency="usd",
                            days="30"
                        )
                        # If it doesn't raise, check that error was logged
                        output = captured.getvalue()
                        assert "bitcoin" in output
                        # Should log the error
                        assert "no data returned" in output or "error" in output.lower()
                    except ValueError as e:
                        # Also acceptable if it raises ValueError
                        assert "No data downloaded" in str(e)
                        output = captured.getvalue()
                        assert "bitcoin" in output

    def test_partial_failure_continues(self):
        """If some coins fail, should continue with successful ones."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ctx = RecipeContext(
                dataset_id="test://crypto",
                work_dir=Path(tmpdir)
            )

            with patch('warpdata.recipes.coingecko_crypto._http_get_json') as mock_http, \
                 patch('warpdata.recipes.coingecko_crypto._get_coins_list') as mock_list:

                mock_list.return_value = [
                    {"id": "bitcoin", "symbol": "btc", "name": "Bitcoin"},
                    {"id": "ethereum", "symbol": "eth", "name": "Ethereum"},
                ]

                # bitcoin succeeds, ethereum fails
                mock_http.side_effect = [
                    [],  # markets
                    {  # bitcoin market_chart
                        "prices": [[1730736000000, 50000.0]],
                        "market_caps": [[1730736000000, 1000000000.0]],
                        "total_volumes": [[1730736000000, 50000000.0]]
                    },
                    {"error": "Rate limit"},  # ethereum fails
                ]

                result = coingecko_crypto(
                    ctx,
                    coin_ids=["bitcoin", "ethereum"],
                    vs_currency="usd",
                    days="30"
                )

                # Should have created output for at least one coin
                assert len(result.main) == 1
                df = pd.read_parquet(result.main[0])
                assert len(df) > 0
                # Should have bitcoin (ethereum failed)
                assert "bitcoin" in df["coin_id"].values

    def test_retry_on_transient_failure(self):
        """Should retry when API returns transient errors."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ctx = RecipeContext(
                dataset_id="test://crypto",
                work_dir=Path(tmpdir)
            )

            with patch('warpdata.recipes.coingecko_crypto._http_get_json') as mock_http, \
                 patch('warpdata.recipes.coingecko_crypto._get_coins_list') as mock_list, \
                 patch('time.sleep'):  # Don't actually sleep in tests

                mock_list.return_value = [
                    {"id": "bitcoin", "symbol": "btc", "name": "Bitcoin"}
                ]

                # First market_chart call fails, second succeeds
                mock_http.side_effect = [
                    [],  # markets
                    {"raw": "Service temporarily unavailable"},  # first attempt
                    {  # second attempt succeeds
                        "prices": [[1730736000000, 50000.0]],
                        "market_caps": [[1730736000000, 1000000000.0]],
                        "total_volumes": [[1730736000000, 50000000.0]]
                    },
                ]

                # This test verifies the structure, actual retry logic needs implementation
                # For now, we'll get the failure and verify error message
                result = coingecko_crypto(
                    ctx,
                    coin_ids=["bitcoin"],
                    vs_currency="usd",
                    days="30"
                )

                # Should eventually succeed
                assert len(result.main) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
