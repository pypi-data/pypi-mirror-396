# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Mapping, Sequence

import numpy as np

from forecast.metrics import Metric, MetricMode
from azureml.contrib.automl.dnn.forecasting.wrapper._distributed_helper import DistributedHelper
from azureml.contrib.automl.dnn.forecasting._distributed._metrics._metric_util import clip_metric
from azureml.training.tabular.score import constants


class MAPE(Metric):
    """Computes the Mean Absolute Percentage Error."""

    def __init__(self, index: int, mode: MetricMode):
        """
        Computes the Mean Absolute Percentage Error.

        :param index: The index in the forecast_head axis of the quantity to compare to the target
        :param mode: Which datasets the metric should be computed on
        """
        super().__init__(mode)
        self._index = index
        self._tot = self._count = 0.0
        self.reset_state()

    def update_state(self, inputs: Mapping[str, np.ndarray], act: np.ndarray, pred: Sequence[np.ndarray]) -> None:
        """
        Updates the streaming Mean Absolute Percentage Error state.

        :param inputs: Unused
        :param act: The target values (shape [batch_size, forecast_length])
        :param pred: The predicted values (shape [forecast_heads][batch_size, forecast_length])
        """
        pred = pred[self._index].reshape(-1)
        act = act.reshape(-1)
        safe = ~np.isclose(act, 0.0)
        act_safe = act[safe]
        pred_safe = pred[safe]
        epsilon = np.finfo(np.float64).eps
        self._tot += np.sum(np.abs(pred_safe - act_safe) / np.maximum(np.abs(act_safe), epsilon))
        self._count += len(pred_safe)

    def reset_state(self) -> None:
        """Resets the state of Mean Absolute Percentage Error at the end of an epoch."""
        self._count = 0.0
        self._tot = 0.0

    def result(self) -> float:
        """Computes the Mean Absolute Percentage Error over the last epoch."""
        tot = DistributedHelper.allreduce_sum(self._tot)
        count = DistributedHelper.allreduce_sum(self._count)
        if count == 0:
            return clip_metric(np.nan, constants.MAPE)
        return clip_metric(tot / count * 100, constants.MAPE)
