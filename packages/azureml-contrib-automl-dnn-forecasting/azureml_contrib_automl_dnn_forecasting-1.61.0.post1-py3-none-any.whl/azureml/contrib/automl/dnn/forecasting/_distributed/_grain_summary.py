# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Any, Mapping, Sequence

from azureml.automl.core.shared.constants import MLTableDataLabel
from azureml.data import TabularDataset
from azureml.data.abstract_dataset import _PartitionKeyValueCommonPath
from azureml.train.automl.runtime._partitioned_dataset_utils import _get_sorted_partitions
from azureml.training.tabular.featurization.timeseries._distributed.timeseries_data_profile import \
    AggregatedTimeSeriesDataProfile, TimeSeriesDataProfile
from azureml.automl.runtime.featurizer.transformer.timeseries._distributed.distributed_timeseries_util import \
    convert_grain_dict_to_str


class GrainSummary:
    """The summary of one grain in the timeseries dataset"""

    def __init__(self,
                 grain: Mapping[str, Any],
                 grain_download_path: str,
                 grain_profile: TimeSeriesDataProfile,
                 dataset_type: MLTableDataLabel) -> None:
        """
        The summary of one grain in the timeseries dataset.

        :param grain: The dictionary representing a grain.
        :param grain_download_path: The path from which this grain can be downloaded.
        :param grain_profile: The data profile for this grain
        :param dataset_type: The dataset type.
        """
        self.grain = grain
        self.grain_download_path = grain_download_path
        if dataset_type is MLTableDataLabel.TrainData:
            self.num_rows = grain_profile.train_row_count
        elif dataset_type is MLTableDataLabel.ValidData:
            self.num_rows = grain_profile.val_row_count
        else:
            # Set to none as that information is not available.
            self.num_rows = None

    @property
    def grain_key_value_and_common_path(self) -> _PartitionKeyValueCommonPath:
        """The grain key value and common path."""
        return _PartitionKeyValueCommonPath(self.grain, self.grain_download_path)


def get_dataset_grain_summaries(dataset: TabularDataset,
                                data_profile: AggregatedTimeSeriesDataProfile,
                                dataset_type: MLTableDataLabel) -> Sequence[GrainSummary]:
    """
    Get the Sequence of grain summary for a dataset.

    :param dataset: The TabularDataset from which we can the grain partitions.
    :param data_profile: The data profile for the train/val datasets.
    :param dataset_type: The type of dataset

    :returns: Return a Sequence of GrainSummary representing the dataset
    """
    grain_keyvalues_and_path_list = _get_sorted_partitions(dataset)
    dataset_grain_summaries: Sequence[GrainSummary] = []
    for grain_keyvalues_and_path in grain_keyvalues_and_path_list:
        grain = grain_keyvalues_and_path.key_values
        grain_download_path = grain_keyvalues_and_path.common_path
        grain_dataprofile = data_profile.profile_mapping.get(convert_grain_dict_to_str(grain), None)
        # If data profile is None, that means it was not generated because of unique target grain
        if grain_dataprofile is not None:
            dataset_grain_summaries.append(
                GrainSummary(grain, grain_download_path, grain_dataprofile, dataset_type)
            )
    return dataset_grain_summaries
