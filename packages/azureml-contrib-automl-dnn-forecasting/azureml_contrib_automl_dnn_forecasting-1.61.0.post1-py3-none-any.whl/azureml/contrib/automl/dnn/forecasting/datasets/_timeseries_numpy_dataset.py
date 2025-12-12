# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module for creating timeseries dataset from numpy array."""

import bisect
import numpy as np
import torch
from torch.utils.data import Dataset
from typing import Optional

from forecast.data import (
    FUTURE_DEP_KEY,
    FUTURE_IND_KEY,
    PAST_DEP_KEY,
    PAST_IND_KEY,
)
from forecast.data.transforms import AbstractTransform, TSample

from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.core.shared._diagnostics.contract import Contract


class TimeSeriesNumpyDataset(Dataset):
    """This class provides a dataset for training timeseries model with numpy arrays."""

    def __init__(self,
                 data: np.ndarray,
                 data_fut: np.ndarray,
                 data_offsets: np.ndarray,
                 horizon: int,
                 lookback: int,
                 step=1,
                 transform: Optional[AbstractTransform] = None,
                 future_channels: Optional[int] = None
                 ):
        """
        Create timeseries dataset for training and evaluation.
        :param data: The numpy array containing the timeseries data. It is of shape (N, M)
                     where N is the sum of rows across all grains and M is the number of columns.
                     The last column will always be the target column.
        :param data_fut: Similar as data, but only with the columns that are available at forecast
                         time.
        :param data_offsets: The offsets at which different timeseries are present in data. It is a
                             1-D array of length equal to the number of grains in the data. It
                             should have 0 as the first element and total number of rows as the
                             last element.
        :param horizon: Number of time steps to forecast.
        :param lookback: Time step size between consecutive examples.
        :param step: Number of rows to move ahead to get the next sample.
        :param transform: Transformations to apply on each sample.
        :param future_channels: Number of featurized columns which are available at forecast time.
        """
        self._data = data
        self._data_fut = data_fut
        self._data_offsets = data_offsets
        self._horizon = horizon
        self._lookback = lookback
        self._step = step
        self._future_channels = future_channels
        Contract.assert_true(
            len(self._data_offsets) == 0 or self._data_offsets[0] == 0,
            "Grain offsets should be either empty or start with 0",
            reference_code=ReferenceCodes._TS_NUMPY_DATASET_INVALID_OFFSETS,
            target="Timeseries numpy dataset"
        )
        Contract.assert_true(
            all(grain_len == 0 or grain_len >= lookback + horizon for grain_len in np.diff(self._data_offsets)),
            "Some grains were dropped from the dataset.",
            reference_code=ReferenceCodes._TS_NUMPY_DATASET_SHORT_GRAIN_DROPPED,
            target="Timeseries numpy dataset"
        )
        # Imagine we have 5 grains with 2, 3, 2, 3, 3 samples each. _idx_mapping will be the following
        # cumulative array- [2, 5, 7, 10, 13]. The i-th grain contains samples in the range
        # _idx_mapping[i - 1] to _idx_mapping[i] - 1. Example- The 3rd grain above contains 7-th, 8-th
        # and 9-th sample in the whole dataset.
        # To calculate this, first we convert the cumulative offsets to number of rows in each grain.
        # Then we calculate how many samples are in each grain. Finally, we create a cumulative array
        # of it.
        self._idx_mapping = np.array([max(0, (grain_len - lookback - horizon + self._step) // self._step)
                                     for grain_len in np.diff(self._data_offsets)]).cumsum()
        self._len = self._idx_mapping[-1] if len(self._idx_mapping) > 0 else 0
        self.sample_transform = transform
        self.transform = None

    def __len__(self) -> int:
        """
        Return the number of samples in the dataset.

        :return: number of samples.
        """
        return self._len

    def __getitem__(self, idx: int) -> TSample:
        """
        Get the idx-th training sample item from the dataset.

        :param idx: the item to get the sample.
        :return: returns the idx-th sample.
        """
        # idx < 0 means we want a sample from the end.
        # Example- arr[-1] means the last element of arr.
        if idx < 0:
            idx += self._len
        Contract.assert_true(
            idx >= 0 and idx < self._len,
            f"idx {idx} not in valid range",
            reference_code=ReferenceCodes._TS_NUMPY_DATASET_IDX_NOT_IN_VALID_RANGE,
            target="Timeseries numpy dataset"
        )

        # grain_idx is the index of the grain for which we are fetching the sample.
        grain_idx = bisect.bisect_right(self._idx_mapping, idx)
        # grain_start_idx is the row at which (grain_idx)-th grain starts.
        grain_start_idx = self._data_offsets[grain_idx]
        if grain_idx > 0:
            # sample_to_fetch is sample which we need from (grain_idx)-th grain.
            sample_to_fetch = idx - self._idx_mapping[grain_idx - 1]
        else:
            sample_to_fetch = idx

        # We will use lookback_start_idx to lookback_end_idx as inputs to the model.
        # The model will forecast horizon_start_idx to horizon_end_idx.
        lookback_start_idx = grain_start_idx + sample_to_fetch * self._step
        lookback_end_idx = lookback_start_idx + self._lookback
        horizon_start_idx = lookback_end_idx
        horizon_end_idx = horizon_start_idx + self._horizon

        X_past = self._data[lookback_start_idx: lookback_end_idx, : -1]
        y_past = self._data[lookback_start_idx: lookback_end_idx, -1:]
        X_fut = self._data_fut[horizon_start_idx: horizon_end_idx, : -1]
        y_fut = self._data_fut[horizon_start_idx: horizon_end_idx, -1:]
        # In the lines below, we use torch.from_numpy to convert memmap array to
        # numpy array. Pytorch cannot convert memmap array to torch array directly.
        sample = {
            PAST_IND_KEY: torch.from_numpy(X_past.T),
            PAST_DEP_KEY: torch.from_numpy(y_past.T),
            FUTURE_IND_KEY: torch.from_numpy(X_fut.T),
            FUTURE_DEP_KEY: torch.from_numpy(y_fut.T)
        }
        if self.sample_transform:
            # If any transformations are provided, we apply them.
            sample = self.sample_transform(sample)
        return sample

    def feature_count(self):
        """
        Return the number of features in the dataset.

        :return: number of features.
        """
        # self._data.shape[1] is the number of columns.
        # We subtract one because we have one target column.
        return self._data.shape[1] - 1
