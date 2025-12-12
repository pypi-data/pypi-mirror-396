# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
import sys
import torch
import numpy as np
from typing import Union, Any, Sequence
from torch.utils.data import Dataset, Sampler, RandomSampler, SequentialSampler

try:
    from torch.utils.data.distributed import DistributedSampler
except ImportError:
    DistributedSampler = None

try:
    import horovod.torch as hvd
except ImportError:
    hvd = None

from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.core.shared._diagnostics.contract import Contract

from forecast.distributed import (
    DistributionStrategy,
    HorovodDistributionStrategy,
    SingleProcessDistributionStrategy,
)


logger = logging.getLogger(__name__)


class DistributedHelper:
    """Helper for running a distributed job."""

    horovod_dep_available = hvd is not None
    is_without_hvd = hvd is None or not hvd.is_initialized()

    @classmethod
    def initialize(cls):
        """Do the necessary initialization for a distributed job."""
        cls.horovod_dep_available = hvd is not None
        if not cls.horovod_dep_available:
            logger.info('Horovod import failed.')
        else:
            logger.info('Horovod import succeeded')
            if not hvd.is_initialized():
                logger.info("Initializing horovod.")
                hvd.init()
                cls.is_without_hvd = False
            else:
                logger.info("Horovod already initialized.")

    @classmethod
    def is_master_node(cls) -> bool:
        """Return if the current node is the master node."""
        return cls.is_without_hvd or hvd.rank() == 0

    @classmethod
    def is_local_master_node(cls) -> bool:
        """Return if the current process is the first node on the current machine."""
        return cls.is_without_hvd or hvd.local_rank() == 0

    @classmethod
    def rank(cls) -> int:
        """Return the global rank of the current node."""
        return 0 if cls.is_without_hvd else hvd.rank()

    @classmethod
    def local_rank(cls) -> int:
        """Return the local rank of the current node."""
        return 0 if cls.is_without_hvd else hvd.local_rank()

    @classmethod
    def node_rank(cls) -> int:
        """Return the node rank of the current node."""
        return 0 if cls.is_without_hvd else hvd.rank() // hvd.local_size()

    @classmethod
    def node_count(cls) -> int:
        """Return the number of machines available."""
        return 1 if cls.is_without_hvd else hvd.size() // hvd.local_size()

    @classmethod
    def process_count(cls) -> int:
        """Return the number of processes that horovod has started."""
        return 1 if cls.is_without_hvd else hvd.size()

    @classmethod
    def local_processes_count(cls) -> int:
        """Return the number of nodes on the current machine."""
        return 1 if cls.is_without_hvd else hvd.local_size()

    @classmethod
    def wait_for_all_processes(cls):
        """Waits for all processes to reach this point."""
        if not cls.is_without_hvd:
            # The current installed version of horovod does not support
            # hvd.barrier() yet.
            hvd.allreduce(torch.tensor([0]))

    @classmethod
    def wait_for_all_processes_async(cls, name: str) -> Union[int, None]:
        """
        Waits asynchronously for all processes to reach this point where operation is keyed on the name.

        :param name: A string specifying the name of the operation to synchronize on.
        :type name: str

        :return: A handle to the allreduce operation that can be used with `poll()` or `synchronize()`.
        :rtype: int or None
        """
        if not cls.is_without_hvd:
            return hvd.allreduce_async(torch.tensor([0]), name=name)
        return None

    @classmethod
    def poll(cls, handle: Union[int, None]) -> bool:
        """
        Polls the handle to determine whether underlying asynchronous operation has completed.

        :param handle: A handle returned by an allreduce, allgather, alltoall, broadcast, or
            reducescatter asynchronous operation.
        :type handle: int or None

        :return: A flag indicating whether the operation has completed.
        :rtype: bool
        """
        if not cls.is_without_hvd:
            return hvd.poll(handle)
        return True

    @classmethod
    def broadcast_from_master_to_all(cls, *args: Any) -> Sequence[Any]:
        """Broadcast any number of arguments from master node to other nodes."""
        return args if cls.is_without_hvd else hvd.broadcast_object(args)

    @classmethod
    def assert_same_across_all_nodes(cls, arg: Any) -> None:
        """Assert a value is same across all processes."""
        if not cls.is_without_hvd:
            all_values = hvd.allgather_object(arg)
            Contract.assert_true(
                all(value == all_values[0] for value in all_values[1:]),
                "A Value for model parameter is different across nodes.",
                reference_code=ReferenceCodes._TS_DIST_HYPERPARAM_DIFFERENT_ON_MACHINES,
                target="Distributed timeseries hyperparameters"
            )

    @classmethod
    def get_distributed_sampler(
        cls,
        dataset: Dataset,
        num_replicas: int,
        rank: int,
        shuffle: bool
    ) -> Sampler:
        """Get the distributed sampler based on OS and configuration."""
        if sys.platform == 'win32' or DistributedSampler is None:
            # If we cannot import distributed sampler or the platform is windows, the sampler is None
            # This is because DistributedSampler is not supported for windows currently.
            # By returning None, the dataloader will use it's own sampler.
            if shuffle:
                return RandomSampler(dataset)
            else:
                return SequentialSampler(dataset)
        return DistributedSampler(
            dataset,
            num_replicas=num_replicas,
            rank=rank,
            shuffle=shuffle
        )

    @classmethod
    def allgather_object(cls, *args: Any) -> Sequence[Any]:
        """Gathers all objects from all machines."""
        return [args] if cls.is_without_hvd else hvd.allgather_object(args)

    @classmethod
    def allreduce_sum(cls, arg: Union[float, np.array]) -> Union[float, np.array]:
        """
        Gather values from all machines and adding them up.

        :param arg: Value to be aggregated, can be a single number or a numpy array.

        :return: If a single number is passed as arg, a single number will be returned.
        Otherwise, a numpy array will be returned. The value will be the variable aggregated across
        all of the machines. If the value is an array, all values in dimension 0 are added.
        Example- [1, 2, 3], [4, 5, 6] => [5, 7, 9]
        """
        if cls.is_without_hvd:
            return arg
        return_array = True
        if not isinstance(arg, np.ndarray):
            arg = [arg]
            return_array = False
        arg_tensor = torch.tensor(arg, dtype=torch.float64)
        result_tensor = hvd.allreduce(arg_tensor, op=hvd.Sum)
        if return_array:
            # multiple elements are returned as a numpy array.
            return result_tensor.numpy()
        else:
            # Single is element is returned as a scalar
            return result_tensor.item()

    @classmethod
    def clear_gpu_cache(cls) -> None:
        """Clear GPU cache (if GPU is available)."""
        # If GPU is available, free up cache.
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    @classmethod
    def get_distribution_strategy(cls, is_distributed_training: bool) -> DistributionStrategy:
        """Get the distribution strategy for training."""
        if cls.is_without_hvd or not is_distributed_training:
            return SingleProcessDistributionStrategy()
        return HorovodDistributionStrategy()
