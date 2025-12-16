"""
PyTorch integration for warpdata.

Provides DDP-aware IterableDataset for seamless distributed training.
Automatically handles sharding across GPUs and DataLoader workers.
"""
import torch
import torch.distributed as dist
from torch.utils.data import IterableDataset, get_worker_info
from typing import Iterator, List, Optional, Dict, Any

from .api.streaming import stream_batch_dicts


class WarpDataset(IterableDataset):
    """
    A DDP-aware PyTorch IterableDataset backed by warpdata streaming.

    Automatically handles:
    1. Distributed Data Parallel (DDP) sharding (splitting files across GPUs)
    2. DataLoader worker sharding (splitting files across CPU workers)
    3. Infinite looping (optional) for epoch-based training

    The global sharding formula is:
        global_world_size = ddp_world_size * num_workers
        global_rank = (ddp_rank * num_workers) + worker_id

    This ensures every worker on every GPU gets a unique subset of files.

    Example:
        >>> from warpdata.pytorch import WarpDataset
        >>> from torch.utils.data import DataLoader
        >>>
        >>> # Dataset automatically detects DDP/worker context
        >>> ds = WarpDataset("warpdata://crypto/binance-klines-um-1h")
        >>>
        >>> # Works with multi-worker DataLoader
        >>> dl = DataLoader(ds, batch_size=64, num_workers=4)
        >>>
        >>> for batch in dl:
        ...     # Train on batch
        ...     pass
    """

    def __init__(
        self,
        dataset_id: str,
        columns: Optional[List[str]] = None,
        batch_size: int = 10000,
        infinite: bool = False,
    ):
        """
        Initialize WarpDataset.

        Args:
            dataset_id: Warpdata dataset ID (e.g., 'warpdata://crypto/binance-klines-um-1h'
                        or shorthand 'crypto/binance-klines-um-1h')
            columns: Specific columns to load (projection pushdown for speed).
                     If None, loads all columns.
            batch_size: Number of rows per Arrow batch read from storage.
                        This is NOT the training batch size (that's in DataLoader).
            infinite: If True, loop over data indefinitely for epoch-based training.
        """
        self.dataset_id = dataset_id
        self.columns = columns
        self.batch_size = batch_size
        self.infinite = infinite

    def _get_shard_info(self) -> Dict[str, int]:
        """
        Calculate global rank and world size accounting for DDP + DataLoader workers.

        Returns:
            dict with keys: rank, world_size, ddp_rank, worker_id
        """
        # 1. Determine DDP status
        if dist.is_available() and dist.is_initialized():
            ddp_rank = dist.get_rank()
            ddp_world_size = dist.get_world_size()
        else:
            ddp_rank = 0
            ddp_world_size = 1

        # 2. Determine DataLoader Worker status
        worker_info = get_worker_info()
        if worker_info is not None:
            worker_id = worker_info.id
            num_workers = worker_info.num_workers
        else:
            worker_id = 0
            num_workers = 1

        # 3. Calculate Global Sharding
        # This treats every worker on every GPU as a unique consumer
        global_world_size = ddp_world_size * num_workers
        global_rank = (ddp_rank * num_workers) + worker_id

        return {
            "rank": global_rank,
            "world_size": global_world_size,
            "ddp_rank": ddp_rank,
            "worker_id": worker_id,
        }

    def __iter__(self) -> Iterator[Dict[str, Any]]:
        """
        Iterate over samples from the dataset.

        Yields individual samples (dict per row), not batches.
        The DataLoader's collate_fn handles batching.
        """
        shard_info = self._get_shard_info()

        def data_stream():
            """Inner generator that yields individual samples from batches."""
            streamer = stream_batch_dicts(
                self.dataset_id,
                columns=self.columns,
                batch_size=self.batch_size,
                shard=(shard_info["rank"], shard_info["world_size"]),
            )

            for batch_dict in streamer:
                # Unpack columnar batch {'col': [v1, v2, ...]} into rows
                keys = list(batch_dict.keys())
                if not keys:
                    continue

                length = len(batch_dict[keys[0]])

                for i in range(length):
                    yield {k: batch_dict[k][i] for k in keys}

        if self.infinite:
            while True:
                yield from data_stream()
        else:
            yield from data_stream()
