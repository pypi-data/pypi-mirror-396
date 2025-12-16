"""
Tests for PyTorch DDP integration (warpdata.pytorch).

TDD: These tests are written BEFORE the implementation.
"""
import pytest
from unittest.mock import patch, MagicMock
from typing import Iterator, Dict, Any


class TestWarpDatasetShardCalculation:
    """Test shard calculation logic for DDP + DataLoader workers."""

    def test_no_ddp_no_workers_returns_rank_0_world_1(self):
        """Without DDP or workers, should use rank=0, world_size=1."""
        from warpdata.pytorch import WarpDataset

        ds = WarpDataset("warpdata://test/dataset")

        # Mock: DDP not initialized
        with patch('warpdata.pytorch.dist.is_available', return_value=True), \
             patch('warpdata.pytorch.dist.is_initialized', return_value=False), \
             patch('warpdata.pytorch.get_worker_info', return_value=None):

            shard_info = ds._get_shard_info()

            assert shard_info['rank'] == 0
            assert shard_info['world_size'] == 1
            assert shard_info['ddp_rank'] == 0
            assert shard_info['worker_id'] == 0

    def test_ddp_only_uses_ddp_rank(self):
        """With DDP but no workers, should use DDP rank directly."""
        from warpdata.pytorch import WarpDataset

        ds = WarpDataset("warpdata://test/dataset")

        # Mock: DDP initialized with rank=2, world_size=4
        with patch('warpdata.pytorch.dist.is_available', return_value=True), \
             patch('warpdata.pytorch.dist.is_initialized', return_value=True), \
             patch('warpdata.pytorch.dist.get_rank', return_value=2), \
             patch('warpdata.pytorch.dist.get_world_size', return_value=4), \
             patch('warpdata.pytorch.get_worker_info', return_value=None):

            shard_info = ds._get_shard_info()

            assert shard_info['rank'] == 2
            assert shard_info['world_size'] == 4
            assert shard_info['ddp_rank'] == 2
            assert shard_info['worker_id'] == 0

    def test_workers_only_uses_worker_id(self):
        """With workers but no DDP, should use worker ID."""
        from warpdata.pytorch import WarpDataset

        ds = WarpDataset("warpdata://test/dataset")

        # Mock worker info
        worker_info = MagicMock()
        worker_info.id = 1
        worker_info.num_workers = 4

        with patch('warpdata.pytorch.dist.is_available', return_value=False), \
             patch('warpdata.pytorch.get_worker_info', return_value=worker_info):

            shard_info = ds._get_shard_info()

            assert shard_info['rank'] == 1
            assert shard_info['world_size'] == 4
            assert shard_info['ddp_rank'] == 0
            assert shard_info['worker_id'] == 1

    def test_ddp_plus_workers_calculates_global_rank(self):
        """With both DDP and workers, global_rank = ddp_rank * num_workers + worker_id."""
        from warpdata.pytorch import WarpDataset

        ds = WarpDataset("warpdata://test/dataset")

        # Mock: DDP rank=1, world_size=2, worker_id=2, num_workers=4
        # Global: rank = 1*4 + 2 = 6, world_size = 2*4 = 8
        worker_info = MagicMock()
        worker_info.id = 2
        worker_info.num_workers = 4

        with patch('warpdata.pytorch.dist.is_available', return_value=True), \
             patch('warpdata.pytorch.dist.is_initialized', return_value=True), \
             patch('warpdata.pytorch.dist.get_rank', return_value=1), \
             patch('warpdata.pytorch.dist.get_world_size', return_value=2), \
             patch('warpdata.pytorch.get_worker_info', return_value=worker_info):

            shard_info = ds._get_shard_info()

            assert shard_info['rank'] == 6  # 1*4 + 2
            assert shard_info['world_size'] == 8  # 2*4
            assert shard_info['ddp_rank'] == 1
            assert shard_info['worker_id'] == 2

    def test_8_gpu_4_workers_each_calculates_correctly(self):
        """Realistic scenario: 8 GPUs with 4 workers each = 32 total consumers."""
        from warpdata.pytorch import WarpDataset

        ds = WarpDataset("warpdata://test/dataset")

        # GPU 5, worker 3: rank = 5*4 + 3 = 23, world = 8*4 = 32
        worker_info = MagicMock()
        worker_info.id = 3
        worker_info.num_workers = 4

        with patch('warpdata.pytorch.dist.is_available', return_value=True), \
             patch('warpdata.pytorch.dist.is_initialized', return_value=True), \
             patch('warpdata.pytorch.dist.get_rank', return_value=5), \
             patch('warpdata.pytorch.dist.get_world_size', return_value=8), \
             patch('warpdata.pytorch.get_worker_info', return_value=worker_info):

            shard_info = ds._get_shard_info()

            assert shard_info['rank'] == 23
            assert shard_info['world_size'] == 32


class TestWarpDatasetIteration:
    """Test dataset iteration with mocked streaming backend."""

    @pytest.fixture
    def mock_stream_batch_dicts(self):
        """Mock the stream_batch_dicts function to return test data."""
        def _mock(dataset_id, columns=None, batch_size=10000, shard=None, limit=None):
            # Return 3 batches of 2 rows each
            for i in range(3):
                yield {
                    'id': [i*2, i*2+1],
                    'value': [100+i*2, 100+i*2+1],
                }
        return _mock

    def test_yields_individual_samples_from_batches(self, mock_stream_batch_dicts):
        """Should unpack batch dicts into individual sample dicts."""
        from warpdata.pytorch import WarpDataset

        ds = WarpDataset("warpdata://test/dataset", batch_size=2)

        with patch('warpdata.pytorch.stream_batch_dicts', mock_stream_batch_dicts), \
             patch('warpdata.pytorch.dist.is_available', return_value=False), \
             patch('warpdata.pytorch.get_worker_info', return_value=None):

            samples = list(ds)

            # 3 batches * 2 rows = 6 samples
            assert len(samples) == 6

            # Check first sample
            assert samples[0] == {'id': 0, 'value': 100}
            # Check last sample
            assert samples[5] == {'id': 5, 'value': 105}

    def test_passes_shard_to_stream(self, mock_stream_batch_dicts):
        """Should pass calculated shard info to stream_batch_dicts."""
        from warpdata.pytorch import WarpDataset

        ds = WarpDataset("warpdata://test/dataset")

        captured_shard = None

        def capture_shard(dataset_id, columns=None, batch_size=10000, shard=None, limit=None):
            nonlocal captured_shard
            captured_shard = shard
            yield {'id': [1], 'value': [100]}

        with patch('warpdata.pytorch.stream_batch_dicts', capture_shard), \
             patch('warpdata.pytorch.dist.is_available', return_value=True), \
             patch('warpdata.pytorch.dist.is_initialized', return_value=True), \
             patch('warpdata.pytorch.dist.get_rank', return_value=3), \
             patch('warpdata.pytorch.dist.get_world_size', return_value=8), \
             patch('warpdata.pytorch.get_worker_info', return_value=None):

            list(ds)  # Consume iterator

            assert captured_shard == (3, 8)

    def test_passes_columns_to_stream(self, mock_stream_batch_dicts):
        """Should pass columns parameter to stream_batch_dicts."""
        from warpdata.pytorch import WarpDataset

        ds = WarpDataset("warpdata://test/dataset", columns=['id', 'value'])

        captured_columns = None

        def capture_columns(dataset_id, columns=None, batch_size=10000, shard=None, limit=None):
            nonlocal captured_columns
            captured_columns = columns
            yield {'id': [1], 'value': [100]}

        with patch('warpdata.pytorch.stream_batch_dicts', capture_columns), \
             patch('warpdata.pytorch.dist.is_available', return_value=False), \
             patch('warpdata.pytorch.get_worker_info', return_value=None):

            list(ds)

            assert captured_columns == ['id', 'value']


class TestWarpDatasetInfiniteMode:
    """Test infinite looping for epoch-based training."""

    def test_infinite_loops_forever(self):
        """With infinite=True, should loop over data indefinitely."""
        from warpdata.pytorch import WarpDataset

        ds = WarpDataset("warpdata://test/dataset", infinite=True)

        call_count = 0

        def mock_stream(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            yield {'id': [1], 'value': [100]}

        with patch('warpdata.pytorch.stream_batch_dicts', mock_stream), \
             patch('warpdata.pytorch.dist.is_available', return_value=False), \
             patch('warpdata.pytorch.get_worker_info', return_value=None):

            iterator = iter(ds)

            # Consume 10 samples (should loop multiple times)
            for _ in range(10):
                next(iterator)

            # Stream should have been called multiple times
            assert call_count == 10  # Each yield gives 1 sample, so 10 calls

    def test_non_infinite_stops_after_data_exhausted(self):
        """With infinite=False (default), should stop after one pass."""
        from warpdata.pytorch import WarpDataset

        ds = WarpDataset("warpdata://test/dataset", infinite=False)

        def mock_stream(*args, **kwargs):
            yield {'id': [1, 2], 'value': [100, 200]}
            yield {'id': [3], 'value': [300]}

        with patch('warpdata.pytorch.stream_batch_dicts', mock_stream), \
             patch('warpdata.pytorch.dist.is_available', return_value=False), \
             patch('warpdata.pytorch.get_worker_info', return_value=None):

            samples = list(ds)

            # Should have exactly 3 samples, then stop
            assert len(samples) == 3


class TestWarpDatasetIsIterableDataset:
    """Verify WarpDataset is a proper PyTorch IterableDataset."""

    def test_inherits_from_iterable_dataset(self):
        """Should inherit from torch.utils.data.IterableDataset."""
        from warpdata.pytorch import WarpDataset
        from torch.utils.data import IterableDataset

        assert issubclass(WarpDataset, IterableDataset)

    def test_is_iterable(self):
        """Should be iterable (implement __iter__)."""
        from warpdata.pytorch import WarpDataset

        ds = WarpDataset("warpdata://test/dataset")

        # Should have __iter__ method
        assert hasattr(ds, '__iter__')
        assert callable(getattr(ds, '__iter__'))


class TestWarpDatasetInitialization:
    """Test dataset initialization and parameter storage."""

    def test_stores_dataset_id(self):
        """Should store dataset_id parameter."""
        from warpdata.pytorch import WarpDataset

        ds = WarpDataset("warpdata://crypto/btc-klines")

        assert ds.dataset_id == "warpdata://crypto/btc-klines"

    def test_stores_columns(self):
        """Should store columns parameter."""
        from warpdata.pytorch import WarpDataset

        ds = WarpDataset("warpdata://test/ds", columns=['a', 'b'])

        assert ds.columns == ['a', 'b']

    def test_stores_batch_size_with_default(self):
        """Should store batch_size with default of 10000."""
        from warpdata.pytorch import WarpDataset

        ds = WarpDataset("warpdata://test/ds")
        assert ds.batch_size == 10000

        ds2 = WarpDataset("warpdata://test/ds", batch_size=5000)
        assert ds2.batch_size == 5000

    def test_stores_infinite_with_default_false(self):
        """Should store infinite with default of False."""
        from warpdata.pytorch import WarpDataset

        ds = WarpDataset("warpdata://test/ds")
        assert ds.infinite is False

        ds2 = WarpDataset("warpdata://test/ds", infinite=True)
        assert ds2.infinite is True
