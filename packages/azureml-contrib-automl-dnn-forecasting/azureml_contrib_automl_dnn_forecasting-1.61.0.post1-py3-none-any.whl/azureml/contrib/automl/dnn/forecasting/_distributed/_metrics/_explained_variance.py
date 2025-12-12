# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Mapping, Sequence

import numpy as np

from forecast.metrics import Metric, MetricMode
from azureml.contrib.automl.dnn.forecasting._distributed._metrics._metric_util import clip_metric
from azureml.contrib.automl.dnn.forecasting.wrapper._distributed_helper import DistributedHelper
from azureml.training.tabular.score import constants


class ExplainedVariance(Metric):
    """Computes the Explained Variance."""

    def __init__(self, index: int, mode: MetricMode):
        """
        Computes the Explained Variance.

        :param index: The index in the forecast_head axis of the quantity to compare to the target
        :param mode: Which datasets the metric should be computed on
        """
        super().__init__(mode)
        self._index = index
        self._residue_sum = 0.0
        self._residue_sq_sum = 0.0
        self._act_sum = 0.0
        self._act_sq_sum = 0.0
        self._count = 0.0
        self.reset_state()

    def update_state(self, inputs: Mapping[str, np.ndarray], act: np.ndarray, pred: Sequence[np.ndarray]) -> None:
        """
        Updates the streaming Explained Variance state.

        :param inputs: Unused
        :param act: The target values (shape [batch_size, forecast_length])
        :param pred: The predicted values (shape [forecast_heads][batch_size, forecast_length])
        """
        pred = pred[self._index].reshape(-1)
        act = act.reshape(-1)
        self._residue_sum += np.sum(act - pred)
        self._residue_sq_sum += np.sum(np.square(act - pred))
        self._act_sum += np.sum(act)
        self._act_sq_sum += np.sum(np.square(act))
        self._count += len(act)

    def reset_state(self) -> None:
        """Resets the state of Explained Variance at the end of an epoch."""
        self._residue_sum = 0.0
        self._residue_sq_sum = 0.0
        self._act_sum = 0.0
        self._act_sq_sum = 0.0
        self._count = 0.0

    def result(self) -> float:
        """Computes the Explained Variance over the last epoch."""
        residue_sum = DistributedHelper.allreduce_sum(self._residue_sum)
        residue_sq_sum = DistributedHelper.allreduce_sum(self._residue_sq_sum)
        count = DistributedHelper.allreduce_sum(self._count)
        act_sum = DistributedHelper.allreduce_sum(self._act_sum)
        act_sq_sum = DistributedHelper.allreduce_sum(self._act_sq_sum)
        if count == 0:
            return clip_metric(np.nan, constants.EXPLAINED_VARIANCE)
        numerator = residue_sq_sum - residue_sum ** 2 / count
        denominator = act_sq_sum - act_sum ** 2 / count
        if numerator == 0:
            return 1.0
        if denominator < 100 * np.finfo(denominator).eps:
            return 0.0
        return clip_metric(1.0 - numerator / denominator, constants.EXPLAINED_VARIANCE)
