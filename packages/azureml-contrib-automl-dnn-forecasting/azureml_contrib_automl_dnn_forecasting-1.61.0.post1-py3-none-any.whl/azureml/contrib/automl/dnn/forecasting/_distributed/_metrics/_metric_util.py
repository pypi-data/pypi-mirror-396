# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import numpy as np
from azureml.contrib.automl.dnn.forecasting.metrics.metrics import _get_worst_scores
from azureml.training.tabular.score import _scoring_utilities, constants


def clip_metric(metric_score: float, metric_name: str) -> float:
    """
    Clips the metric score based on valid range for that metric.

    :param metric_score: The score of the metric
    :param metric_name: The name of the metric

    :return: The clipped metric.
    """
    # If the score is negative zero, make it positive zero.
    if metric_score == 0.0:
        metric_score = 0.0
    if np.isnan(metric_score) or np.isinf(metric_score):
        worst_scores = _get_worst_scores([metric_name])
        return worst_scores[metric_name]
    return _scoring_utilities.clip_score(metric_score, *constants.REGRESSION_RANGES[metric_name], metric_name)
