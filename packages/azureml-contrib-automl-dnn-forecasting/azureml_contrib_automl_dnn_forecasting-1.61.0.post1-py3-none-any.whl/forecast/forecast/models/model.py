"""This module implements the basic functionality of a forecasting model."""

import copy
import dataclasses as dc
import json
from typing import Dict, List, Optional, Sequence

import torch
import torch.nn as nn

import forecast.models.backbone.base as backbone
import forecast.models.common.module as module
import forecast.models.forecast_head as head
import forecast.models.premix as premix


class ForecastingModel(module.StatefulModule):
    """Class which composes a premixer, backbone, and list of heads to forecast the evolution of a time series.

    Attributes:
    -----------
    premix_config: AbstractPremixConfig
        The configuration specifying the structure of the premixer (up to output width)
    backbone_config: AbstractBackboneConfig
        The configuration specifying the structure of the backbone (up to initial width, depth multiplier, and
        dropout_rate)
    head_configs: Sequence[AbstractForecastHead]
        A list of configurations specifying the structure of the forecast outputs (up to input width and dropout rate)

    """

    _PREMIX_KEY = "premix"
    _BACKBONE_KEY = "backbone"
    _FORECAST_HEADS_KEY = "heads"

    def __init__(
        self,
        premix_config: premix.AbstractPremixConfig,
        backbone_config: backbone.AbstractBackboneConfig,
        head_configs: Sequence[head.AbstractForecastHeadConfig],
    ):
        """Creates a forecaster whose structure is determined by configs and whose scale is determined by scalars.

        Parameters
        ----------
        premix_config: AbstractPremixConfig
            The configuration specifying the structure of the premixer (up to output width)
        backbone_config: AbstractBackboneConfig
            The configuration specifying the structure of the backbone (up to initial width, depth multiplier, and
            dropout rate)
        head_configs: Sequence[AbstractForecastHeadConfig]
            A list of configurations specifying the structure of the forecast outputs (up to input width and dropout
            rate)

        """
        super().__init__()

        self.premix_config = copy.deepcopy(premix_config)
        self._premix = self.premix_config.create_premix()

        self.backbone_config = copy.deepcopy(backbone_config)
        self._backbone = self.backbone_config.create_backbone(self._premix.output_channels)

        self.head_configs = copy.deepcopy(head_configs)
        self._heads = nn.ModuleList([h.create_head(self._backbone.output_channels) for h in self.head_configs])

        self._stateful_submodules = self._get_stateful_submodules()

    def forward(self, state: torch.Tensor, future_state: Optional[torch.Tensor] = None) -> List[torch.Tensor]:
        """Forecasts upcoming time-series values based on the state vector `x`.

        Parameters
        ----------
        state: torch.Tensor
            The observed state prior to forecasting
        future_state: torch.Tensor, optional
            The future state during the forecasting period

        Returns
        -------
        List[torch.Tensor]
            A list of torch tensors representing the distribution of the forecasted state.

        """
        if self.is_future_conditioned and future_state is None:
            raise ValueError("Model is conditioned on future state however none was provided.")
        elif not self.is_future_conditioned and future_state is not None:
            raise ValueError("Model is not conditioned on future state however it was provided.")

        # premix first
        if self._premix.is_future_conditioned:
            out = self._premix(state, future_state)
        else:
            out = self._premix(state)

        # apply the backbone
        if self._backbone.is_future_conditioned:
            out = self._backbone(out, future_state)
        else:
            out = self._backbone(out)

        # apply the heads
        return [h(out, future_state) if h.is_future_conditioned else h(out) for h in self._heads]

    @property
    def receptive_field(self) -> int:
        """Returns the receptive field of the model.

        Returns
        -------
        int
            The receptive field of the model

        """
        return (
            max(h.receptive_field for h in self._heads)
            + self._backbone.receptive_field
            + self._premix.receptive_field
            - 2
        )

    @property
    def is_future_conditioned(self) -> bool:
        """Is the model conditioned on values from the time period in which it is forecasting.

        Returns
        -------
        bool

        """
        return (
            self._premix.is_future_conditioned
            or self._backbone.is_future_conditioned
            or any(h.is_future_conditioned for h in self._heads)
        )

    def to_json(self, filename: str) -> None:
        """Serialize the model architecture, but not weights, to disk (JSON).

        Parameters
        ----------
        filename: str
            The path of the file which will be written.

        Returns
        -------
        None

        """
        d = {
            ForecastingModel._PREMIX_KEY: dc.asdict(self.premix_config),
            ForecastingModel._BACKBONE_KEY: dc.asdict(self.backbone_config),
            ForecastingModel._FORECAST_HEADS_KEY: [dc.asdict(h) for h in self.head_configs],
        }
        with open(filename, "w") as f:
            json.dump(d, f)

    def _get_stateful_submodules(self) -> Dict[str, module.StatefulModule]:
        return {n: m for n, m in self.named_modules() if n and isinstance(m, module.StatefulModule)}

    def export_state(self) -> dict:
        """Exports the state of any `StatefulModule`s (non-`StatefulModule`s return `None`).

        Returns
        -------
        dict

        """
        return {n: m.export_state() for n, m in self._stateful_submodules.items()}

    def import_state(self, state: dict) -> None:
        """Imports the state from `state` into the model's `StatefulModule`s.

        Parameters
        ----------
        state: dict
            A mapping from component name to state

        Returns
        -------
        None

        """
        for n, m_state in state.items():
            self.get_submodule(n).import_state(m_state)

    def reset_state(self) -> None:
        """Resets the state of any `StatefulModule`s in the model.

        Returns:
        --------
        None

        """
        for m in self._stateful_submodules.values():
            m.reset_state()

    def retain_state(self, retain: bool) -> None:
        """Allows the caller to signal that contained modules should begin/end retaining state."""
        for m in self._stateful_submodules.values():
            m.retain_state(retain)
