# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Computes various metrics evaluating forecasting model performance."""

from typing import Mapping, Sequence, Tuple
from forecast.metrics import MetricMode

from azureml.contrib.automl.dnn.forecasting._distributed._metrics._rmse import RMSE
from azureml.contrib.automl.dnn.forecasting._distributed._metrics._nrmse import NRMSE
from azureml.contrib.automl.dnn.forecasting._distributed._metrics._mae import MAE
from azureml.contrib.automl.dnn.forecasting._distributed._metrics._rmsle import RMSLE
from azureml.contrib.automl.dnn.forecasting._distributed._metrics._mape import MAPE
from azureml.contrib.automl.dnn.forecasting._distributed._metrics._nmae import NMAE
from azureml.contrib.automl.dnn.forecasting._distributed._metrics._nrmsle import NRMSLE
from azureml.contrib.automl.dnn.forecasting._distributed._metrics._r2_score import R2Score
from azureml.contrib.automl.dnn.forecasting._distributed._metrics._explained_variance import ExplainedVariance
from azureml.contrib.automl.dnn.forecasting.constants import ForecastConstant
from azureml.training.tabular.score import constants


def get_supported_metrics_for_distributed_forecasting(
    grain_map: Mapping[Tuple, int],
    numericalized_grain_cols: Sequence[int],
    y_min: Sequence[float],
    y_max: Sequence[float],
):
    """Get metrices supported for distributed DNN Forecasting models.

    :param grain_map: A mapping of numericalized grain cols to grain index.
    :param numericalized_grain_cols: Sequence of numericalized grain columns.
    :param y_min: Sequence of y_min for each grain.
    :param y_max: Sequence of y_max for each grain.
    :return: A dictionary mapping metric name to metric object.
    """
    mode = MetricMode.VAL
    index = ForecastConstant.MEDIAN_PREDICTION_INDEX
    return {
        constants.RMSE: RMSE(index, mode),
        constants.RMSLE: RMSLE(index, mode),
        constants.MAPE: MAPE(index, mode),
        constants.MEAN_ABS_ERROR: MAE(index, mode),
        constants.R2_SCORE: R2Score(index, mode),
        constants.EXPLAINED_VARIANCE: ExplainedVariance(index, mode),
        constants.NORM_RMSE: NRMSE(index, mode, grain_map, numericalized_grain_cols, y_min, y_max),
        constants.NORM_MEAN_ABS_ERROR: NMAE(index, mode, grain_map, numericalized_grain_cols, y_min, y_max),
        constants.NORM_RMSLE: NRMSLE(index, mode, grain_map, numericalized_grain_cols, y_min, y_max),
    }
