# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Sequence
from joblib import Parallel, delayed
import logging
import pandas as pd
import psutil

from azureml.automl.core.shared import logging_utilities
from azureml.automl.core.shared.constants import TimeSeriesInternal
from azureml.contrib.automl.dnn.forecasting._distributed._grain_summary import GrainSummary
from azureml.data import TabularDataset
from azureml.train.automl.runtime._partitioned_dataset_utils import _get_dataset_for_grain

logger = logging.getLogger(__name__)


def _dataset_to_picklable_dataset(dataset: TabularDataset):
    """Return a picklable TabuarDataset from a TabularDataset that may not be picklable (for reasons unknown)."""
    return TabularDataset._create(
        dataset._dataflow,
        dataset._properties,
        telemetry_info=dataset._telemetry_info
    )


def _get_k_rows_from_end(
    grain_summary: GrainSummary,
    dataset: TabularDataset,
    row_count: int
) -> pd.DataFrame:
    """Returns the last K rows from the end of a dataset"""
    # row_count can be greater than total number of rows in the grain.
    # In this case, we will take all rows of the grain.
    rows_to_take = min(row_count, grain_summary.num_rows)
    rows_to_skip = grain_summary.num_rows - rows_to_take
    partial_dataset = _get_dataset_for_grain(grain_summary.grain_key_value_and_common_path, dataset)
    partial_dataset = partial_dataset.skip(rows_to_skip).take(rows_to_take)
    df: pd.DataFrame = partial_dataset.to_pandas_dataframe()
    df.drop(columns=TimeSeriesInternal.DUMMY_LOG_TARGET_COLUMN, inplace=True, errors='ignore')
    return df


def _download_lookback_data_for_inference(
    train_grain_summary: GrainSummary,
    valid_grain_summary: GrainSummary,
    train_dataset: TabularDataset,
    valid_dataset: TabularDataset,
    lookback: int
) -> pd.DataFrame:
    """Download the last lookback rows from train and validation dataset combined."""
    df_valid = _get_k_rows_from_end(valid_grain_summary, valid_dataset, lookback)
    if df_valid.shape[0] < lookback:
        rows = lookback - df_valid.shape[0]
        df_train = _get_k_rows_from_end(train_grain_summary, train_dataset, rows)
        df_valid = pd.concat([df_train, df_valid], copy=False, ignore_index=True)
    return df_valid


def get_lookback_data_for_inference_from_partitioned_datasets(
    train_grain_summaries: Sequence[GrainSummary],
    valid_grain_summaries: Sequence[GrainSummary],
    train_dataset: TabularDataset,
    valid_dataset: TabularDataset,
    lookback: int
) -> pd.DataFrame:
    """Download lookback data for inference used in distributed TCN."""
    with logging_utilities.log_activity(logger=logger, activity_name="DownloadDataForInference"):

        train_dataset = _dataset_to_picklable_dataset(train_dataset)
        valid_dataset = _dataset_to_picklable_dataset(valid_dataset)

        concurrency = min(psutil.cpu_count(), len(train_grain_summaries), 256)
        # Set verbose to 1 to get minimal log lines that output values like-
        # the number of tasks completed, total number of tasks and time taken.
        result = Parallel(n_jobs=concurrency, verbose=1)([
            delayed(_download_lookback_data_for_inference)(
                train_grain_summary,
                valid_grain_summary,
                train_dataset,
                valid_dataset,
                lookback
            ) for (train_grain_summary, valid_grain_summary) in
            zip(train_grain_summaries, valid_grain_summaries)
        ])
    return pd.concat(result, copy=False, ignore_index=True)
