"""A no-op premix and its config."""

from __future__ import annotations

import dataclasses as dc

import torch

from forecast.models.premix.base import AbstractPremix, AbstractPremixConfig


class IdentityPremix(AbstractPremix):
    """A no-op premix."""

    config: IdentityPremixConfig

    def __init__(self, config: IdentityPremixConfig):
        """Creates the no-op premix."""
        super().__init__(config)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """A no-op."""
        return x

    @property
    def receptive_field(self) -> int:
        """A no-op does not increase the receptive field.

        Returns
        -------
        1

        """
        return 1

    @property
    def output_channels(self) -> int:
        """The number of channels in the tensor output from the premix (same as input_channels).

        Returns
        -------
        int

        """
        return self.config.input_channels

    @property
    def is_future_conditioned(self) -> bool:
        """A no-op is not conditioned on future values.

        Returns
        -------
        False

        """
        return False


@dc.dataclass
class IdentityPremixConfig(AbstractPremixConfig):
    """A config for the no-op premix."""

    input_channels: int

    def create_premix(self) -> IdentityPremix:
        """Creates the no-op premix and validates that no change in channel count is requested.

        Returns
        -------
        IdentityPremix

        """
        return IdentityPremix(self)

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.input_channels < 1:
            raise ValueError(f"`input_channels` must be >= 1, was set to {self.input_channels}")
