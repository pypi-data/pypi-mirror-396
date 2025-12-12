# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Mapping, Sequence, Tuple

import numpy as np

from azureml.contrib.automl.dnn.forecasting.wrapper._distributed_helper import DistributedHelper
from azureml.contrib.automl.dnn.forecasting._distributed._metrics._metric_util import clip_metric
from azureml.training.tabular.score import constants
from forecast.data import FUTURE_IND_KEY
from forecast.metrics import Metric, MetricMode


class NRMSLE(Metric):
    """Computes the Normalized Root Mean Squared Log Error."""

    def __init__(
        self,
        index: int,
        mode: MetricMode,
        grain_map: Mapping[Tuple, int],
        numericalized_grain_cols: Sequence[int],
        y_min: Sequence[float],
        y_max: Sequence[float],
    ):
        """Computes the Normalized Root Mean Squared Log Error.

        :param index: The index in the forecast_head axis of the quantity to compare to the target.
        :param mode: Which datasets the metric should be computed on.
        :param grain_map: Mapping of numericalized grain cols to grain index.
        :param numericalized_grain_cols: Sequence of numericalized grain column names.
        :param y_min: Sequence of y_min for each grain.
        :param y_max: Sequence of y_max for each grain.
        """
        super().__init__(mode)
        self.numericalized_grain_cols = numericalized_grain_cols
        self.grain_map = grain_map
        self._index = index
        self.grain_count = len(grain_map)
        self._tot = np.full(self.grain_count, 0.0)
        self._count = np.full(self.grain_count, 0.0)
        self._y_min = np.array(y_min)
        self._y_max = np.array(y_max)
        self._has_negatives = np.full(self.grain_count, 0)
        self.reset_state()

    def update_state(self, inputs: Mapping[str, np.ndarray], act: np.ndarray, pred: Sequence[np.ndarray]) -> None:
        """Updates the streaming metric state.

        :param inputs: The inputs for which the predictions are made.
        :param act: The target values (shape [batch_size, forecast_length])
        :param pred: The predicted values (shape [forecast_heads][batch_size, forecast_length])
        """
        pred = pred[self._index]
        grain_cols = inputs[FUTURE_IND_KEY][:, self.numericalized_grain_cols, 0].astype(int)
        grain_indices = np.apply_along_axis(lambda a: self.grain_map[tuple(a)], 1, grain_cols).reshape(-1)

        for grain_idx, sample_pred, sample_act in zip(grain_indices, pred, act):
            if self._has_negatives[grain_idx] == 0 and np.any(sample_pred < 0) or np.any(sample_act < 0):
                self._has_negatives[grain_idx] = 1
            if self._has_negatives[grain_idx] != 1:
                sample_pred = np.log1p(sample_pred)
                sample_act = np.log1p(sample_act)
                self._tot[grain_idx] += np.sum(np.square(sample_pred.reshape(-1) - sample_act.reshape(-1)))
            self._count[grain_idx] += len(sample_pred.reshape(-1))

    def reset_state(self) -> None:
        """Resets the state of the metric at the end of an epoch."""
        self._tot = np.full(self.grain_count, 0.0)
        self._count = np.full(self.grain_count, 0.0)
        self._has_negatives = np.full(self.grain_count, 0)

    def result(self) -> float:
        """Computes the metric over the last epoch."""
        tot = DistributedHelper.allreduce_sum(self._tot)
        count = DistributedHelper.allreduce_sum(self._count)
        if np.sum(count) == 0:
            return clip_metric(np.nan, constants.NORM_RMSLE)
        is_negative_per_series = DistributedHelper.allreduce_sum(self._has_negatives)
        non_zero = count > 0
        max_min_div = np.abs(np.log1p(self._y_max) - np.log1p(self._y_min))
        max_min_div[max_min_div == 0] = 1.0
        metric_per_series = np.sqrt(tot / count) / max_min_div
        metric_per_series[is_negative_per_series > 0] = 1.0
        metric_per_series = metric_per_series[non_zero]
        if np.isnan(metric_per_series).sum() == len(metric_per_series):
            return clip_metric(np.nan, constants.NORM_RMSLE)
        metric_per_series[metric_per_series > 1] = 1.0
        return clip_metric(float(np.nanmean(metric_per_series)), constants.NORM_RMSLE)
