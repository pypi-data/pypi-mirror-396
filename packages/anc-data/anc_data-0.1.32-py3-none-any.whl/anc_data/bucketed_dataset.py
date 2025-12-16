"""
BucketedDataset implementation for handling variable sequence lengths in training.
Please refer to the following link for more details:
https://anuttacon.atlassian.net/wiki/x/VwmBEQ
"""

import copy
import json
import logging
from collections import deque
from typing import Any, Dict, List, Optional, Tuple

from typing_extensions import override

from .anc_dataset import AncDataset, EndOfIteration


class BucketManager:
    """Manages buckets for storing and retrieving data indices based on sequence length."""

    def __init__(self, num_buckets: int, world_size: int, tail_strategy: str = "merge"):
        """
        Initialize BucketManager.

        Args:
            num_buckets: Number of buckets to create
            world_size: Number of distributed ranks
            tail_strategy: Strategy for handling remaining data ('drop', 'merge')
        """
        self.num_buckets = num_buckets
        self.world_size = world_size
        self.tail_strategy = tail_strategy

        # Each bucket is a deque storing index tuples
        self.buckets = [deque() for _ in range(num_buckets)]

    def add_to_bucket(self, bucket_idx: int, index_tuple: Tuple):
        """Add an index tuple to the specified bucket."""
        if 0 <= bucket_idx < self.num_buckets:
            self.buckets[bucket_idx].append(index_tuple)
        else:
            logging.warning(f"Invalid bucket index {bucket_idx}, please check the bucket configuration")
            raise ValueError(f"Invalid bucket index {bucket_idx}")

    def has_full_bucket(self) -> bool:
        """Check if any bucket has enough items for a full batch."""
        for bucket in self.buckets:
            if len(bucket) >= self.world_size:
                return True
        return False

    def pop_batch(self) -> Tuple[Optional[int], Optional[List]]:
        """
        Pop a batch from the first full bucket.

        Returns:
            Tuple of (bucket_idx, batch_indices) or (None, None) if no full bucket
        """
        for bucket_idx, bucket in enumerate(self.buckets):
            if len(bucket) >= self.world_size:
                batch = []
                for _ in range(self.world_size):
                    batch.append(bucket.popleft())  # O(1) operation
                return bucket_idx, batch
        return None, None

    def flush_all(self) -> List[List]:
        """
        Deprecated: use move_to_bucket_0 instead
        Return all remaining data and clear buckets.

        Returns:
            List of remaining indices from each bucket
        """
        remaining = []
        for bucket in self.buckets:
            if bucket:
                remaining.append(list(bucket))
                bucket.clear()
        return remaining

    def move_to_bucket_0(self):
        """Move all items to bucket 0."""
        for i, bucket in enumerate(self.buckets):
            if i > 0 and bucket:
                for _ in range(len(bucket)):
                    curItem = bucket.popleft()
                    self.add_to_bucket(0, curItem)

        logging.debug(f"moved all items to bucket 0 {len(self.buckets[0])} items ")

    @property
    def total_items(self) -> int:
        """Get total number of items across all buckets."""
        return sum(len(b) for b in self.buckets)

    def get_bucket_stats(self) -> Dict[int, int]:
        """Get statistics about bucket sizes."""
        return {i: bucket for i, bucket in enumerate(self.buckets)}

    def get_state(self):
        # Directly save deque objects, pickle can handle them
        return {
            "buckets": copy.deepcopy(self.buckets),
        }

    def set_state(self, state):
        # Restore buckets, ensuring they are deques
        buckets = state["buckets"]
        if buckets and not isinstance(buckets[0], deque):
            # Convert from list to deque if necessary
            self.buckets = [deque(bucket) for bucket in buckets]
        else:
            self.buckets = buckets


class BucketedDataset(AncDataset):
    """
    Dataset wrapper that implements bucketing for variable sequence lengths.
    Inherits from AncDataset and overrides get_generator, adding bucketing logic.
    """

    @override
    def __init__(
        self,
        bucket_config: Dict[str, Any],
        true_world_size: int,
        true_rank: int,
        **kwargs,
    ):
        """
        Initialize BucketedDataset.

        Args:
            bucket_config: Configuration for bucketing including:
                - boundaries: List of sequence length boundaries for buckets
                    each boundry is the exclusive upper bound of the bucket
                    for example:
                        boundaries: [512, 1024, 2048, 4096]
                        length 512 will be in bucket 1
                        length 1024 will be in bucket 2
                        length 1025 will be in bucket 2
                - tail_strategy: How to handle remaining data ('drop', 'merge')
            true_world_size: Actual world size for distributed training
            true_rank: Actual rank of current process
            **kwargs: Arguments to pass to parent AncDataset
        """
        super().__init__(**kwargs)

        # Store true distributed training parameters
        self.world_size = true_world_size
        self.rank = true_rank

        # Bucket configuration
        # for example: 0-512, 512-1024, 1024-5000, 5000-infinity
        self.bucket_boundaries = bucket_config.get("boundaries", [512, 1024, 5000])
        self.tail_strategy = bucket_config.get("tail_strategy", "merge")

        # Initialize bucket manager
        self.bucket_manager = BucketManager(
            num_buckets=len(self.bucket_boundaries) + 1,
            world_size=self.world_size,
            tail_strategy=self.tail_strategy,
        )

        logging.info(f"BucketedDataset initialized with {len(self.bucket_boundaries) + 1} buckets")
        logging.info(f"Bucket boundaries: {self.bucket_boundaries}")
        logging.info(f"World size: {self.world_size}, Rank: {self.rank}")

    @override
    def get_generator(self, sampler_iter, num_workers):
        """
        Override parent's get_generator supporting bucketing logic.
        The back pressure is handled by generator so the bucket size will not grow too large.

        This method:
        1. Receives indices from sampler
        2. Gets sequence lengths without loading data
        3. Buckets indices by length
        4. Yields batches when buckets are available to pop
        5. Handles remaining data at epoch end
        """

        while True:
            # Get indices from sampler
            indices = next(sampler_iter, EndOfIteration)
            if indices is EndOfIteration:
                # Handle remaining data at epoch end
                logging.debug("End of iteration reached, flushing remaining buckets")
                yield from self._flush_remaining_buckets(self.wid)
                break

            # Get lengths without loading actual data
            lengths = self._get_lengths_only([indices])

            # Add indices to appropriate buckets
            for idx_tuple, length in zip([indices], lengths):
                bucket_idx = self._get_bucket_index_for_length(length)
                self.bucket_manager.add_to_bucket(bucket_idx, idx_tuple)

            # Process full buckets
            while self.bucket_manager.has_full_bucket():
                bucket_idx, batch_indices_for_all_ranks = self.bucket_manager.pop_batch()
                cur_rank_indices = []
                for i, batch_indice in enumerate(batch_indices_for_all_ranks):
                    logging.debug(f"batch_indice: {batch_indice}, current rank: {self.rank}, cur idx: {i}")
                    # sample will be assigned to the rank according to the index_position in batch % world_size == rank
                    if i % self.world_size == self.rank:
                        cur_rank_indices.append(batch_indice)

                if cur_rank_indices:
                    # Load and process actual data
                    item_generator = self._getitem(cur_rank_indices[0])
                    while True:
                        result = next(item_generator, EndOfIteration)
                        if result is EndOfIteration:
                            # no more item from bucket available yet, let sampler proceed to the next batch of indices
                            break
                        yield (self.wid, result, False)

                        self.cur_step += 1
                        if self.ckpt_interval is not None and self.cur_step % self.ckpt_interval == 0:
                            if self.state_queues is not None:
                                self.state_queues[self.wid].put(self._get_ckpt())

    def _get_lengths_only(self, indices: List[Tuple]) -> List[int]:
        """
        Get sequence lengths without loading full data.

        Args:
            indices: List of (ds_idx, idx, is_last) tuples

        Returns:
            List of sequence lengths
        """
        lengths = []
        for ds_idx, idx, is_last in indices:
            # keep the original sequence
            length = self._read_length_from_dataset(ds_idx, idx[0])
            lengths.append(length)

        return lengths

    def _read_length_from_dataset(self, ds_idx: int, idx: int) -> int:
        """
        Read sequence length from dataset metadata.

        Args:
            ds_idx: Dataset index
            idx: Sample index

        Returns:
            Sequence length
        """
        try:
            # Try to read the latent_length column
            sample = self.ds[ds_idx][idx]
            # print(f"sample in read length: {sample}")
            if isinstance(sample, dict) and "video_vae_latent_shape" in sample:
                latent_shape = json.loads(sample["video_vae_latent_shape"])
                # seq_len = latent_f * latent_h * latent_w
                seq_len = latent_shape[1] * latent_shape[2] * latent_shape[3]
                return seq_len
            # raise error because the seq data is not available in the sample
            raise ValueError(f"video_vae_latent_shape not found for ds_idx={ds_idx}, idx={idx}, sample: {sample}")

        except Exception as e:
            logging.error(f"Error reading length for ds_idx={ds_idx}, idx={idx}: {e}")
            return 1024  # Default length on error

    def _get_bucket_index_for_length(self, length: int) -> int:
        """
        Determine bucket index based on sequence length.

        Args:
            length: Sequence length

        Returns:
            Bucket index
        """
        for i, boundary in enumerate(self.bucket_boundaries):
            if length < boundary:
                return i
        return len(self.bucket_boundaries)  # Last bucket for longest sequences

    def _flush_remaining_buckets(self):
        """
        Handle remaining data at epoch end based on tail_strategy.

        Yields:
            Remaining batches based on configured strategy
        """

        if self.tail_strategy == "drop":
            # Simply drop remaining data
            total_dropped = sum(len(bucket) for bucket in self.bucket_manager.buckets)
            if total_dropped > 0:
                logging.warning(f"Dropped {total_dropped} samples at epoch end")
            return

        if self.tail_strategy == "merge":
            # Merge all remaining data to idx 0 bucket and form as many complete batches as possible

            self.bucket_manager.move_to_bucket_0()

            logging.warning(f"Merging {len(self.bucket_manager.buckets[0])} remaining samples")

            # Process full buckets
            while self.bucket_manager.has_full_bucket():
                bucket_idx, batch_indices_for_all_ranks = self.bucket_manager.pop_batch()
                cur_rank_indices = []

                for i, batch_indice in enumerate(batch_indices_for_all_ranks):
                    # sample will be assigned to the rank according to the index_position in batch % world_size == rank
                    if i % self.world_size == self.rank:
                        cur_rank_indices.append(batch_indice)

                if cur_rank_indices:
                    # Load and process actual data
                    item_generator = self._getitem(cur_rank_indices[0])
                    while True:
                        result = next(item_generator, EndOfIteration)
                        if result is EndOfIteration:
                            break
                        yield (self.wid, result, False)

                        self.cur_step += 1
                        if self.ckpt_interval is not None and self.cur_step % self.ckpt_interval == 0:
                            if self.state_queues is not None:
                                self.state_queues[self.wid].put(self._get_ckpt())

            # Drop the final incomplete batch
            remaining_count = len(self.bucket_manager.buckets[0])
            if remaining_count > 0:
                logging.info(f"Dropped {remaining_count} samples (not enough for a complete batch)")
        else:
            logging.warning(f"Unknown tail_strategy: {self.tail_strategy}, using 'drop'")
            # Default to drop
            total_dropped = sum(len(bucket) for bucket in self.bucket_manager.buckets)
            if total_dropped > 0:
                logging.warning(f"Dropped {total_dropped} samples at epoch end")

    @override
    def _get_ckpt(self):
        state = super()._get_ckpt()

        state["bucket_manager"] = self.bucket_manager.get_state()

        # for verfication only
        state["bucket_config"] = {
            "boundaries": self.bucket_boundaries,
            "world_size": self.world_size,
        }
        return state

    @override
    def _set_ckpt(self, state):
        try:
            if "bucket_config" in state:
                saved_config = state.pop("bucket_config")

                if (
                    saved_config.get("boundaries") != self.bucket_boundaries
                    or saved_config.get("world_size") != self.world_size
                ):
                    logging.warning(f"Rank {self.rank}: Config mismatch, please check the bucket configuration")
                    raise ValueError("Config mismatch, please check the bucket configuration")
                    state.pop("bucket_manager", None)

            # restore bucket state
            if "bucket_manager" in state:
                bucket_state = state.pop("bucket_manager")
                self.bucket_manager.set_state(bucket_state)

        except Exception as e:
            logging.error(f"Rank {self.rank}: Failed to restore bucket state: {e}")

        super()._set_ckpt(state)
