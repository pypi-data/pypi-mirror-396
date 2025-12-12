"""A premix which concatenates a past premix's output with the reduction of a future premix's output."""

from __future__ import annotations

import dataclasses as dc

import torch

from forecast.models.premix.base import AbstractPremix, AbstractPremixConfig

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal


@dc.dataclass
class FutureConcatPremixConfig(AbstractPremixConfig):
    """A config which fully specifies a FutureMixerPremix."""

    past_premix_config: AbstractPremixConfig
    future_premix_config: AbstractPremixConfig
    reduction_mode: Literal["mean", "max"]

    def create_premix(self) -> FutureConcatPremix:
        """Creates a FutureConcatPremix from the config."""
        return FutureConcatPremix(self)

    def __post_init__(self) -> None:
        """Validates the premix config."""
        super().__post_init__()
        if self.reduction_mode not in ["mean", "max"]:
            raise ValueError(f"Unknown reduction mode `{self.reduction_mode}`")


class FutureConcatPremix(AbstractPremix):
    """A premix which pools, repeats, & concatenates future features with past ones prior to the backbone.

    To match sequence length, after the premix is applied to the future correlates, the result is reduced over the
    sequence length via the format specified in the config. It is then broadcast along the sequence length to match the
    forecast window of the model.
    """

    config: FutureConcatPremixConfig

    def __init__(self, config: FutureConcatPremixConfig):
        """Creates a FutureConcatPremix."""
        super().__init__(config)

        self._past_premix = config.past_premix_config.create_premix()
        self._future_premix = config.future_premix_config.create_premix()

        rmode = config.reduction_mode.lower()
        if rmode == "mean":
            self._reduction = lambda x: torch.mean(x, dim=2, keepdim=True)
        elif rmode == "max":
            self._reduction = lambda x: torch.max(x, dim=2, keepdim=True)[0]
        else:
            raise ValueError(f"Unknown reduction mode `{config.reduction_mode}`")

    def forward(self, past_features: torch.Tensor, future_features: torch.Tensor) -> torch.Tensor:
        """Applies the two premixes to the past and future features and reduces/concats the two together."""
        past_out = self._past_premix(past_features)
        future_out = self._future_premix(future_features)

        # concat the reduced future features with the past
        return torch.cat([past_out, self._reduction(future_out).repeat(1, 1, past_out.shape[-1])], dim=1)

    @property
    def output_channels(self) -> int:
        """The number of output channels of the combined premix."""
        return self._past_premix.output_channels + self._future_premix.output_channels

    @property
    def is_future_conditioned(self) -> bool:
        """The premix requires future data."""
        return True

    @property
    def receptive_field(self) -> int:
        """The receptive field of the premix is defined by the past feature premix."""
        return self._past_premix.receptive_field
