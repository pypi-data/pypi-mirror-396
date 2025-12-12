# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Contains sharding modules for AutoML DNN forecasting package."""
from typing import List, Type
from azureml.contrib.automl.dnn.forecasting._distributed._sharding._equal_samples_sharding_strategy import \
    _EqualSamplesShardingStrategy
from azureml.contrib.automl.dnn.forecasting._distributed._sharding._sharding_strategy_base import _ShardingStrategyBase

# Here, we have a list of sharding strategies. Any new strategy should be put
# in the order where best strategy is on top and worst on the bottom.
SHARDING_STRATEGIES: List[Type[_ShardingStrategyBase]] = [
    _EqualSamplesShardingStrategy
]
