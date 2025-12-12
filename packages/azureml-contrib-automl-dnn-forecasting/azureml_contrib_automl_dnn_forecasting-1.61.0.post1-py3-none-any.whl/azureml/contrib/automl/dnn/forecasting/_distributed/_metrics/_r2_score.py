# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Mapping, Sequence

import numpy as np

from forecast.metrics import Metric, MetricMode
from azureml.contrib.automl.dnn.forecasting.wrapper._distributed_helper import DistributedHelper
from azureml.contrib.automl.dnn.forecasting._distributed._metrics._metric_util import clip_metric
from azureml.training.tabular.score import constants


class R2Score(Metric):
    """Computes the R2 Score."""

    def __init__(self, index: int, mode: MetricMode):
        """
        Computes the R2 Score.

        :param index: The index in the forecast_head axis of the quantity to compare to the target
        :param mode: Which datasets the metric should be computed on
        """
        super().__init__(mode)
        self._index = index
        self._diff_squared = 0.0
        self._count = 0.0
        self._act_sum = 0.0
        self._act_sq_sum = 0.0
        self.reset_state()

    def update_state(self, inputs: Mapping[str, np.ndarray], act: np.ndarray, pred: Sequence[np.ndarray]) -> None:
        """
        Updates the streaming R2 Score state.

        :param inputs: Unused
        :param act: The target values (shape [batch_size, forecast_length])
        :param pred: The predicted values (shape [forecast_heads][batch_size, forecast_length])
        """
        pred = pred[self._index].reshape(-1)
        act = act.reshape(-1)
        self._diff_squared += np.sum(np.square(pred - act))
        self._count += len(act)
        self._act_sum += np.sum(act)
        self._act_sq_sum += np.sum(np.square(act))

    def reset_state(self) -> None:
        """Resets the state of R2 Score at the end of an epoch."""
        self._diff_squared = 0.0
        self._count = 0.0
        self._act_sum = 0.0
        self._act_sq_sum = 0.0

    def result(self) -> float:
        """Computes the R2 Score over the last epoch."""
        diff_squared = DistributedHelper.allreduce_sum(self._diff_squared)
        count = DistributedHelper.allreduce_sum(self._count)
        act_sum = DistributedHelper.allreduce_sum(self._act_sum)
        act_sq_sum = DistributedHelper.allreduce_sum(self._act_sq_sum)

        if count == 0:
            return clip_metric(np.nan, constants.R2_SCORE)
        numerator = diff_squared
        denominator = act_sq_sum - act_sum * act_sum / count
        if numerator == 0:
            return 1.0
        if denominator == 0:
            return 0.0
        return clip_metric(1.0 - numerator / denominator, constants.R2_SCORE)
