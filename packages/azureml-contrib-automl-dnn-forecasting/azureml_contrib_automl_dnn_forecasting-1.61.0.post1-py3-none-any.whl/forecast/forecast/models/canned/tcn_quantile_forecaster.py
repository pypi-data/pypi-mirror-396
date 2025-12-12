"""A simply parameterized model for predicting one or more quantiles of a time-varying series."""

import dataclasses as dc
from typing import Optional, Sequence

from typing_extensions import Literal

from forecast.models import ForecastingModel
from forecast.models.backbone.base import MultilevelType
from forecast.models.backbone.cell.residual_tcn_cell import CausalConvResidConfig
from forecast.models.backbone.repeated_cell import RepeatedCellBackboneConfig, RepeatMode
from forecast.models.forecast_head import StrictlyPositiveScalarForecastHeadConfig, UnboundedScalarForecastHeadConfig
from forecast.models.premix import (
    AbstractPremixConfig,
    ConvPremixConfig,
    EmbeddingConfig,
    EmbeddingPremixConfig,
    FutureConcatPremixConfig,
    MixerPremixConfig,
)


def create_tcn_quantile_forecaster(
    input_channels: int,
    num_cells_per_block: int,
    multilevel: Literal["cell", "cell_list", "none"],
    horizon: int,
    num_quantiles: int,
    num_channels: int,
    num_blocks: int,
    dropout_rate: float,
    *,
    init_dilation: int = 2,
    embeddings: Optional[Sequence[EmbeddingConfig]] = None,
    nonnegative_forecast: bool = False,
    num_convs: int = 2,
    num_pointwise: int = 0,
    future_input_channels: int = 0,
    future_layers: int = 0,
    future_expansion_factor: int = 4,
) -> ForecastingModel:
    """This function creates a simply parameterized model which forecasts the quantiles of a time-varying series.

    Parameters
    ----------
    input_channels: int
        The number of input channels in the data passed to the model
    num_cells_per_block: int
        The number of cells per cell block
    multilevel: str (one of 'cell', 'none', 'cell_list')
        How the output of the backbone is passed to the forecast heads (see `MultilevelType` for further details)
    horizon: int
        The number of samples to forecast
    num_quantiles: int
        The number of quantiles to forecast
    num_channels: int
        The number of channels in the intermediate layers of the model
    num_blocks: int
        The depth scale factor (how many cell blocks are created)
    dropout_rate: float
        The rate at which dropout is applied
    init_dilation: int
        The dilation of the first TCN cell. Defaults to 2.
    embeddings: Sequence[EmbeddingConfig], optional
        Configs specifying how particular features should be embedded, defaults to no embeddings
    nonnegative_forecast: bool, optional
        Should the output heads return nonnegative values (applies a softplus), defaults to False
    num_convs: int, optional
        Number of total convolutions per cell, defaults to 2.
    num_pointwise: int, optional
        Number of pointwise convs in each cell which replace dilated convs, defaults to 0
    future_input_channels: int, optional
        Number of future input channels available to the model, defaults to 0
    future_layers: int, optional
        Depth of the future Mixer premix (only valid if future_input_channels > 0), defaults to 0
    future_expansion_factor: int, optional
        Expansion width of the future Mixer premix, defaults to 4

    Returns
    -------
    ForecastingModel
        A model which outputs a time-varying estimate of the series quantiles

    """
    premix_config: AbstractPremixConfig
    if embeddings is None:
        premix_config = ConvPremixConfig(
            input_channels=input_channels,
            output_channels=num_channels,
            kernel_size=1,
            dilation=1,
            stride=1,
        )
    else:
        premix_config = EmbeddingPremixConfig(input_channels, num_channels, embeddings)

    if future_input_channels >= 1 and future_layers >= 1:
        # set the future_output_channels to be proportional to the number of model channels, rounding to the nearest
        # multiple of 8 for computational efficiency
        # note: this will increase the model width in the backbone beyond num_channels
        future_output_ch = max(round(future_input_channels / input_channels * num_channels / 8) * 8, 8)
        premix_config = FutureConcatPremixConfig(
            past_premix_config=premix_config,
            future_premix_config=MixerPremixConfig(
                input_channels=future_input_channels,
                output_channels=future_output_ch,
                sequence_length=horizon,
                num_layers=future_layers,
                dropout=dropout_rate,
                expansion_factor=future_expansion_factor,
            ),
            reduction_mode="mean",
        )
    elif future_input_channels != 0 or future_layers != 0:
        raise ValueError("Both `future_input_channels` and `future_layers` must be >= 1 to apply a FutureConcatPremix.")

    base_cell = CausalConvResidConfig(
        num_prev_cell_inputs=1,
        kernel_size=2,
        dilation=init_dilation,
        stride=1,
        num_convs=num_convs,
        num_pointwise_convs=num_pointwise,
        dropout=dropout_rate,
    )
    cell_configs = [
        dc.replace(base_cell, dilation=(2**i) * base_cell.dilation) for i in range(1, num_cells_per_block)
    ]
    cell_configs = [base_cell] + cell_configs

    try:
        ml = MultilevelType[multilevel.upper()]
    except KeyError:
        raise ValueError(f"`multilevel` must be one of {[m.name for m in MultilevelType]}")
    backbone_config = RepeatedCellBackboneConfig(
        cell_configs=cell_configs, depth=num_blocks, multilevel=ml.name, repeat_mode=RepeatMode.OUTER.name
    )

    head_type = StrictlyPositiveScalarForecastHeadConfig if nonnegative_forecast else UnboundedScalarForecastHeadConfig
    head_configs = [head_type(horizon, dropout=dropout_rate) for _ in range(num_quantiles)]

    return ForecastingModel(premix_config, backbone_config, head_configs)
