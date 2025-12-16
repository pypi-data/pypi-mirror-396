import json
import logging
import os
import pickle

NUM_OBJECTS_KEY = "num_objects"
NUM_BATCHES_PER_SUBDIR_KEY = "num_batches_per_subdir"
BLOB_FILENAME_PREFIX_KEY = "blob_filename_prefix"


class BlobDataset:
    def __init__(self, obj_dir, metadata_file="metadata.json", obj_count=None, prefix=None):
        assert isinstance(obj_dir, list) and len(obj_dir) == 1, "obj_dir should be a list of length 1"
        self.obj_dir = obj_dir[0]
        assert os.path.exists(self.obj_dir), f"Object directory {self.obj_dir} not found"
        if os.path.exists(os.path.join(self.obj_dir, metadata_file)):
            with open(os.path.join(self.obj_dir, metadata_file), "r") as f:
                metadata = json.load(f)
                self.obj_count = metadata[NUM_OBJECTS_KEY]
                self.num_batches_per_subdir = metadata.get(NUM_BATCHES_PER_SUBDIR_KEY, None)
                self.prefix = metadata.get(BLOB_FILENAME_PREFIX_KEY, None)
        else:
            assert obj_count is not None, "obj_count is required if metadata file is not provided"
            self.obj_count = obj_count
            self.num_batches_per_subdir = None  # no subdirs
            self.prefix = prefix
        logging.info(
            f"BlobDataset initialized with obj_count: {self.obj_count}, "
            f"num_batches_per_subdir: {self.num_batches_per_subdir}, prefix: {self.prefix}"
        )

    def __len__(self):
        return self.obj_count

    def get_obj_filename(self, idx):
        prefix = self.prefix + "_" if self.prefix else ""
        subdir_idx = idx // self.num_batches_per_subdir if self.num_batches_per_subdir else ""
        # TODO: support other file formats
        return os.path.join(self.obj_dir, f"{subdir_idx}", f"{prefix}{idx}.pkl")

    def __getitem__(self, idx):
        filename = self.get_obj_filename(idx)
        assert os.path.exists(filename), f"Object file {filename} not found"
        assert 0 <= idx < self.obj_count, f"Object index {idx} out of range, expected range is [0, {self.obj_count})"
        # TODO: support other file formats
        with open(filename, "rb") as f:
            return pickle.loads(f.read())

    def get_sub_lengths(self, level="file"):
        return [self.obj_count]
