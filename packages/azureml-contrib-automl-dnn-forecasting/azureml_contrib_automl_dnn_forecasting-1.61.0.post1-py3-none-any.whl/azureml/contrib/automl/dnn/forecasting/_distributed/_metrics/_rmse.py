# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Mapping, Sequence

import numpy as np

from forecast.metrics import Metric, MetricMode
from azureml.contrib.automl.dnn.forecasting.wrapper._distributed_helper import DistributedHelper
from azureml.contrib.automl.dnn.forecasting._distributed._metrics._metric_util import clip_metric
from azureml.training.tabular.score import constants


class RMSE(Metric):
    """Computes the Root Mean Squared Error."""

    def __init__(self, index: int, mode: MetricMode):
        """
        Computes the Root Mean Squared Error.

        :param index: The index in the forecast_head axis of the quantity to compare to the target
        :param mode: Which datasets the metric should be computed on
        """
        super().__init__(mode)
        self._index = index
        self._tot = self._count = 0.0
        self.reset_state()

    def update_state(self, inputs: Mapping[str, np.ndarray], act: np.ndarray, pred: Sequence[np.ndarray]) -> None:
        """
        Updates the streaming Root Mean Squared Error state.

        :param inputs: Unused
        :param act: The target values (shape [batch_size, forecast_length])
        :param pred: The predicted values (shape [forecast_heads][batch_size, forecast_length])
        """
        pred = pred[self._index].reshape(-1)
        act = act.reshape(-1)
        self._tot += np.sum(np.square(pred - act))
        self._count += len(pred)

    def reset_state(self) -> None:
        """Resets the state of Root Mean Squared Error at the end of an epoch."""
        self._count = 0.0
        self._tot = 0.0

    def result(self) -> float:
        """Computes the Root Mean Squared Error over the last epoch."""
        tot = DistributedHelper.allreduce_sum(self._tot)
        count = DistributedHelper.allreduce_sum(self._count)
        if count == 0:
            return clip_metric(np.nan, constants.RMSE)
        return clip_metric(np.sqrt(tot / count), constants.RMSE)
