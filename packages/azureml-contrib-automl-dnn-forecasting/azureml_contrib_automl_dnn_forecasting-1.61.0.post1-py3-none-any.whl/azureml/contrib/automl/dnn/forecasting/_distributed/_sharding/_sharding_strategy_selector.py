# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
from typing import Sequence, Optional

from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.contrib.automl.dnn.forecasting._distributed._grain_summary import GrainSummary
from azureml.contrib.automl.dnn.forecasting._distributed._sharding._sharding_strategy_base import _ShardingStrategyBase
from azureml.contrib.automl.dnn.forecasting._distributed._sharding import SHARDING_STRATEGIES

logger = logging.getLogger(__name__)


def get_best_sharding_strategy(
    train_grain_summaries: Sequence[GrainSummary],
    valid_grain_summaries: Sequence[GrainSummary],
    node_count: int,
    lookback: int,
    horizon: int,
    validation_step_size: int,
) -> _ShardingStrategyBase:
    """
    Get the best sharding strategy.

    :param train_grain_summaries: Sequence of grain summaries for the training dataset
    :param valid_grain_summaries: Sequence of grain summaries for the validation dataset
    :param node_count: Number of machines on which the dataset has to be shareded
    :param horizon: Number of time steps to forecast.
    :param lookback: Time step size between consecutive examples.
    :param validation_step_size: The step size for the validation dataset.
    :return: The best sharding strategy.
    """
    Contract.assert_true(
        node_count > 0,
        f"Number of devices ({node_count}) for sharding cannot be less than 0",
        reference_code=ReferenceCodes._TS_NODE_COUNT_NEGATIVE,
        log_safe=True
    )
    strategy_instance: Optional[_ShardingStrategyBase] = None
    for strategy in SHARDING_STRATEGIES:
        try:
            strategy_instance = strategy(
                train_grain_summaries,
                valid_grain_summaries,
                node_count,
                lookback,
                horizon,
                validation_step_size
            )
            break
        except Exception as ex:
            logger.warning(f"Failed to use {strategy_instance.__class__.__name__} sharding strategy {ex}.")
            continue
    Contract.assert_true(
        strategy_instance is not None,
        message="No applicable sharding strategy found.",
        reference_code=ReferenceCodes._TS_SHARDING_STRATEGY_NOT_FOUND,
        log_safe=True)
    logger.info(f"Selected {strategy_instance.__class__.__name__} sharding strategy")
    return strategy_instance
