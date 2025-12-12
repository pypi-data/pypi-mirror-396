# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from abc import ABC, abstractmethod
from typing import Mapping, Sequence

from azureml.automl.core.shared.constants import MLTableDataLabel
from azureml.contrib.automl.dnn.forecasting._distributed._grain_summary import GrainSummary
from azureml.contrib.automl.dnn.forecasting._distributed._shard_summary import GrainShardSummary


class _ShardingStrategyBase(ABC):
    """Base class for a sharding strategy."""

    def __init__(self,
                 train_grain_summary: Sequence[GrainSummary],
                 valid_grain_summary: Sequence[GrainSummary],
                 node_count: int,
                 lookback: int,
                 horizon: int,
                 validation_step_size: int) -> None:
        """
        Base class for a sharding strategy.

        :param train_grain_summaries: Sequence of grain summaries for the training dataset
        :param valid_grain_summaries: Sequence of grain summaries for the validation dataset
        :param node_count: Number of machines on which the dataset has to be shareded
        :param horizon: Number of time steps to forecast.
        :param lookback: Time step size between consecutive examples.
        :param validation_step_size: The step size for the validation dataset.
        """
        super().__init__()

    @abstractmethod
    def get_shards_for_node(self, node_id: int, dataset_split: MLTableDataLabel) -> Sequence[GrainShardSummary]:
        """
        Get the Sequence of shard summaries for a specific machine.

        :param node_id: The machine id.
        :param dataset_split: The dataset split for which Sequence of shard summaries is required.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def num_of_processes_per_shard(self) -> Mapping[MLTableDataLabel, int]:
        """
        Get the dictionary mapping dataset type to the number of process sharing the dataset shard.

        :returns:
            A Mapping where the key is the dataset type
            and value is number of machines sharing the data.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def process_rank_in_shard(self) -> Mapping[MLTableDataLabel, int]:
        """
        Get the dictionary mapping dataset type to the rank of process sharing the dataset shard.

        :returns:
            A Mapping where the key is the dataset type
            and value is index of process sharing the dataset.
        """
        raise NotImplementedError
