import copy
import logging
import multiprocessing as mp
import os
from collections import defaultdict
from collections.abc import Mapping

from torch.utils.data import DataLoader

from anc_data.anc_dataset import BATCH_DATA_KEY, DATASET_IDX, AncDataset
from anc_data.anc_processor import AncProcessor
from anc_data.anc_sampler import AncMultiSourceSampler, RankShardingMode, WorkerShardingMode
from anc_data.bucketed_dataset import BucketedDataset


def fake_collate(x):
    return x


class AncDataLoader:
    r"""
    A wrapper for dataloader, dataset and sampler
    It makes the handling of the data gathering logic in each subprocess easier
    It also helps handle the checkpoint load and resume logic

    Args:
        paths (list of str): files from which to load the data.
        batch_size (int): how many samples per batch to load.
        num_workers (int): how many subprocesses to use for data
            loading. ``0`` means that the data will be loaded in the main process.
        rank (int, optional): data parallel rank of current process (default: ``0``).
        world (int, optional): data parallel world size (default: ``1``).
        processor (Processor, optional): object that defines the data transform and batch transform
            logic (default ``AncProcessor`` instance which just return the input as is for both
            transform and batch transform).
        data_type (str, optional): the type of dataset that the paths represents (default ``parquet``).
        shuffle (bool, optional): set to ``True`` to have the data reshuffled
            at every epoch (default: ``False``).
        drop_last (bool, optional): set to ``True`` to drop the last incomplete batch,
            if the dataset size is not divisible by the batch size. If ``False`` and
            the size of dataset is not divisible by the batch size, then the last batch
            will be smaller. (default: ``False``).
        seed (int, optional): seed for randomness (default: ``0``).
        pin_memory (bool, optional): If ``True``, the data loader will copy Tensors
            into device/CUDA pinned memory before returning them.  If your data elements
            are a custom type, or your :attr:`collate_fn` returns a batch that is a custom type,
            see the example below.
        ds_args (dict, optional): dataset arguments for data loading, such as the columns to load
            for parquet files, etc (default ``{}``).
        repeat (bool, optional): If ``True``, data would be loaded repeatedly
        prefetch_factor (int, optional): the prefetch_factor for torch dataloader
        enable_bucketing (bool, optional): If ``True``, enable bucketing mechanism for variable
            sequence lengths (default: ``False``)
        bucket_config (dict, optional): Configuration for bucketing including boundaries,
            tail_strategy, and preload_lengths
    """

    def __init__(
        self,
        paths,
        batch_size,
        num_workers,
        rank=0,
        world=1,
        processor=AncProcessor(),
        data_type="parquet",
        shuffle=False,
        drop_last=False,
        seed=0,
        pin_memory=True,
        ds_args={},
        repeat=False,
        prefetch_factor=2,
        enable_compose=False,
        global_shuffle=False,
        max_steps=-1,
        enable_logging=True,
        ckpt_interval=None,
        ds_ratios=[1],
        chunk_granularity=-1,
        persistent_workers=False,
        use_spawn=False,
        always_return_first_batch=False,
        skip_read_failures=False,
        gc_freq=None,
        enable_bucketing=False,
        bucket_config=None,
        add_batch_metadata=False,
        sequential_sampler=False,
        sampler_use_mem_save_mode=False,
        sampler_kwargs={},
        compose_buffer_ratio=2.0,
    ):
        # TODO: add support to get rank and world from torch env
        self.paths = paths
        if data_type == "jsonl" and isinstance(self.paths[0], str):
            self.paths = [self.paths]
        self.batch_size = batch_size
        # set self.num_workers to 1 if num_workers=0
        # torch loader will use num_workers and other part will use self.num_workers
        self.num_workers = num_workers if num_workers > 0 else 1
        self.repeat = repeat
        self.add_batch_metadata = add_batch_metadata
        if num_workers > 0:
            if use_spawn:
                ctx = mp.get_context("spawn")
                self.ds_state_queues = [ctx.Queue() for _ in range(num_workers)]
            else:
                self.ds_state_queues = [mp.Queue() for _ in range(num_workers)]
        else:
            self.ds_state_queues = [mp.Queue()]
            prefetch_factor = None
            if ckpt_interval is not None:
                logging.warning("ckpt is not supported for num_worker = 0, will set ckpt_interval to None")
                ckpt_interval = None

        if int(os.getenv("ANC_DISABLE_LOGGING", "0")) == 1:
            enable_logging = False

        ds_ckpt_interval = None
        if ckpt_interval is not None and ckpt_interval % self.num_workers == 0:
            ds_ckpt_interval = ckpt_interval // self.num_workers
        worker_gc_freq = gc_freq // self.num_workers + 1 if gc_freq is not None else None

        # Store original rank and world for bucketing
        self.true_rank = rank
        self.true_world = world
        self.enable_bucketing = enable_bucketing

        # Configure sampler parameters based on bucketing
        sampler_world = world
        sampler_rank = rank
        if enable_bucketing:
            # When bucketing is enabled, make sampler generate all indices for all ranks
            sampler_world = 1
            sampler_rank = 0
            logging.warning(
                f"Bucketing enabled: sampler configured with world=1, rank=0 (true world={world}, true rank={rank})"
            )

            # Raise error if no bucket config is provided
            if bucket_config is None:
                raise ValueError("Bucket is enabled but no bucket configuration provided, please check config")

        # Create dataset based on bucketing configuration
        if enable_bucketing:
            self.dataset = BucketedDataset(
                bucket_config=bucket_config,
                true_world_size=world,
                true_rank=rank,
                filepaths=self.paths,
                processor=processor,
                dataset_type=data_type,
                ds_args=ds_args,
                enable_compose=enable_compose,
                enable_logging=enable_logging,
                state_queues=self.ds_state_queues,
                ckpt_interval=ds_ckpt_interval,
                skip_read_failures=skip_read_failures,
                worker_gc_freq=worker_gc_freq,
            )
        else:
            self.dataset = AncDataset(
                self.paths,
                processor=processor,
                dataset_type=data_type,
                ds_args=ds_args,
                enable_compose=enable_compose,
                enable_logging=enable_logging,
                state_queues=self.ds_state_queues,
                ckpt_interval=ckpt_interval,
                skip_read_failures=skip_read_failures,
                worker_gc_freq=worker_gc_freq,
                rank=rank,
                compose_buffer_ratio=compose_buffer_ratio,
            )

        self.sampler = AncMultiSourceSampler(
            dataset=self.dataset,
            ratios=ds_ratios,
            batch_size=batch_size,
            world=sampler_world,  # Use modified world for bucketing
            rank=sampler_rank,  # Use modified rank for bucketing
            num_workers=self.num_workers,
            shuffle=shuffle,
            seed=seed,
            drop_last=drop_last,
            repeat=repeat,
            global_shuffle=global_shuffle,
            chunk_granularity=chunk_granularity,
            mem_save_mode=sampler_use_mem_save_mode,
            sequential=sequential_sampler,
            **sampler_kwargs,
        )
        self.dataset.set_sampler(self.sampler)
        self.loader = DataLoader(
            self.dataset,
            num_workers=num_workers,
            pin_memory=pin_memory,
            collate_fn=fake_collate,
            prefetch_factor=prefetch_factor,
            persistent_workers=persistent_workers,
            multiprocessing_context=mp.get_context("spawn") if use_spawn else None,
        )
        self.step = 0
        self.rank = rank
        self.world = world
        self.loader_iter = None
        self.buffer = [[] for _ in range(self.num_workers)]
        self.cur_wid = 0
        self.out_of_data_worker = set()
        self.max_steps = max_steps
        self.logging = enable_logging
        self.ckpt_interval = ckpt_interval
        # nemo may call get_checkpoint multiple times for the same step
        self.last_ckpt = {}
        self.always_return_first_batch = always_return_first_batch
        self.first_batch = None
        # with multi val dataloader, we may get _loader_idx as _ds_idx in data, so use a dict instead of a list here
        self.ds_read_counts = defaultdict(int)
        self.samples_read_per_dataset = [{} for _ in range(self.num_workers)]
        self.no_more_data = False
        self.all_ranks_no_more_data = False
        self.first_no_more_data = True

    def __iter__(self):
        logging.debug(f"pid {os.getpid()} rank {self.rank} in iter")
        self.loader_iter = iter(self.loader)
        self.out_of_data_worker = set()
        return self

    def __len__(self):
        if self.max_steps > 0:
            # maybe need to check if max_steps is less than length of sampler, or repeat is set
            return self.max_steps
        return len(self.sampler)

    def _try_advance_wid_to_next_unfinished(self):
        if self.cur_wid is None:
            return False
        for i in range(self.num_workers):
            if self.cur_wid not in self.out_of_data_worker or self.buffer[self.cur_wid]:
                return True
            self.cur_wid = (self.cur_wid + 1) % self.num_workers
        self.cur_wid = None
        return False

    def _empty_buffer(self):
        logging.info(f"All workers stop, try to get data from buffer, buffer size {sum([len(i) for i in self.buffer])}")
        for i in range(self.num_workers):
            if len(self.buffer[i]) > 0:
                data = self.buffer[i].pop()
                return data
        return None

    def _try_getting_next_batch_for_curr_wid(self):
        if self.cur_wid is None:
            assert self.no_more_data, "cur_wid is None but no_more_data is False"
            return None
        for loop_cnt in range(self.num_workers * 1000):
            if self.buffer[self.cur_wid]:
                return self.buffer[self.cur_wid].pop()
            if self.cur_wid in self.out_of_data_worker:
                # no more data will come from cur_wid
                return None

            # pytorch dataloader with default batch_size=1 when not specified
            cur_data_wid, cur_data, is_last_batch = next(self.loader_iter)[0]
            if is_last_batch:
                # curr_data_wid's sampler yielded no more indices
                assert cur_data is None
                self.out_of_data_worker.add(cur_data_wid)
            else:
                self.buffer[cur_data_wid].append(cur_data)

        logging.warning(
            f"{self.rank} Too many loop ({loop_cnt} times) when getting next data"
            f"for worker {self.cur_wid} of step {self.step}"
        )
        return None

    def __next__(self):
        if self.all_ranks_no_more_data:
            raise StopIteration
        if self.always_return_first_batch and self.first_batch is not None:
            return self.first_batch

        batch = None
        for loop_cnt in range(self.num_workers * 1000):
            batch = self._try_getting_next_batch_for_curr_wid()
            if batch is not None:
                # prepare for the next wid in round robin fashion
                self.cur_wid = (self.cur_wid + 1) % self.num_workers
                break
            if not self._try_advance_wid_to_next_unfinished():
                # all buffers are empty and all workers are out of data, mark permanently done for this rank
                self.no_more_data = True
                break
            if loop_cnt > 0 and loop_cnt % 20 == 0:
                logging.warning(
                    f"rank {self.rank} is still getting data from worker {self.cur_wid} of step {self.step}"
                )
        if loop_cnt >= self.num_workers * 1000:
            raise RuntimeError(
                f"Too many loop ({loop_cnt} times) when getting next data for worker {self.cur_wid} of step {self.step}"
            )

        self.step += 1
        if self.no_more_data:
            if self.first_no_more_data:
                logging.info(f"rank {self.rank} has no more data, will keep returning the first batch")
                self.first_no_more_data = False
            return copy.deepcopy(self.first_batch)

        assert batch is not None
        if isinstance(batch, Mapping):
            if DATASET_IDX in batch:
                for idx in batch[DATASET_IDX]:
                    self.ds_read_counts[idx] += 1
            if "samples_read_per_dataset" in batch and "wid" in batch:
                self.samples_read_per_dataset[batch["wid"]] = batch["samples_read_per_dataset"]
            if not self.add_batch_metadata:
                if BATCH_DATA_KEY in batch:
                    batch = batch[BATCH_DATA_KEY]
        if self.first_batch is None:
            self.first_batch = copy.deepcopy(batch)

        return batch

    def get_checkpoint(self):
        if self.step in self.last_ckpt:
            return self.last_ckpt[self.step]
        step_to_del = []
        for i in self.last_ckpt:
            if i < self.step:
                step_to_del.append(i)
        for i in step_to_del:
            del self.last_ckpt[i]
        ds_states = None
        if self.dataset.ckpt_interval is not None:
            ds_states = [self.ds_state_queues[i].get() for i in range(self.num_workers)]
        ckpt = self.__getstate__()
        ckpt["ds_states"] = ds_states
        self.last_ckpt[self.step] = ckpt
        return ckpt

    def set_checkpoint(self, ckpt, recalc_assignments=False):
        if recalc_assignments:
            # recalc_assignments works only for continuous sharding: all used indices in the current epoch are
            # continuous for all ranks and workers. ROUND_ROBIN mode is the only continuous sharding mode for now
            assert (
                self.sampler.rank_sharding_mode == RankShardingMode.ROUND_ROBIN
                and self.sampler.worker_sharding_mode == WorkerShardingMode.ROUND_ROBIN
            ), "recalc_assignments is only supported for round robin sharding mode"
            # Note: actually we can support different samplers/datasets with a mechanism to specify the mapping.
            # Being strict for now.
            assert len(self.dataset.sampler.samplers) == len(
                ckpt["ds_states"][0]["sampler"]["samplers"]
            ), "samplers in the current configuration and the checkpoint must match"
            sum_indices = defaultdict(int)
            for state in ckpt["ds_states"]:
                for idx, sampler in enumerate(state["sampler"]["samplers"]):
                    sum_indices[idx] += sampler["step"] * sampler["batch_size"] * sampler["num_replicas"]
            for idx, s in enumerate(self.dataset.sampler.samplers):
                s.curr_epoch_index_offset = sum_indices[idx]
            # we want to recalc assignments so not inheriting anything from the prev ckpt except step
            self.step = ckpt["step"]
        else:
            self.dataset.set_ds_states(ckpt.pop("ds_states"))
            self.__setstate__(ckpt)

    def __getstate__(self):
        state = {}
        state["paths"] = self.paths
        state["batch_size"] = self.batch_size
        state["num_workers"] = self.num_workers
        state["cur_wid"] = self.cur_wid
        state["out_of_data_worker"] = copy.deepcopy(self.out_of_data_worker)
        state["step"] = self.step
        state["ds_read_counts"] = copy.deepcopy(self.ds_read_counts)
        state["samples_read_per_dataset"] = copy.deepcopy(self.samples_read_per_dataset)
        state["world"] = self.world
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)


if __name__ == "__main__":
    folder = "/mnt/personal/parquet_demo_data"
    fnames = [
        "01_0001.parquet",
        "02_0001.parquet",
        "03_0001.parquet",
        "04_0001.parquet",
        "05_0001.parquet",
        "06_0001.parquet",
        "07_0001.parquet",
    ]
    files = [f"{folder}/{fname}" for fname in fnames]
    loader = AncDataLoader(files, 1024, num_workers=4)
    for data in loader:
        print(len(data))
