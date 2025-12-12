"""A head (and its config) which forecasts strictly positive values by applying a softplus after a linear layer."""

from __future__ import annotations

import dataclasses as dc

import torch
import torch.nn as nn

from forecast.models.forecast_head.base import AbstractForecastHead, AbstractForecastHeadConfig


class StrictlyPositiveScalarForecastHead(AbstractForecastHead):
    """A head which forecasts a strictly positive scalar value by applying a softplus after a linear layer.

    Stricly positive values are commonly required for probabilistic forecasting (e.g., forecasting the standard
    deviation of a normal distribution over time).
    """

    def __init__(self, config: StrictlyPositiveScalarForecastHeadConfig, input_channels: int):
        """Creates a `StrictlyPositiveScalarForecastHead`.

        Parameters
        ----------
        config: StrictlyPositiveScalarForecastHeadConfig
            The config specifying the head's architecture
        input_channels: int
            The number of channels of the input to the layer

        """
        super().__init__(config)

        self._dropout = nn.Dropout(config.dropout) if config.dropout > 0 else nn.Identity()
        self._linear = nn.Linear(input_channels, config.horizon)
        self._linear.weight.data.normal_(0, 0.01)
        self._op = nn.Sequential(self._dropout, self._linear, nn.Softplus())

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Applies the forecast head to the provided Tensor.

        Parameters
        ----------
        x: torch.Tensor
            The input to the forecast head

        Returns
        -------
        torch.Tensor
            The prediction made by the forecast head

        """
        return self._op(x)

    @property
    def receptive_field(self) -> int:
        """The receptive field of the forecast head.

        Returns
        -------
        1

        """
        return 1

    @property
    def is_future_conditioned(self) -> bool:
        """This forecast head is not conditioned on future values.

        Returns
        -------
        False

        """
        return False


@dc.dataclass
class StrictlyPositiveScalarForecastHeadConfig(AbstractForecastHeadConfig):
    """The config for the `StrictlyPositiveScalarForecastHead`."""

    dropout: float

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.dropout < 0 or self.dropout >= 1:
            raise ValueError("`dropout` must be in the range of [0, 1).")

    def create_head(self, input_channels: int) -> StrictlyPositiveScalarForecastHead:
        """Creates a `StrictlyPositiveScalarForecastHead`.

        Parameters
        ----------
        input_channels: int
            The number of channels passed to the head.

        Returns
        -------
        StrictlyPositiveScalarForecastHead
            A `StrictlyPositiveScalarForecastHead` configured according to the specs provided.

        """
        if input_channels <= 0:
            raise ValueError("`input_channels` must be > 0")
        return StrictlyPositiveScalarForecastHead(self, input_channels)
