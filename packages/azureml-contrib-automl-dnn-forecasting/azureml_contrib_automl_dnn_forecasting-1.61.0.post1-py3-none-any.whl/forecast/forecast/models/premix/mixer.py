"""An Mixer-MLP implementation for premixes."""

from __future__ import annotations

import dataclasses as dc

import torch
import torch.nn as nn

from forecast.models.premix.base import AbstractPremix, AbstractPremixConfig


@dc.dataclass
class MixerPremixConfig(AbstractPremixConfig):
    """A config which fully specifies a FutureMixerPremix."""

    input_channels: int
    output_channels: int
    sequence_length: int
    num_layers: int
    dropout: float
    expansion_factor: float = 4

    def create_premix(self) -> MixerPremix:
        """Creates a MixerPremix from the config."""
        return MixerPremix(self)

    def __post_init__(self) -> None:
        """Validates the MixerPremixConfig."""
        super().__post_init__()
        if self.input_channels < 1:
            raise ValueError(f"`input_channels` must be >= 1, was set to {self.input_channels}")
        if self.output_channels < 1:
            raise ValueError(f"`output_channels` must be >= 1, was set to {self.output_channels}")
        if self.sequence_length < 1:
            raise ValueError(f"`sequence_length` must be >= 1, was set to {self.sequence_length}")
        if self.num_layers < 1:
            raise ValueError(f"`num_layers` must be >= 1, was set to {self.num_layers}")
        if self.dropout < 0 or self.dropout >= 1:
            raise ValueError(f"`dropout` must be [0, 1), was set to {self.dropout}")
        if round(self.expansion_factor * self.input_channels) < 1:
            raise ValueError(
                f"Selected value of `expansion_factor` ({self.expansion_factor}) and `input_channels` "
                f"({self.input_channels}) would result in an MLP dimension of < 1."
            )


class MixerPremix(AbstractPremix):
    """Projects the feature dimension to the requested size followed by applying a set of Mixer-like blocks."""

    config: MixerPremixConfig

    def __init__(self, config: MixerPremixConfig):
        """Creates the MixerPremix."""
        super().__init__(config)

        self._lin = nn.Linear(config.input_channels, config.output_channels)
        self._mixer = nn.Sequential(
            *[
                _MixerBlock(
                    config.sequence_length,
                    config.output_channels,
                    expansion_factor=config.expansion_factor,
                    dropout=config.dropout,
                )
                for _ in range(config.num_layers)
            ]
        )

    def forward(self, features: torch.Tensor) -> torch.Tensor:
        """Applies the Mixer to the input features."""
        return self._mixer(self._lin(features.transpose(1, 2))).transpose(1, 2)

    @property
    def output_channels(self) -> int:
        """The number of output channels."""
        return self.config.output_channels

    @property
    def is_future_conditioned(self) -> bool:
        """Not future conditioned."""
        return False

    @property
    def receptive_field(self) -> int:
        """The receptive field is defined as the input sequence length."""
        return self.config.sequence_length


class _MixerBlock(nn.Module):
    def __init__(self, seq_len: int, num_features: int, *, expansion_factor: float, dropout: float):
        super().__init__()
        self._seq_mlp = _MLP(seq_len, expansion_factor, dropout)
        self._seq_ln = nn.LayerNorm(num_features)
        self._chan_mlp = _MLP(num_features, expansion_factor, dropout)
        self._chan_ln = nn.LayerNorm(num_features)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # the mixer module will transpose from (N, C, SL) -> (N, SL, C) before a block receives the tensor
        # therefore, we can follow the implementation as defined in the paper (which assumes the channels are last)
        seq_mixed = self._seq_mlp(self._seq_ln(x).transpose(1, 2)).transpose(1, 2) + x
        return self._chan_mlp(self._chan_ln(seq_mixed)) + seq_mixed


class _MLP(nn.Module):
    def __init__(self, in_features: int, expansion_factor: float, dropout: float):
        super().__init__()
        inter_features = round(in_features * expansion_factor)
        self._op = nn.Sequential(
            nn.Linear(in_features, inter_features),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(inter_features, in_features),
            nn.Dropout(dropout),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self._op(x)
