# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Mapping, Sequence, List

from azureml.automl.core.shared.constants import MLTableDataLabel
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.contrib.automl.dnn.forecasting._distributed._sharding._sharding_strategy_base import \
    _ShardingStrategyBase
from azureml.contrib.automl.dnn.forecasting._distributed._grain_summary import GrainSummary
from azureml.contrib.automl.dnn.forecasting._distributed._shard_summary import GrainShardSummary
from azureml.contrib.automl.dnn.forecasting.wrapper._distributed_helper import DistributedHelper


class _EqualSamplesShardingStrategy(_ShardingStrategyBase):
    """Equal samples sharding strategy."""

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
        self.grain_summary_list = {
            MLTableDataLabel.TrainData: train_grain_summary,
            MLTableDataLabel.ValidData: valid_grain_summary
        }
        self.node_count = node_count
        self.lookback = lookback
        self.horizon = horizon
        self.validation_step_size = validation_step_size

    def get_shards_for_node(self, node_id: int, dataset_split: MLTableDataLabel) -> Sequence[GrainShardSummary]:
        """
        Get the Sequence of shard summaries for a specific machine.

        :param node_id: The machine id.
        :param dataset_split: The dataset split for which shard summaries is required.
        """
        self._validate_node_id(node_id)

        shard_summaries: List[GrainShardSummary] = []
        step_size = 1 if dataset_split is MLTableDataLabel.TrainData else self.validation_step_size
        additional_lookback_rows = 0 if dataset_split is MLTableDataLabel.TrainData else self.lookback

        # Count the total number of samples
        total_samples = sum(
            self._sample_count_in_grain(grain_summary, additional_lookback_rows, step_size)
            for grain_summary in self.grain_summary_list[dataset_split]
        )
        # Start scheduling for machine with index 0.
        machine_index = 0
        # Initialize the current capacity of machine_index.
        machine_capacity = self._get_capacity_for_machine_index(machine_index, total_samples)

        for idx, grain_summary in enumerate(self.grain_summary_list[dataset_split]):
            samples_to_schedule = self._sample_count_in_grain(grain_summary, additional_lookback_rows, step_size)
            # The start index of the row to be scheduled. If grain has very few rows, start with a lower value
            # such that we pad appropriate number of rows to get one sample.
            row_start_idx = min(-additional_lookback_rows, grain_summary.num_rows - self.lookback - self.horizon)
            # Loop as long as we have some unscheduled samples
            while samples_to_schedule > 0:
                # Schedule all of the remaining samples bounded by the capacity of the current machine
                samples_to_add = min(samples_to_schedule, machine_capacity)
                row_end_idx = row_start_idx + (samples_to_add - 1) * step_size + self.lookback + self.horizon
                # If we are scheduling for the current machine, we save shard summaries
                if machine_index == node_id:
                    shard_summaries.extend(
                        self._get_shard_summary_from_indices(idx, dataset_split, row_start_idx, row_end_idx)
                    )

                machine_capacity -= samples_to_add
                samples_to_schedule -= samples_to_add
                # Get the start index of the last sample and move by step_size to get the next sample start idx.
                row_start_idx = row_end_idx - (self.lookback + self.horizon) + step_size
                Contract.assert_true(
                    machine_capacity >= 0,
                    "Machine capacity cannot be negative",
                    target="Distributed forecasting sharding",
                    reference_code=ReferenceCodes._TS_SHARDING_NEGATIVE_CAPACITY
                )
                if machine_capacity == 0:
                    machine_index += 1
                    machine_capacity = self._get_capacity_for_machine_index(machine_index, total_samples)
                    if machine_index > node_id:
                        break

        if self._should_add_duplicate_sample(node_id, total_samples, dataset_split):
            shard_summaries.append(self._get_first_sample())
        return shard_summaries

    @property
    def num_of_processes_per_shard(self) -> Mapping[MLTableDataLabel, int]:
        """
        Get the dictionary mapping dataset type to the number of process sharing the dataset.

        :returns:
            A Mapping where the key is the dataset type
            and value is number of machines sharing the data.
        """
        return {
            MLTableDataLabel.TrainData: DistributedHelper.local_processes_count(),
            MLTableDataLabel.ValidData: DistributedHelper.local_processes_count()
        }

    @property
    def process_rank_in_shard(self) -> Mapping[MLTableDataLabel, int]:
        """
        Get the dictionary mapping dataset type to the index of process sharing the dataset.

        :returns:
            A Mapping where the key is the dataset type
            and value is index of process sharing the dataset.
        """
        return {
            MLTableDataLabel.TrainData: DistributedHelper.local_rank(),
            MLTableDataLabel.ValidData: DistributedHelper.local_rank()
        }

    def _sample_count_in_grain(
        self,
        grain_summary: GrainSummary,
        additional_lookback_rows: int,
        step_size: int
    ) -> int:
        """
        Get the number of samples in a grain.

        :param grain_summary: the grain summary.
        :param additional_lookback_rows: additional number of lookback rows available.
        :param step_size: Number of rows to move ahead to get the next sample.

        :returns: Number of samples in the grain.
        """
        if grain_summary.num_rows == 0:
            return 0
        return max(
            1,
            (grain_summary.num_rows + additional_lookback_rows - self.lookback - self.horizon + step_size) // step_size
        )

    def _get_capacity_for_machine_index(self, machine_index: int, total_samples: int) -> int:
        """
        Get the total number of samples that should be present in machine_index machine.

        :param machine_index: The index of the machine for which the capacity is needed.
        :param total_samples: The total number of samples in the dataset.

        :returns: The capacity of machine_index machine.
        """
        samples_per_machine = total_samples // self.node_count
        remainder_samples = total_samples % self.node_count
        if machine_index < remainder_samples:
            return samples_per_machine + 1
        return samples_per_machine

    def _should_add_duplicate_sample(
        self,
        machine_index: int,
        total_samples: int,
        dataset_split: MLTableDataLabel
    ) -> bool:
        """
        Check if we should add a duplicate sample to the machine_index machine.

        :param machine_index: The index of the machine for which we need to check.
        :param total_samples: The total number of samples in the dataset.
        :param dataset_split: The split of the dataset.

        :returns: Boolean value indicating if we should add a duplicate sample to the machine_index machine.
        """
        remainder_samples = total_samples % self.node_count
        return dataset_split is MLTableDataLabel.TrainData and machine_index >= remainder_samples \
            and remainder_samples != 0

    def _get_first_sample(self) -> GrainShardSummary:
        """Get first sample from the training dataset"""
        first_train_grain_summary = self.grain_summary_list[MLTableDataLabel.TrainData][0]
        row_end_idx = min(first_train_grain_summary.num_rows, self.lookback + self.horizon)
        row_start_idx = row_end_idx - (self.lookback + self.horizon)
        return GrainShardSummary(
            first_train_grain_summary,
            MLTableDataLabel.TrainData,
            row_start_idx,
            row_end_idx
        )

    def _validate_node_id(self, node_id: int) -> None:
        """Assert node_id is between 0 and num_machines - 1"""
        Contract.assert_true(
            node_id >= 0,
            f"Shards requested for f{node_id} node which is less than 0.",
            log_safe=True
        )
        Contract.assert_true(
            node_id < self.node_count,
            f"Shards requested for f{node_id} node which is less than total number of nodes ({self.node_count}).",
            log_safe=True
        )

    def _get_shard_summary_from_indices(
        self,
        grain_idx: int,
        dataset_split: MLTableDataLabel,
        row_start_idx: int,
        row_end_idx: int
    ) -> Sequence[GrainShardSummary]:
        """Get shard summaries for a grain given a start and end index (Handle lookback and apply padding)."""
        shard_summaries = []
        # For validation data, if row_start_idx < 0, we first take samples from training data.
        # If enough rows are not there in training data, we pad them.
        if row_start_idx < 0 and dataset_split is MLTableDataLabel.ValidData:
            train_grain_rows = self.grain_summary_list[MLTableDataLabel.TrainData][grain_idx].num_rows
            shard_summaries.append(GrainShardSummary(
                self.grain_summary_list[MLTableDataLabel.TrainData][grain_idx],
                MLTableDataLabel.TrainData,
                row_start_idx + train_grain_rows,
                train_grain_rows
            ))
        shard_summaries.append(GrainShardSummary(
            self.grain_summary_list[dataset_split][grain_idx],
            dataset_split,
            max(0, row_start_idx) if dataset_split is MLTableDataLabel.ValidData else row_start_idx,
            row_end_idx
        ))
        return shard_summaries
