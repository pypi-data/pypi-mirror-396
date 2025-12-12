# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Sequence, Tuple
from joblib import Parallel, delayed
import logging
import numpy as np
import pandas as pd
import psutil

from azureml.automl.core.shared import logging_utilities
from azureml.automl.core.shared.constants import MLTableDataLabel
from azureml.contrib.automl.dnn.forecasting._distributed._sharding._sharding_strategy_base import _ShardingStrategyBase
from azureml.contrib.automl.dnn.forecasting._distributed._shard_summary import GrainShardSummary
from azureml.contrib.automl.dnn.forecasting.wrapper._distributed_helper import DistributedHelper
from azureml.data import TabularDataset
from azureml.train.automl.runtime._partitioned_dataset_utils import _get_dataset_for_grain
from azureml.contrib.automl.dnn.forecasting._distributed._data_for_inference import _dataset_to_picklable_dataset

logger = logging.getLogger(__name__)


def _get_memmap_shape(shard_summaries: Sequence[GrainShardSummary], column_names: Sequence[str]) -> Tuple[int, int]:
    """
    Get the shape of the memmap to create.

    :param shard_summaries: Sequence of shard summaries to be saved in the mammap array.
    :param column_names: Sequence of columns that are in our dataset.

    :returns: A tuple of number of rows and columns for the memmap file.
    """
    rows = sum(shard_summary.num_rows for shard_summary in shard_summaries)
    columns = len(column_names)
    return (rows, columns)


def _download_shard_to_memmap(
    grain_shard_summary: GrainShardSummary,
    numericalized_grain_columns: Sequence[int],
    memmap: np.ndarray,
    memmap_offset: int,
    dataset: TabularDataset,
    columns: Sequence[str]
) -> None:
    """
    Download a shard summary into the memmap array at a given offset.

    :param shard_summary: The shard summary representing the piece of data to be downloaded.
    :param numericalized_grain_columns: Index of numericalized grain columns.
    :param memmap: The memmap file in which the data has to be saved.
    :param memmap_offset: The offset at which the data has to be saved.
    :param dataset: The TabularDataset from which data has to be fetched.
    :param columns: The Sequence of columns (in the provided order) that our data should have.
    """
    if grain_shard_summary.num_rows == 0:
        return
    # Download the grain depending on the grain and the dataset type
    grain_key_value_and_path = grain_shard_summary.grain_summary.grain_key_value_and_common_path
    grain_data: TabularDataset = _get_dataset_for_grain(grain_key_value_and_path, dataset)
    # Get the range of rows that we want to keep
    rows_to_skip = grain_shard_summary.rows_to_download_range[0]
    rows_to_pad = grain_shard_summary.rows_to_pad
    rows_to_take = grain_shard_summary.rows_to_download_range[1] - grain_shard_summary.rows_to_download_range[0]
    # Get the pandas dataframe with the required rows
    grain_data = grain_data \
        .keep_columns(columns) \
        .skip(rows_to_skip) \
        .take(rows_to_take)
    df: pd.DataFrame = grain_data.to_pandas_dataframe()[columns]
    # Convert the dataframe to numpy array and store it in the memmap and the desired offset
    numpy_data = df.to_numpy()
    memmap[memmap_offset + rows_to_pad : memmap_offset + rows_to_pad + rows_to_take, :] = numpy_data
    if rows_to_pad:
        memmap[memmap_offset : memmap_offset + rows_to_pad, :] = 0
        memmap[memmap_offset : memmap_offset + rows_to_pad, numericalized_grain_columns] = \
            numpy_data[0, numericalized_grain_columns]


def _get_offsets(grain_shard_summaries: Sequence[GrainShardSummary]) -> np.ndarray:
    """
    Get the offsets at which each grain should be saved in the memmap file.

    :param shard_summaries: The Sequence of shard summaries for which the offsets have to be calculated.

    :returns: A numpy array containing the offsets for each grain.
    """
    grain_offsets = np.zeros(len(grain_shard_summaries) + 1, dtype=np.int64)
    grain_offsets[1 :] = [shard_summary.num_rows for shard_summary in grain_shard_summaries]
    return grain_offsets.cumsum()


def download_shards(
    sharding_strategy: _ShardingStrategyBase,
    train_dataset: TabularDataset,
    val_dataset: TabularDataset,
    numericalized_grain_columns: Sequence[int],
    columns: Sequence[str],
    download_file_path: str,
    dataset_type: MLTableDataLabel,
    should_download: bool,
) -> np.ndarray:
    """
    Download the shards for a dataset type.

    :param sharding_strategy: The sharding strategy to be used to get the shard summaries.
    :param train_dataset: The training TabularDataset.
    :param val_dataset: The validation TabularDataset.
    :param numericalized_grain_columns: Index of numericalized grain columns.
    :param columns: The Sequence of columns in a specified order that have to be downloaded.
    :param download_file_path: The path where the memmap file has to be created.
    :param dataset_type: The type of the dataset.
    :param should_download: If we should download the data or just calculate the offsets.

    :returns: A numpy array of offsets at which different grains are stored.
    """
    shard_summaries = sharding_strategy.get_shards_for_node(DistributedHelper.node_rank(), dataset_type)
    memmap_shape = _get_memmap_shape(shard_summaries, columns)
    download_grain_offsets = _get_offsets(shard_summaries)
    train_dataset = _dataset_to_picklable_dataset(train_dataset)
    val_dataset = _dataset_to_picklable_dataset(val_dataset)
    if should_download:
        with logging_utilities.log_activity(
            logger=logger,
            activity_name=f"Create {dataset_type.value} memmap file of shape {memmap_shape}"
        ):
            # We use np.lib.format.open_memmap instead of np.memmap because when we use np.memmap to
            # load a already created memmap of shape (N, M), it loads it with shape (N * M) unless we
            # specify shape to it. This issue is not present with np.lib.format.open_memmap
            memmap_array = np.lib.format.open_memmap(
                download_file_path,
                dtype=np.float32,
                shape=memmap_shape,
                mode="w+"
            )
        with logging_utilities.log_activity(logger=logger, activity_name=f"Download{dataset_type.value}"):
            concurrency = min(psutil.cpu_count(), len(shard_summaries), 256)
            # Set verbose to 1 to get minimal log lines.
            Parallel(n_jobs=concurrency, verbose=1)([
                delayed(_download_shard_to_memmap)(
                    shard_summary,
                    numericalized_grain_columns,
                    memmap_array,
                    grain_offset,
                    train_dataset if shard_summary.dataset_type is MLTableDataLabel.TrainData else val_dataset,
                    columns,
                ) for (shard_summary, grain_offset) in zip(shard_summaries, download_grain_offsets)
            ])
            memmap_array.flush()
            del memmap_array
    # The grain shard summary list for validation dataset can contain grain shard summary from the
    # training dataset. Hence, when calculating offsets for the validation dataset, we cannot use
    # them for calculating offsets. To fix this, we remove them from the offset list.
    # Example- If we have the following to shard for validation dataset (3T below would mean 3 rows from
    #  training dataset and 3V would mean 3 rows from the validation dataset)-
    # 5T, 3V, 5T, 6V, 5T, 2V, our offsets would be-
    # 0, 5, 8, 13, 19, 24, 26.
    # But, only 0, 8, 19, 26 represet the offsets for grains in validation datasets.
    grain_offsets: Sequence[int] = []
    for (idx, grain_offset) in enumerate(download_grain_offsets):
        if idx == 0 or shard_summaries[idx - 1].dataset_type is dataset_type:
            grain_offsets.append(grain_offset)
    return np.array(grain_offsets)
