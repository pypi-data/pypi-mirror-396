# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module for creating a model based on TCN."""
from abc import ABCMeta, abstractmethod
import math
import random
import logging
from typing import List, Optional, Sequence

import dataclasses as dc
from .forecast_wrapper import DNNParams
from ..datasets.timeseries_datasets import EmbeddingColumnInfo
from ..constants import TCNForecastParameters
from forecast.data.sources.data_source import DataSourceConfig
from forecast.models import ForecastingModel
from forecast.models.canned import create_tcn_quantile_forecaster
from forecast.models.backbone.base import MultilevelType
from forecast.models.backbone.cell.residual_tcn_cell import CausalConvResidConfig
from forecast.models.backbone.repeated_cell import RepeatedCellBackboneConfig, RepeatMode
from forecast.models.forecast_head import UnboundedScalarForecastHeadConfig
from forecast.models.premix import EmbeddingConfig, EmbeddingPremixConfig

from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.core.shared.exceptions import ClientException
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (
    TCNEmbeddingInvalidFactor,
    TCNEmbeddingInvalidMultilevel,
    TCNEmbeddingUnsupportCalcType
)
from azureml.contrib.automl.dnn.forecasting.wrapper._distributed_helper import DistributedHelper


logger = logging.getLogger(__name__)


class _EmbeddingDimensionCalcBase(metaclass=ABCMeta):
    """Base class for embedding dimension calculator."""

    @abstractmethod
    def get_embedding_dimension(self, num_distinct_values: int) -> int:
        """
        Get the embedding dimension.

        :param num_distinct_values: The number of distinct values in the index being embedded
        :type: int
        """
        raise NotImplementedError


class _EmbeddingDimensionCalcRoot(_EmbeddingDimensionCalcBase):
    """
    Embedding dimension calculator using n-th root method.

    Embedding dimension for a column x is: dim = #x ^ (1 / embed_factor)
    where #x is the number of distinct values in x.
    """

    def __init__(self, embed_factor: float):
        """
        Create an object for calculating embedding dimension using the root method.

        :param embed_factor: Root to use in the dimension calculation
        :type: float
        """
        self.embed_factor = embed_factor

    @property
    def embed_factor(self) -> int:
        """Root to use when calculating the embedding dimension."""
        return self._embed_factor

    @embed_factor.setter
    def embed_factor(self, factor):
        if factor <= 0:
            raise ClientException._with_error(AzureMLError.create(
                TCNEmbeddingInvalidFactor, target="embed_factor", embed_factor=factor,
                reference_code=ReferenceCodes._TCN_EMBEDDING_INVALID_FACTOR)
            )
        self._embed_factor = factor

    def get_embedding_dimension(self, num_distinct_values: int) -> int:
        """
        Get the embedding dimension using the root method.

        :param num_distinct_values: The number of distinct values in the index being embedded
        :type: int
        """
        target_dim = num_distinct_values ** (1. / self.embed_factor)

        target_dim = min(TCNForecastParameters.MAX_EMBEDDING_DIM, target_dim)
        return math.ceil(max(TCNForecastParameters.MIN_EMBEDDING_DIM, target_dim))


def create_tcn_embedded_forecaster(input_channels: int,
                                   num_cells_per_block: int, multilevel: str,
                                   horizon: int, num_quantiles: int,
                                   num_channels: int, num_blocks: int, dropout_rate: float,
                                   dilation: int, embedding_configs: Sequence[EmbeddingConfig]) -> ForecastingModel:
    """
    Create a tcn model with grain embedding which forecasts the quantiles of a time-varying series.

    :param input_channels: The number of input channels in the data passed to the model
    :type:int

    :param num_cells_per_block: The number of cells per cell block
    :type:int

    :param multilevel: How the output of the backbone is passed to the forecast heads
    (see `MultilevelType` for further details)
    :type:str

    :param horizon: forecast horizon
    :type:int

    :param num_quantiles: number of quantiles predictions to make.
    :type:int

    :param num_channels: The number of channels in the intermediate layers of the model
    :type:int

    :param num_blocks: The depth scale factor (how many cell blocks are created)
    :type:int

    :param dropout_rate: The rate at which dropout is applied
    :type:float

    :param dilation: The dilation of the first TCN cell.
    :type:int

    :param embedding_configs: embedding configuration for each grain column.
    :type:Sequence[EmbeddingConfig]

    :return: a forecaster model.
    :rtype: ForecastingModel
    """
    premix_config = EmbeddingPremixConfig(input_channels=input_channels,
                                          output_channels=num_channels,
                                          embeddings=embedding_configs)

    base_cell = CausalConvResidConfig(num_prev_cell_inputs=1,
                                      kernel_size=2,
                                      dilation=dilation,
                                      stride=1)
    cell_configs = [dc.replace(base_cell, dilation=(2**i) * base_cell.dilation) for i in range(1, num_cells_per_block)]
    cell_configs = [base_cell] + cell_configs

    try:
        ml = MultilevelType[multilevel.upper()]
    except KeyError as e:
        raise ClientException._with_error(AzureMLError.create(
            TCNEmbeddingInvalidMultilevel, target="embed_factor",
            multilevel=multilevel.upper(),
            multi_levels=[m.name for m in MultilevelType],
            reference_code=ReferenceCodes._TCN_EMBEDDING_INVALID_MULTILEVEL)
        ) from e
    backbone_config = RepeatedCellBackboneConfig(cell_configs=cell_configs,
                                                 multilevel=ml.name,
                                                 repeat_mode=RepeatMode.OUTER.name)

    head_configs = [UnboundedScalarForecastHeadConfig(horizon) for _ in range(num_quantiles)]

    return ForecastingModel(premix_config,
                            backbone_config,
                            head_configs)


def get_embedding_dimension_calc(params: DNNParams) -> _EmbeddingDimensionCalcBase:
    """
    Get an object for calculating the embedding dimension.

    :param params:  DNN parameters for the model.
    :type: DNNParams
    """
    embed_calc_type = params.get_value(TCNForecastParameters.EMBEDDING_TARGET_CALC_TYPE,
                                       TCNForecastParameters.EMBEDDING_TARGET_CALC_TYPE_DEFAULT)

    # Only support root calculation type for now
    if embed_calc_type is not TCNForecastParameters.ROOT:
        raise ClientException._with_error(AzureMLError.create(
            TCNEmbeddingUnsupportCalcType, target="embed_calc_type", embed_calc_type=embed_calc_type,
            reference_code=ReferenceCodes._TCN_EMBEDDING_UNSUPPORTED_CALC_TYPE)
        )

    embed_factor = float(params.get_value(TCNForecastParameters.EMBEDDING_ROOT,
                                          TCNForecastParameters.EMBEDDING_ROOT_DEFAULT))
    return _EmbeddingDimensionCalcRoot(embed_factor)


def build_canned_model(params: DNNParams, dset_config: DataSourceConfig, horizon: int, num_quantiles: int,
                       enable_future_regressors: Optional[bool] = False,
                       future_channels: Optional[int] = 0,
                       embedding_column_info: Optional[List[EmbeddingColumnInfo]] = None) -> ForecastingModel:
    """
    Build a model based on config.

    :param params:  DNN parameters for the model.
    :type:DNNParams

    :param dset_config:  configuration for the model.
    :type:DataSourceConfig

    :param horizon: forecast horizon
    :type:int

    :param num_quantiles: number of quantiles predictions to make.
    :type:int

    :param enable_future_regressors: Flag to enable/disable future features for DNN training.
    :type:bool

    :param future_channels: Number of the future input channels.
    :type:int

    :param embedding_column_info: List of each grain column details.
    :type:List[EmbeddingColumnInfo]

    :return: a forecaster model.
    :rtype: ForecastingModel
    """
    if dset_config.encodings:
        input_channels = dset_config.feature_channels + dset_config.forecast_channels +\
            sum(e.num_vals for e in dset_config.encodings) - len(dset_config.encodings)
        if enable_future_regressors:
            future_input_channels = future_channels +\
                sum(e.num_vals for e in dset_config.encodings) - len(dset_config.encodings)
    else:
        input_channels = dset_config.feature_channels + dset_config.forecast_channels
        future_input_channels = future_channels if enable_future_regressors else 0

    future_expansion_factor = params.get_value(TCNForecastParameters.FUTURE_EXPANSION_FACTOR,
                                               TCNForecastParameters.FUTURE_EXPANSION_FACTOR_DEFAULT)
    future_layers = params.get_value(TCNForecastParameters.FUTURE_LAYERS,
                                     TCNForecastParameters.FUTURE_LAYERS_DEFAULT) if enable_future_regressors else 0

    # backbone architecture
    num_cells = params.get_value(TCNForecastParameters.NUM_CELLS, random.randint(3, 6))
    multilevel = params.get_value(TCNForecastParameters.MULTILEVEL, random.choice(list(MultilevelType)).name)

    # model hyper-parameters
    depth = params.get_value(TCNForecastParameters.DEPTH, random.randint(1, 3))
    num_channels = params.get_value(TCNForecastParameters.NUM_CHANNELS, random.choice([64, 128, 256]))
    dropout_rate = params.get_value(TCNForecastParameters.DROPOUT_RATE,
                                    random.choice([0, 0.1, 0.25, 0.4, 0.5]))

    num_cells, multilevel, depth, num_channels, dropout_rate = \
        DistributedHelper.broadcast_from_master_to_all(num_cells, multilevel, depth, num_channels, dropout_rate)

    dilation = params.get_value(TCNForecastParameters.DILATION, TCNForecastParameters.DILATION_DEFAULT)
    logger.info('Model used the following hyperparameters:'
                ' num_cells={}, multilevel={}, depth={}, num_channels={}, dropout_rate={},'
                ' dilation={}, future_input_channels={}, future_layers={},'
                'future_expansion_factor={}'.format(num_cells, multilevel, depth, num_channels, dropout_rate, dilation,
                                                    future_input_channels, future_layers, future_expansion_factor))

    embed_calc_type = params.get_value(TCNForecastParameters.EMBEDDING_TARGET_CALC_TYPE,
                                       TCNForecastParameters.EMBEDDING_TARGET_CALC_TYPE_DEFAULT)
    have_embedding_info = embedding_column_info is not None and len(embedding_column_info) > 0
    if have_embedding_info and embed_calc_type is not TCNForecastParameters.NONE:
        embed_configs = []
        logger.info('Embedding on categorical columns in effect')
        embed_dim_calc = get_embedding_dimension_calc(params)
        for col_info in embedding_column_info:
            embedding_out_dim = embed_dim_calc.get_embedding_dimension(col_info.distinct_values)
            embed_config = EmbeddingConfig(col_info.index, col_info.distinct_values, embedding_out_dim)
            logger.info(f'Embedding dimensions:feature_index={embed_config.feature_index}')
            logger.info(f'Embedding dimensions:input_dim={embed_config.input_dim}')
            logger.info(f'Embedding dimensions:output_dim={embed_config.output_dim}')
            embed_configs.append(embed_config)
        canned_model = create_tcn_quantile_forecaster(input_channels, num_cells, multilevel, horizon,
                                                      num_quantiles, num_channels, depth, dropout_rate,
                                                      init_dilation=dilation, embeddings=embed_configs,
                                                      future_input_channels=future_input_channels,
                                                      future_layers=future_layers,
                                                      future_expansion_factor=future_expansion_factor)
    else:
        canned_model = create_tcn_quantile_forecaster(input_channels, num_cells, multilevel, horizon,
                                                      num_quantiles, num_channels, depth, dropout_rate,
                                                      init_dilation=dilation,
                                                      future_input_channels=future_input_channels,
                                                      future_layers=future_layers,
                                                      future_expansion_factor=future_expansion_factor)
    return canned_model
