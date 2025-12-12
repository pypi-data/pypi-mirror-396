"""Provides a PyTorch-compatible dataset."""

import bisect
from typing import List, Optional, Sequence, Tuple, Union

import numpy as np
from torch.utils.data import Dataset

from forecast.data import (
    FUTURE_DEP_KEY,
    FUTURE_DEP_KEY_UTF,
    FUTURE_IND_KEY,
    FUTURE_IND_KEY_UTF,
    PAST_DEP_KEY,
    PAST_DEP_KEY_UTF,
    PAST_IND_KEY,
    PAST_IND_KEY_UTF,
)
from .transforms import AbstractTransform, TSample


class TimeSeriesDatasetBase(Dataset):
    def __init__(
        self,
        *,
        window_size: int,
        forecast_horizon: int,
        num_features: int,
        targets: Sequence[int],
        step: int = 1,
        transform: Optional[AbstractTransform] = None,
        future_regressors: Optional[Sequence[int]] = None,
        include_untransformed: bool = False,
    ):
        self._window_size = window_size
        self._forecast_period = forecast_horizon
        self._full_sample_size = self._window_size + self._forecast_period
        self._step = step
        self._transform = transform

        self._targets = list(targets)
        target_set = set(targets)
        self._regressors = [i for i in range(num_features) if i not in target_set]
        self._future_regressors = future_regressors if future_regressors else self._regressors
        self._include_utf = include_untransformed

    @property
    def transform(self) -> Optional[AbstractTransform]:
        return self._transform


class PrecomputedTimeSeriesDataset(TimeSeriesDatasetBase):
    """Provides a moving window view into a list of time series."""

    def __init__(
        self,
        time_series: Union[np.ndarray, Sequence[np.ndarray]],
        window_size: int,
        forecast_horizon: int,
        targets: List[int],
        step: int = 1,
        transform: Optional[AbstractTransform] = None,
        future_regressors: Optional[List[int]] = None,
        include_untransformed: bool = False,
    ):
        """Creates a time series dataset.

        Parameters
        ----------
        time_series: np.ndarray | Sequence[np.ndarray]
            List of time series arrays
        window_size: int
            Number of samples used as input for forecasting.
        forecast_horizon: int
            Number of samples to forecast.
        targets: List[int]
            A list of row indices of the forecast targets
        step: int
            Number of samples between consecutive examples from the same time series.
        transform: AbstractTransform, optional
            A transform to apply to the data (defaults to None)
        future_regressors: List[int], optional
            The future regressors available for prediction (defaults to all non-targets)
        include_untransformed: bool, optional
            Determines whether untransformed values are also included in a sample (default is False)

        """
        super().__init__(
            window_size=window_size,
            forecast_horizon=forecast_horizon,
            num_features=time_series[0].shape[0],
            targets=targets,
            step=step,
            transform=transform,
            future_regressors=future_regressors,
            include_untransformed=include_untransformed,
        )
        self._data = time_series

        # store (ts_index, start_ind) in list
        # __getitem__ will use this to slice the cached TS data
        self._sample_ids: List[Tuple[int, int]] = []

        n_dropped = 0
        for i, ts in enumerate(self._data):
            # convert a single time series into a series of sequential samples
            if ts.shape[-1] < self._forecast_period:
                # we can't forecast N samples if we have < N samples to serve as ground truth
                n_dropped += 1
                continue
            elif ts.shape[-1] < self._full_sample_size:
                # If the time series is too short, we will zero pad the input
                # TODO: revisit whether we should pad
                num_examples = 1
            else:
                # truncate incomplete samples at the end
                num_examples = (ts.shape[-1] - self._full_sample_size + self._step) // self._step

            # store (ts_index, start_ind)
            for j in range(num_examples):
                self._sample_ids.append((i, j * self._step))

        # Inform user about time series that were too short
        if n_dropped > 0:
            print(f"Dropped {n_dropped} time series due to length.")

    def __len__(self) -> int:
        """Provides the length of the dataset.

        Returns
        -------
        int
            The number of examples in the dataset

        """
        return len(self._sample_ids)

    def __getitem__(self, idx: int) -> TSample:
        """Retrieves an example from the dataset.

        Parameters
        ----------
        idx: int
            The index of the example to retrieve

        Returns
        -------
            The transformed sample

        """
        # Get time series
        ts_id, offset = self._sample_ids[idx]
        ts = self._data[ts_id]

        # Prepare input and target. Zero pad if necessary.
        if ts.shape[-1] < self._full_sample_size:
            # If the time series is too short, zero-pad on the left
            # TODO: revisit whether we should pad
            X_past = ts[self._regressors, : -self._forecast_period]
            X_past = np.pad(
                X_past,
                pad_width=((0, 0), (self._window_size - X_past.shape[-1], 0)),
                mode="constant",
                constant_values=0,
            )
            y_past = ts[self._targets, : -self._forecast_period]
            y_past = np.pad(
                y_past,
                pad_width=((0, 0), (self._window_size - y_past.shape[-1], 0)),
                mode="constant",
                constant_values=0,
            )

            X_fut = ts[self._future_regressors, -self._forecast_period :]
            y_fut = ts[self._targets, -self._forecast_period :]
        else:
            X_past = ts[self._regressors, offset : offset + self._window_size]
            y_past = ts[self._targets, offset : offset + self._window_size]
            X_fut = ts[self._future_regressors, offset + self._window_size : offset + self._full_sample_size]
            y_fut = ts[self._targets, offset + self._window_size : offset + self._full_sample_size]

        # Create the input and output for the sample
        # X_past: (num_features, window_size)
        # y_past: (num_targets, window_size)
        # X_fut: (num_fut_features, horizon)
        # y_fut: (num_targets, horizon)
        sample = {PAST_IND_KEY: X_past, PAST_DEP_KEY: y_past, FUTURE_IND_KEY: X_fut, FUTURE_DEP_KEY: y_fut}

        if self.transform:
            sample = self.transform(sample)

        if self._include_utf:
            sample[PAST_IND_KEY_UTF] = X_past
            sample[PAST_DEP_KEY_UTF] = y_past
            sample[FUTURE_IND_KEY_UTF] = X_fut
            sample[FUTURE_DEP_KEY_UTF] = y_fut

        return sample


class OnlineTimeSeriesDataset(TimeSeriesDatasetBase):
    def __init__(
        self,
        time_series: np.ndarray,
        window_size: int,
        forecast_horizon: int,
        targets: List[int],
        *,
        step: int = 1,
        ts_id_idx: Optional[int] = None,
        sample_offset: int = 0,
        transform: Optional[AbstractTransform] = None,
        future_regressors: Optional[List[int]] = None,
        include_untransformed: bool = False,
    ):
        """Creates a time series dataset.

        Parameters
        ----------
        time_series: np.ndarray
            A (potentially memmap'd) numpy array
        window_size: int
            Number of samples used as input for forecasting.
        forecast_horizon: int
            Number of samples to forecast.
        targets: List[int]
            A list of row indices of the forecast targets
        step: int
            Number of samples between consecutive examples from the same time series.
        ts_id_idx: Optional[int]
            The column corresponding to the time series id, defaults to None (single time series dataset)
        transform: AbstractTransform, optional
            A transform to apply to the data (defaults to None)
        future_regressors: List[int], optional
            The future regressors available for prediction (defaults to all non-targets)
        include_untransformed: bool, optional
            Determines whether untransformed values are also included in a sample (default is False)

        """
        super().__init__(
            window_size=window_size,
            forecast_horizon=forecast_horizon,
            num_features=time_series.shape[1],
            targets=targets,
            step=step,
            transform=transform,
            future_regressors=future_regressors,
            include_untransformed=include_untransformed,
        )

        self._data = time_series
        self._ts_id_idx = ts_id_idx
        self._sample_offset = sample_offset

        if self._ts_id_idx is not None:
            # if we have >1 time series, we assume
            #     ts_id's range from min_series_id -> min_series_id + N_ts - 1
            #     rows are ordered by ts_id first and date second
            #     data is dense (no missing dates)
            min_series_id = self._data[:, self._ts_id_idx].min()
            num_series = self._data[:, self._ts_id_idx].max() - min_series_id + 1
            ts_inds = np.arange(min_series_id, min_series_id + num_series)[None, :]

            # get the first occurrence of the time series index
            # index 0 --> min_series_id
            self._series_start_row_ind = np.argmax(self._data[:, self._ts_id_idx][:, None] == ts_inds, axis=0)
            assert len(self._series_start_row_ind) == num_series

            # if there is only 1 series, np.diff returns a 1d array of length 0 which will concat with the final value
            # as expected
            num_elem_by_series = np.concatenate(
                [np.diff(self._series_start_row_ind), np.array([self._data.shape[0] - self._series_start_row_ind[-1]])]
            )
            num_sample_by_series = (num_elem_by_series - self._full_sample_size + self._step) // self._step
            assert len(num_sample_by_series) == num_series

            num_empty = (num_sample_by_series == 0).sum()
            if num_empty > 0:
                print(f"Dropping {num_empty} series which lack {self._full_sample_size} time steps.")
            if num_empty == num_series:
                raise RuntimeError("All series lack enough time steps to generate a full sample.")

            # compute the first sample of each series
            # note: series with 0 samples will have the same start index as the next series. bisect_right will handle
            #   this though as it'll use the last instance in the 0-sample run. The only exception is if the dataset
            #   ends with 1 or more 0-sample runs. We handle this case explicitly.
            cumul_sample = num_sample_by_series.cumsum()

            # this also works correctly if cumul_sample is of length 1
            self._series_start_sample_ind = np.concatenate([np.array([0]), cumul_sample[:-1]])
            self._max_sample = cumul_sample[-1] + sample_offset

            # manually override the start_sample_ind to inf for any trailing series that have 0 samples
            # this ensures that bisect always stays to their left for all finite values
            if num_sample_by_series[-1] == 0:
                for i in range(1, num_series):
                    if num_sample_by_series[-i] == 0:
                        self._series_start_sample_ind[-i] = np.inf
                    else:
                        break
        else:
            # otherwise, we have a single time series and assume:
            #     rows are ordered by date
            #     data is dense (no missing dates)
            self._series_start_row_ind = self._series_start_sample_ind = None
            self._max_sample = (len(self._data) - self._full_sample_size + self._step) // self._step + sample_offset

    def __len__(self) -> int:
        # TODO: fix for sharded datasets
        return self._max_sample

    def __getitem__(self, idx: int) -> TSample:
        """Retrieves an example from the dataset.

        Parameters
        ----------
        idx: int
            The index of the example to retrieve

        Returns
        -------
            The transformed sample

        """
        if idx < self._sample_offset or idx >= self._max_sample:
            raise IndexError(f"Index {idx} if out of the bounds [{self._sample_offset}, {self._max_sample})")

        idx -= self._sample_offset
        if self._series_start_sample_ind is not None:
            series_idx = bisect.bisect_right(self._series_start_sample_ind, idx) - 1
            series_start_row_ind = self._series_start_row_ind[series_idx]
            sample_start_row_ind = series_start_row_ind + (idx - self._series_start_sample_ind[series_idx]) * self._step
        else:
            sample_start_row_ind = idx * self._step

        X_past = self._data[sample_start_row_ind : sample_start_row_ind + self._window_size, self._regressors]
        y_past = self._data[sample_start_row_ind : sample_start_row_ind + self._window_size, self._targets]
        X_fut = self._data[
            sample_start_row_ind + self._window_size : sample_start_row_ind + self._full_sample_size,
            self._future_regressors,
        ]
        y_fut = self._data[
            sample_start_row_ind + self._window_size : sample_start_row_ind + self._full_sample_size, self._targets
        ]

        # Create the input and output for the sample
        # X_past: (num_features, window_size)
        # y_past: (num_targets, window_size)
        # X_fut: (num_fut_features, horizon)
        # y_fut: (num_targets, horizon)
        sample = {PAST_IND_KEY: X_past.T, PAST_DEP_KEY: y_past.T, FUTURE_IND_KEY: X_fut.T, FUTURE_DEP_KEY: y_fut.T}

        if self.transform:
            sample = self.transform(sample)

        if self._include_utf:
            sample[PAST_IND_KEY_UTF] = X_past.T
            sample[PAST_DEP_KEY_UTF] = y_past.T
            sample[FUTURE_IND_KEY_UTF] = X_fut.T
            sample[FUTURE_DEP_KEY_UTF] = y_fut.T

        return sample


# for backwards compatibility
TimeSeriesDataset = PrecomputedTimeSeriesDataset
