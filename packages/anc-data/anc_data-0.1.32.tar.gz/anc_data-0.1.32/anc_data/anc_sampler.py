import bisect
import copy
import heapq
import logging
import math
import os
import pickle
import random
import time
from enum import Enum

import numpy as np
import torch
from torch.utils.data.distributed import DistributedSampler

from anc_data.utils.data_states import EndOfIteration


class RankShardingMode(Enum):
    CHUNK = "chunk"
    ROUND_ROBIN = "round_robin"


class WorkerShardingMode(Enum):
    CHUNK = "chunk"
    ROUND_ROBIN = "round_robin"


class CustomizedRange:
    def __init__(self, start, end, seed=0):
        self.start = start
        self.end = end
        self._seed = seed
        self._random = None

    def __len__(self):
        return self.end - self.start

    def reset_random_generator(self):
        self._random = np.random.default_rng(self._seed)

    def clone(self, clone_times=1):
        return CustomizedRange(self.start, self.end, self._seed + clone_times)

    def to_list(self, shuffle=False):
        if self._random is None:
            self.reset_random_generator()
        lst = np.arange(
            self.start,
            self.end,
            dtype=np.uint64 if self.end > np.iinfo(np.uint32).max else np.uint32,
        )
        if shuffle:
            self._random.shuffle(lst)
        return lst

    def split_to_lists(self, chunk_sizes, shuffle=False):
        lst = self.to_list(shuffle)
        chunks = []
        assert sum(chunk_sizes) == self.end - self.start
        accu_length = 0
        for chunk_size in chunk_sizes:
            chunks.append(lst[accu_length : accu_length + chunk_size])
            accu_length += chunk_size
        return chunks

    def slice(self, start, length):
        assert start + self.start + length <= self.end
        return CustomizedRange(start + self.start, start + self.start + length, self._seed)


class RangesHolder:
    def __init__(self, list_of_ranges, expand_size_limit=20):
        self.list_of_ranges = list_of_ranges
        self.accu_lengths = self.create_accu_length(list_of_ranges)
        self.length = sum(len(r) for r in list_of_ranges)
        self.expanded = {}
        self.expand_size_limit = expand_size_limit
        self.expanded_heap = []  # (time, range_idx)
        self.i = 0

    def __len__(self):
        return self.length

    def create_accu_length(self, list_of_ranges):
        accu_length = 0
        accu_lengths = []
        for rng in list_of_ranges:
            accu_lengths.append(accu_length)
            accu_length += len(rng)
        accu_lengths.append(accu_length)
        return accu_lengths

    def _get_start_idx(self, start):
        idx = bisect.bisect_right(self.accu_lengths, start) - 1
        assert 0 <= idx < len(self.accu_lengths)
        return idx

    def get_start_and_end_ranges(self, start, length):
        start_range_id, start_range_offset = 0, 0
        n = len(self.list_of_ranges)
        end = start + length
        end_range_id = n - 1
        end_range_offset = len(self.list_of_ranges[end_range_id])
        if self.accu_lengths[self.i] <= start < self.accu_lengths[self.i + 1]:
            start_range_id = self.i
        else:
            start_range_id = self._get_start_idx(start)
        start_range_offset = start - self.accu_lengths[start_range_id]
        accu_length = self.accu_lengths[start_range_id]
        for i in range(start_range_id, n):
            accu_length += len(self.list_of_ranges[i])
            if end < accu_length:
                end_range_id = i
                end_range_offset = end - (accu_length - len(self.list_of_ranges[i]))
                break
        self.i = end_range_id
        return start_range_id, start_range_offset, end_range_id, end_range_offset

    def slice(self, start, length):
        start_range_id, start_range_offset, end_range_id, end_range_offset = self.get_start_and_end_ranges(
            start, length
        )
        res = []
        for i in range(start_range_id, end_range_id + 1):
            if i == start_range_id:
                if start_range_id == end_range_id:
                    res.append(
                        self.list_of_ranges[i].slice(
                            start_range_offset,
                            end_range_offset - start_range_offset,
                        )
                    )
                else:
                    res.append(
                        self.list_of_ranges[i].slice(
                            start_range_offset,
                            len(self.list_of_ranges[i]) - start_range_offset,
                        )
                    )
            elif i == end_range_id:
                res.append(self.list_of_ranges[i].slice(0, end_range_offset))
            else:
                res.append(self.list_of_ranges[i])
        target = RangesHolder(res, self.expand_size_limit)
        assert target.length == length
        return target

    def combine(self, other):
        for i in other.list_of_ranges:
            self.list_of_ranges.append(i)
        self.length = sum(len(r) for r in self.list_of_ranges)
        # Recompute accumulated lengths after modifying ranges
        self.accu_lengths = self.create_accu_length(self.list_of_ranges)

    def to_list(self, shuffle=False):
        arrays = []
        for rng in self.list_of_ranges:
            arrays.append(rng.to_list(shuffle))
        if not arrays:
            return np.array([], dtype=np.uint32)
        return np.concatenate(arrays)

    def expand(self, range_idx, shuffle=False):
        if range_idx in self.expanded:
            return self.expanded[range_idx]
        if self.expand_size_limit > 0:
            self.expanded[range_idx] = self.list_of_ranges[range_idx].to_list(shuffle)
            if len(self.expanded_heap) < self.expand_size_limit:
                heapq.heappush(self.expanded_heap, (time.time(), range_idx))
            else:
                _, range_idx_to_shrink = heapq.heappushpop(self.expanded_heap, (time.time(), range_idx))
                assert range_idx_to_shrink != range_idx
                self.shrink(range_idx_to_shrink)
            assert len(self.expanded) == len(
                self.expanded_heap
            ), f"len(self.expanded) {len(self.expanded)} != len(self.expanded_heap) {len(self.expanded_heap)}"
            return self.expanded[range_idx]

        self.expanded[range_idx] = self.list_of_ranges[range_idx].to_list(shuffle)
        return self.expanded[range_idx]

    def shrink(self, range_idx):
        assert range_idx in self.expanded, f"range idx {range_idx} is not found in self.expanded"
        self.expanded.pop(range_idx)
        self.list_of_ranges[range_idx]._random = None

    def get_value_from(self, start, end, shuffle=False):
        start_range_id, start_range_offset, end_range_id, end_range_offset = self.get_start_and_end_ranges(
            start, end - start
        )
        arrays = []
        for range_idx in range(start_range_id, end_range_id + 1):
            indices = self.expand(range_idx, shuffle)
            if range_idx == start_range_id:
                if range_idx == end_range_id:
                    assert start_range_offset + end - start <= len(self.list_of_ranges[range_idx])
                    arrays.append(indices[start_range_offset : start_range_offset + end - start])
                else:
                    arrays.append(indices[start_range_offset:])
            elif range_idx == end_range_id:
                arrays.append(indices[:end_range_offset])
            else:
                arrays.append(indices)
        if not arrays:
            return np.array([], dtype=np.uint32)
        if len(arrays) == 1:
            return arrays[0]
        return np.concatenate(arrays)

    def random_reset(self, idx, offset=1):
        self.expanded = {}
        self.expanded_heap = []
        self.list_of_ranges = self.list_of_ranges[idx:] + self.list_of_ranges[:idx]
        self.accu_lengths = self.create_accu_length(self.list_of_ranges)
        for range in self.list_of_ranges:
            # reset each range's seed by moving it forward by offset
            range._seed += offset
            range.reset_random_generator()


class AncSampler(DistributedSampler):
    r"""
    A batch sampler controls the data sharding, data shuffling and data loading order with proper indices

    The data sharding is chunk based. For example, to shard a dataset with 10 elements into 2 splits,
    the result data index would be [[0,1,2,3,4],[5,6,7,8,9]] instead of [[0,2,4,6,8],[1,3,5,7,9]]

    Args:
        dataset: dataset from which to load the data.
        batch_size (int): how many samples per batch to load.
        world (int, optional): data parallel world size (default: ``1``).
        rank (int, optional): data parallel rank of current process (default: ``0``).
        num_workers (int): how many subprocesses to use for data
            loading. ``0`` means that the data will be loaded in the main process.
        shuffle (bool, optional): set to ``True`` to have the data reshuffled
            at every epoch (default: ``False``).
        drop_last (bool, optional): set to ``True`` to drop the last incomplete batch,
            if the dataset size is not divisible by the batch size. If ``False`` and
            the size of dataset is not divisible by the batch size, then the last batch
            will be smaller. (default: ``False``).
        seed (int, optional): seed for randomness (default: ``0``).
        resume_step (int, optional): the step to resume from,
            the previous steps will be skipped (default: ``0``).
        repeat (bool, optional): set to ``True`` to repeat the indices when gone through
            all the data. If ``False`` than StopIteration will be raised when all data
            is consumed (default: ``False``).
    """

    def __init__(
        self,
        dataset,
        batch_size,
        world=1,
        rank=0,
        num_workers=1,
        shuffle=False,
        drop_last=False,
        seed=0,
        resume_step=0,
        repeat=False,
        global_shuffle=False,
        ratio=1.0,
        chunk_granularity=-1,
        mem_save_mode=False,
        max_samples=None,
        range_expand_size_limit=20,
        ds_idx=0,
        indices_state_dir=None,
        rank_sharding_mode=RankShardingMode.CHUNK,
        worker_sharding_mode=WorkerShardingMode.CHUNK,
        load_indices_state_from_file=False,
        dump_indices_state_to_file=False,
    ):
        if hasattr(dataset, "get_sub_lengths"):
            self.sub_lengths = dataset.get_sub_lengths()
        else:
            assert isinstance(dataset, list)
            self.sub_lengths = dataset
        self.batch_size = batch_size
        self.num_workers = num_workers
        self.resume_step = resume_step
        self.step = resume_step
        self.seed = seed
        self._np_random = np.random.default_rng(seed)
        self.last_iter_epoch = -1
        self.indices = None
        self.repeat = repeat
        self.inner_epoch_count = 0
        self.global_shuffle = global_shuffle
        self.num_replicas = world
        self.rank = rank
        self.epoch = 0
        self.drop_last = drop_last
        self.chunk_granularity = chunk_granularity
        self.mem_save_mode = mem_save_mode
        self.max_samples = max_samples
        if rank_sharding_mode == RankShardingMode.ROUND_ROBIN or worker_sharding_mode == WorkerShardingMode.ROUND_ROBIN:
            assert not self.mem_save_mode, "mem save mode is not supported for round robin sharding mode"
        self.rank_sharding_mode = rank_sharding_mode
        self.worker_sharding_mode = worker_sharding_mode
        self.range_expand_size_limit = range_expand_size_limit
        if load_indices_state_from_file or dump_indices_state_to_file:
            assert indices_state_dir is not None
        self.load_indices_state_from_file = load_indices_state_from_file
        self.dump_indices_state_to_file = dump_indices_state_to_file
        self.inner_epoch_counts = [0] * self.num_workers
        self.start_idxs = [0] * self.num_workers
        if self.mem_save_mode:
            assert self.chunk_granularity == -1, "chunk_granularity is not supported when mem_save_mode is True"
        self.ds_length = 0
        for item in self.sub_lengths:
            if isinstance(item, list):
                self.ds_length += sum(item)
            else:
                self.ds_length += item
        assert 0 <= ratio <= 1
        self.ratio = ratio
        self._compute_num_samples(self.ds_length)
        if self.total_size > np.iinfo(np.uint64).max:
            raise ValueError(
                f"Total dataset size ({self.total_size}) exceeds uint64 maximum "
                f"({np.iinfo(np.uint64).max}). Consider using fewer samples, "
                f"reducing ratios, or modifying the code to use larger types."
            )
        logging.info(f"num_samples: {self.num_samples}, total_size: {self.total_size}")

        self.shuffle = shuffle
        if getattr(self, "dataset", None) is not None:
            self.dataset = None
        self.padding_indices = set()
        self.start_idx = None
        self.end_idx = None
        self.ds_idx = ds_idx
        self.indices_state_dir = indices_state_dir
        self.curr_epoch_index_offset = 0
        if indices_state_dir is not None:
            os.makedirs(indices_state_dir, exist_ok=True)

    def _compute_num_samples(self, ds_length):
        ds_length = math.ceil(ds_length * self.ratio)
        if self.drop_last and ds_length % self.num_replicas != 0:
            self.num_samples = math.ceil((ds_length - self.num_replicas) / self.num_replicas)
        else:
            self.num_samples = math.ceil(ds_length / self.num_replicas)
        if self.max_samples is not None:
            self.num_samples = min(self.num_samples, self.max_samples)
        self.total_size = self.num_samples * self.num_replicas

    def _split_into_chunks(self, indices):
        num_chunks = int(math.ceil(len(indices) / self.chunk_granularity))
        return [
            indices[i * self.chunk_granularity : min((i + 1) * self.chunk_granularity, len(indices))]
            for i in range(num_chunks)
        ]

    def _get_indices(self, sub_lengths, accu_length=0, return_sub_indices=False):
        if self.mem_save_mode:
            assert return_sub_indices is True
        indices_list = []
        for i, item in enumerate(sub_lengths):
            if not self.mem_save_mode:
                sub_indices = np.arange(
                    accu_length,
                    accu_length + item,
                    dtype=(np.uint64 if accu_length + item > np.iinfo(np.uint32).max else np.uint32),
                )
                if self.shuffle:
                    self._np_random.shuffle(sub_indices)
                if self.chunk_granularity > 0:
                    indices_list += self._split_into_chunks(sub_indices)
                else:
                    indices_list.append(sub_indices)
            else:
                indices_list.append(CustomizedRange(accu_length, accu_length + item))
            accu_length += item

        if self.shuffle:
            self._np_random.shuffle(indices_list)
        if return_sub_indices:
            return indices_list
        if not indices_list:
            return np.array([], dtype=np.uint32)
        indices = np.concatenate(indices_list)
        return indices

    def _compute_worker_indices_ranges(self):
        # calculate num batches per worker
        num_batches = (self.num_samples + self.batch_size - 1) // self.batch_size
        last_batch_size = self.num_samples - (num_batches - 1) * self.batch_size
        num_batches_per_worker = num_batches // self.num_workers
        remain = num_batches - self.num_workers * num_batches_per_worker
        num_batches_per_each_worker = [num_batches_per_worker + 1] * remain + [num_batches_per_worker] * (
            self.num_workers - remain
        )
        assert sum(num_batches_per_each_worker) == num_batches
        last_batch_worker_id = self.num_workers - 1 if remain == 0 else remain - 1

        num_samples_per_worker = []
        for i in range(self.num_workers):
            if i == last_batch_worker_id:
                current_num_samples = (num_batches_per_each_worker[i] - 1) * self.batch_size + last_batch_size
            else:
                current_num_samples = num_batches_per_each_worker[i] * self.batch_size
            num_samples_per_worker.append(current_num_samples)
        assert sum(num_samples_per_worker) == self.num_samples

        start_idx_per_worker = [0] * self.num_workers
        if self.worker_sharding_mode == WorkerShardingMode.CHUNK:
            for i in range(1, self.num_workers):
                start_idx_per_worker[i] = start_idx_per_worker[i - 1] + num_samples_per_worker[i - 1]
        elif self.worker_sharding_mode == WorkerShardingMode.ROUND_ROBIN:
            start_idx_per_worker = [i for i in range(self.num_workers)]
        return num_samples_per_worker, start_idx_per_worker

    def _get_chunk_sharding_batch_end_idx(self, start_idx):
        return min(start_idx + self.batch_size, self.chunk_sharding_worker_end_idx)

    def yield_worker_indices_for_curr_epoch(self, indices):
        if self.worker_sharding_mode == WorkerShardingMode.CHUNK:
            while self.start_idx < self.chunk_sharding_worker_end_idx:
                self.end_idx = self._get_chunk_sharding_batch_end_idx(self.start_idx)
                is_last_batch = self.end_idx == self.chunk_sharding_worker_end_idx and not self.repeat
                if self.resume_step == 0:
                    if self.mem_save_mode:
                        yield (
                            indices.get_value_from(self.start_idx, self.end_idx, self.shuffle).tolist(),
                            is_last_batch,
                        )
                    else:
                        yield indices[self.start_idx : self.end_idx].tolist(), is_last_batch
                else:
                    self.resume_step -= 1
                self.start_idx = self.end_idx
        elif self.worker_sharding_mode == WorkerShardingMode.ROUND_ROBIN:
            if self.mem_save_mode:
                raise NotImplementedError("Round robin sharding mode is not supported when mem_save_mode is True")
            batch_indices = []
            worker_indices = indices[self.wid :: self.num_workers]
            for pos, index in enumerate(worker_indices):
                batch_indices.append(int(index))
                if len(batch_indices) == self.batch_size:
                    yield batch_indices, pos == len(worker_indices) - 1 and not self.repeat
                    batch_indices = []
            if batch_indices:
                # if repeat: not the last batch. otherwise it is the last batch
                yield batch_indices, not self.repeat
        else:
            raise ValueError(f"Invalid worker sharding mode: {self.worker_sharding_mode}")

    def _calc_next_batch_start_end_idx(self):
        num_samples_per_worker, self.start_idx_per_worker = self._compute_worker_indices_ranges()
        if self.start_idx is None:
            self.start_idx = self.start_idx_per_worker[self.wid]
            self.try_to_dump_indices(self.indices)
        if self.worker_sharding_mode == WorkerShardingMode.CHUNK:
            self.chunk_sharding_worker_end_idx = self.start_idx_per_worker[self.wid] + num_samples_per_worker[self.wid]
            self.end_idx = self._get_chunk_sharding_batch_end_idx(self.start_idx)

    def _yield_worker_indices(self, indices):
        while True:
            yield from self.yield_worker_indices_for_curr_epoch(indices)
            if not self.repeat:
                break

            self.inner_epoch_count += 1
            if self.curr_epoch_index_offset != 0:
                indices = self._get_all_dataset_indices()
                self.indices = self.shard_indices_for_rank(indices)
                self.curr_epoch_index_offset = 0
            self.start_idx = self.start_idx_per_worker[self.wid]
            if self.worker_sharding_mode == WorkerShardingMode.CHUNK:
                self.end_idx = self._get_chunk_sharding_batch_end_idx(self.start_idx)
            if self.global_shuffle:
                assert self.mem_save_mode is False
                self._np_random.shuffle(indices)
            elif self.shuffle:
                if self.mem_save_mode:
                    shift_offset = self._np_random.integers(0, len(indices.list_of_ranges))
                    indices.random_reset(shift_offset)
                else:
                    shift_offset = self._np_random.integers(0, len(indices))
                    indices = np.concatenate((indices[shift_offset:], indices[:shift_offset]))
            self.try_to_dump_indices(indices)

    def get_indices_filepath(self):
        return f"ds-{self.ds_idx}_wid-{self.wid}_epoch-{self.inner_epoch_count}.pkl"

    def try_to_dump_indices(self, indices):
        if not self.dump_indices_state_to_file:
            return
        filepath = os.path.join(self.indices_state_dir, f"rank-{self.rank}")
        os.makedirs(filepath, exist_ok=True)
        filepath = os.path.join(filepath, self.get_indices_filepath())
        logging.info(f"dumping sampler indices to {filepath}")
        with open(filepath, "wb") as f:
            f.write(pickle.dumps((indices, self._np_random)))

    def load_indices_and_rg_state(self):
        filepath = os.path.join(self.indices_state_dir, f"rank-{self.rank}", self.get_indices_filepath())
        logging.info(f"loading sampler indices from {filepath}")
        with open(filepath, "rb") as f:
            return pickle.loads(f.read())

    def set_indices_and_rg_state(self):
        assert self.load_indices_state_from_file and self.indices_state_dir is not None
        filepath = os.path.join(self.indices_state_dir, f"rank-{self.rank}", self.get_indices_filepath())
        if not os.path.exists(filepath):
            return
        self.indices, self._np_random = self.load_indices_and_rg_state()
        # no need to replay from the beginning
        self.resume_step = 0

    def is_padding(self, ds_idx, index):
        return index in self.padding_indices

    def try_to_load_indices_state_from_file(self):
        if self.load_indices_state_from_file:
            if self.worker_sharding_mode != WorkerShardingMode.CHUNK:
                # TODO: make round robin sharding mode use start_idx, epoch_count, and indices loaded from files
                raise NotImplementedError("Only worker sharding mode CHUNK is supported for loading indices from file")
            self.inner_epoch_count = self.inner_epoch_counts[self.wid]
            self.start_idx = self.start_idxs[self.wid]
            self.set_indices_and_rg_state()

    def _get_all_dataset_indices(self):
        if isinstance(self.sub_lengths[0], list):
            sub_indices_list = []
            accumulate_length = 0
            for i, item in enumerate(self.sub_lengths):
                sub_indices = self._get_indices(item, accumulate_length, True)
                accumulate_length += sum(item)
                sub_indices_list += sub_indices
            if self.shuffle:
                self._np_random.shuffle(sub_indices_list)
            if not self.mem_save_mode:
                if not sub_indices_list:
                    indices = np.array([], dtype=np.uint32)
                else:
                    indices = np.concatenate(sub_indices_list)
            else:
                indices = RangesHolder(sub_indices_list, self.range_expand_size_limit)
        else:
            if not self.mem_save_mode:
                indices = self._get_indices(self.sub_lengths)
                if self.global_shuffle:
                    self._np_random.shuffle(indices)
            else:
                # Build a RangesHolder when mem_save_mode=True for flat sub_lengths
                sub_indices_list = self._get_indices(self.sub_lengths, return_sub_indices=True)
                if self.shuffle:
                    self._np_random.shuffle(sub_indices_list)
                indices = RangesHolder(sub_indices_list, self.range_expand_size_limit)
        offset = self.curr_epoch_index_offset % len(indices)
        if self.mem_save_mode:
            return indices.slice(offset, len(indices) - offset)
        return indices[offset:]

    def _iter_init(self):
        worker_info = torch.utils.data.get_worker_info()
        self.wid = worker_info.id if worker_info is not None else 0
        self.try_to_load_indices_state_from_file()
        indices = []
        if self.epoch == self.last_iter_epoch:
            indices = self.indices
        elif self.indices is None:
            self.last_iter_epoch = self.epoch
            indices = self._get_all_dataset_indices()
            self.indices = self.shard_indices_for_rank(indices)

        # calc before yielding to initialize variables before next()
        self._calc_next_batch_start_end_idx()
        return self._yield_worker_indices(self.indices)

    def shard_indices_for_rank(self, indices):
        self._compute_num_samples(len(indices))
        indices = self._add_padding_indices(indices)
        if self.rank_sharding_mode == RankShardingMode.CHUNK:
            if self.mem_save_mode:
                return indices.slice(self.rank * self.num_samples, self.num_samples)
            return indices[self.rank * self.num_samples : (self.rank + 1) * self.num_samples]
        if self.rank_sharding_mode == RankShardingMode.ROUND_ROBIN:
            return indices[self.rank :: self.num_replicas]
        raise ValueError(f"Invalid rank sharding mode: {self.rank_sharding_mode}")

    # TODO: remove padding
    def _add_padding_indices(self, indices):
        # if max_samples is set, may need to truncate indices to total_size
        if self.drop_last or len(indices) >= self.total_size:
            # remove tail of data to make it evenly divisible.
            if self.mem_save_mode:
                indices = indices.slice(0, self.total_size)
            else:
                indices = indices[: self.total_size]
            padding_size = 0  # No padding when truncating
        else:
            # add extra samples to make it evenly divisible
            padding_size = self.total_size - len(indices)
            if padding_size <= len(indices):
                if self.mem_save_mode:
                    indices.combine(indices.slice(0, padding_size))
                else:
                    indices = np.concatenate((indices, indices[:padding_size]))
            else:
                assert (
                    self.mem_save_mode is False
                ), "mem_save_mode is True but padding_size greater than indices length isn't supported for now"
                padding = np.tile(indices, math.ceil(padding_size / len(indices)))[:padding_size]
                indices = np.concatenate((indices, padding))
        assert len(indices) == self.total_size

        # max padding indices len: min(world_size, num_samples), should be small enough
        if padding_size > 0 and len(indices) - padding_size < (self.rank + 1) * self.num_samples:
            start = len(indices) - padding_size
            end = (self.rank + 1) * self.num_samples
            if self.mem_save_mode:
                self.padding_indices = set(indices.slice(start, end - start).to_list().tolist())
            else:
                self.padding_indices = set(indices[start:end])
        return indices

    def __iter__(self):
        # do all initialization before yielding to trigger local variable recycling
        # otherwise they are maintained in all dataloader worker's heap
        # python's variable scope is function based not block based
        indices_generator = self._iter_init()
        return self._generate_indices(indices_generator)

    def _generate_indices(self, indices_generator):
        while True:
            self.step += 1
            indices = next(indices_generator, EndOfIteration)
            if indices is EndOfIteration:
                break
            yield indices

    def set_step(self, step):
        self.resume_step = step
        self.step = step

    def __len__(self):
        # this is a batch sampler, return the number of batches
        if not self.repeat:
            if self.drop_last:
                return self.num_samples // self.batch_size
            return (self.num_samples + self.batch_size - 1) // self.batch_size
        return 1000000000000

    def _set_ckpt(self, state):
        self.__dict__.update(state)
        # reset random generators, their states will be resumed by resume_step
        self._np_random = np.random.default_rng(self.seed)
        self.start_idx = None

    def _get_ckpt(self):
        indices = self.__dict__.pop("indices", None)
        ckpt_state = copy.deepcopy(self.__dict__)
        ckpt_state["resume_step"] = self.step
        ckpt_state["last_iter_epoch"] = -1
        self.__dict__["indices"] = indices
        del ckpt_state["_np_random"]
        return ckpt_state


class AncMultiSourceSampler:
    def __init__(
        self,
        dataset,
        ratios,
        batch_size,
        world=1,
        rank=0,
        num_workers=1,
        shuffle=False,
        drop_last=False,
        seed=0,
        resume_step=0,
        repeat=False,
        global_shuffle=False,
        chunk_granularity=-1,
        mem_save_mode=False,
        sequential=False,
        rank_sharding_mode=RankShardingMode.CHUNK,
        worker_sharding_mode=WorkerShardingMode.CHUNK,
        load_indices_state_from_file=False,
        dump_indices_state_to_file=False,
        indices_state_dir=None,
    ):
        self.ratios = ratios
        self.seed = seed + rank
        if not sequential:
            assert 0.9999 <= sum(ratios) <= 1.0001
        self.sequential = sequential
        if sequential and len(ratios) > 1:
            assert len(ratios) == len(dataset), "ratios must be the same length as dataset when sequential is True"
            logging.info(f"each dataset will repeat according to the ratios: {ratios}")
        self.rank_sharding_mode = rank_sharding_mode
        self.worker_sharding_mode = worker_sharding_mode
        self.samplers = [
            AncSampler(
                dataset.get_sub_lengths(i),
                batch_size,
                world=world,
                rank=rank,
                num_workers=num_workers,
                shuffle=shuffle,
                drop_last=drop_last,
                seed=seed,
                resume_step=resume_step,
                repeat=repeat,
                global_shuffle=global_shuffle,
                chunk_granularity=chunk_granularity,
                mem_save_mode=mem_save_mode,
                ratio=self.ratios[i] if sequential and len(self.ratios) > 1 else 1,
                ds_idx=i,
                rank_sharding_mode=rank_sharding_mode,
                worker_sharding_mode=worker_sharding_mode,
                load_indices_state_from_file=load_indices_state_from_file,
                dump_indices_state_to_file=dump_indices_state_to_file,
                indices_state_dir=indices_state_dir,
            )
            for i in range(len(dataset))
        ]
        self.repeat = repeat
        self.random = random.Random(self.seed)
        if self.repeat and self.sequential:
            # TODO: implement
            raise NotImplementedError("repeat and sequential are not supported together")
        self.cur_iter_idx = 0
        self.rgs = [None] * num_workers

    def __iter__(self):
        worker_info = torch.utils.data.get_worker_info()
        self.wid = worker_info.id if worker_info is not None else 0
        if self.rgs[self.wid] is not None:
            self.random = self.rgs[self.wid]
        iters = [iter(sampler) for sampler in self.samplers]
        iter_list = list(range(len(iters)))
        while True:
            if not self.sequential:
                self.cur_iter_idx = self.random.choices(iter_list, weights=self.ratios)[0]
            cur_iter = iters[self.cur_iter_idx]
            result = next(cur_iter, EndOfIteration)
            if result is EndOfIteration:
                self.cur_iter_idx += 1
                if self.cur_iter_idx >= len(iters):
                    break
                continue
            indices, is_last_batch = result

            yield self.cur_iter_idx, indices, is_last_batch

    def is_padding(self, ds_idx, index):
        return self.samplers[ds_idx].is_padding(ds_idx, index)

    def __len__(self):
        return int(sum(len(sampler) for sampler in self.samplers))

    def _get_ckpt(self):
        state = {}
        samplers_state = [sampler._get_ckpt() for sampler in self.samplers]
        state["samplers"] = samplers_state
        state["random_state"] = self.random.getstate()
        state["cur_iter_idx"] = self.cur_iter_idx
        return state

    def _set_ckpt(self, state):
        assert len(state["samplers"]) == len(self.samplers)
        for i, sampler in enumerate(self.samplers):
            sampler._set_ckpt(state["samplers"][i])
        self.random.setstate(state["random_state"])
        self.cur_iter_idx = state["cur_iter_idx"]
