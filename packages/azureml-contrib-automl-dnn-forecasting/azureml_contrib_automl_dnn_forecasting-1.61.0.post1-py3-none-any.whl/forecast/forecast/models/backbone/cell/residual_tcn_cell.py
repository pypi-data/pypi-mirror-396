"""A residual cell (and its config) with a user-configurable number of casual convolutions."""

from __future__ import annotations

import dataclasses as dc
import itertools
from typing import cast, List, Sequence

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing_extensions import Literal

from forecast.models.backbone.cell.base import AbstractCell, AbstractCellConfig, CellInputs, NullCell
from forecast.models.common.ops import CausalConv1d, Dropout, LayerNorm2ndDim


def _order_uneven_iterables(*iterables: Sequence) -> Sequence:
    # https://stackoverflow.com/questions/19293481/how-to-elegantly-interleave-two-lists-of-uneven-length-in-python
    #
    # this generates weights based on sequence length, attaches them to elements, and then sorts by weight
    # since the sort is stable, two lists of the same length will alternate, with elements of the first list drawn first
    return [
        item[1]
        for item in sorted(
            itertools.chain.from_iterable(
                zip(itertools.count(start=1.0 / (len(seq) + 1), step=1.0 / (len(seq) + 1)), seq) for seq in iterables
            )
        )
    ]


class CausalConvResidCell(AbstractCell):
    """A residual cell with a configurable number of internal causal convolutions.

    Attributes:
    -----------
    config: CausalConvResidCellConfig
        The configuration specifying the properties of the cell's convolutions (dilation, count, etc)
    channels: int
        The number of channels the cell should expect as both input and output
    dropout_rate: float
        The rate at which dropout should be applied within the cell

    """

    def __init__(self, config: CausalConvResidConfig, input_channels: int, prev_cells: CellInputs):
        """Creates a residual casual convolution cell.

        Parameters
        ----------
        config: CausalConvResidConfig
            The configuration specifying the properties of the cell's convolutions (dilation, count, etc)
        input_channels: int
            The number of channels the cell should expect as input and also output
        prev_cells: Sequence[AbstractCell] or AbstractCell
            A single abstract cell (either in a list or as itself); used for computing the cell's receptive field

        """
        super().__init__(config)

        if isinstance(prev_cells, Sequence):
            assert len(prev_cells) == 1, "prev_cells must be of length 1 for `CausalConvResidCell`"
            prev_cell = prev_cells[0]
        else:
            prev_cell = prev_cells

        self.channels = input_channels
        self.dropout_rate = config.dropout

        self._output_norm: nn.Module
        if config.output_norm == "none":
            self._output_norm = nn.Identity()
        elif config.output_norm == "batch_norm":
            self._output_norm = nn.BatchNorm1d(input_channels)
        elif config.output_norm == "layer_norm":
            self._output_norm = LayerNorm2ndDim(input_channels)
        else:
            raise ValueError(f"Unknown output_norm type {config.output_norm}")

        # create our ops
        conv_reg = [
            CausalConv1d(
                input_channels,
                input_channels,
                config.kernel_size,
                config.dilation,
                config.stride,
                use_wn=config.op_norm == "weight_norm",
                bias=config.op_norm != "batch_norm",
            )
            for _ in range(config.num_convs - config.num_pointwise_convs)
        ]
        conv_ptwise = [
            CausalConv1d(
                input_channels,
                input_channels,
                1,
                use_wn=config.op_norm == "weight_norm",
                bias=config.op_norm != "batch_norm",
            )
            for _ in range(config.num_pointwise_convs)
        ]
        convs = _order_uneven_iterables(conv_ptwise, conv_reg)
        ops = []
        for c in convs:
            ops.append(c)

            if config.op_norm == "batch_norm":
                ops.append(nn.BatchNorm1d(input_channels))
            elif config.op_norm == "layer_norm":
                ops.append(LayerNorm2ndDim(input_channels))
            elif config.op_norm != "weight_norm":
                raise ValueError(f"Unknown op_norm type {config.op_norm}")

            if self.dropout_rate > 0:
                ops.append(Dropout(self.dropout_rate))
            ops.append(nn.ReLU())

        self._ops = nn.Sequential(*ops)
        self._receptive_field = sum(c.receptive_field for c in self._ops if isinstance(c, CausalConv1d)) - (
            config.num_convs - 1
        )
        if not isinstance(prev_cell, NullCell):
            self._receptive_field += prev_cell.receptive_field - 1

    def forward(self, x: List[torch.Tensor]) -> torch.Tensor:
        """Applies the cell to the input tensor.

        Parameters
        ----------
        x: List[torch.Tensor]
            A list of length 1 whose tensor will be transformed by the cell

        Returns
        -------
        torch.Tensor
            The tensor that results from transforming the input tensor by this cell

        """
        assert len(x) == 1
        x0 = x[0]
        out = self._ops(x0)

        config = cast(CausalConvResidConfig, self.config)
        if config.output_relu:
            return self._output_norm(F.relu(out + x0))
        else:
            return self._output_norm(out + x0)

    @property
    def receptive_field(self) -> int:
        """The receptive field of this cell starting at the root of the backbone.

        Returns
        -------
        int
            The receptive field

        """
        return self._receptive_field

    @property
    def is_future_conditioned(self) -> bool:
        """A residual causal convolution cell is not conditioned upon future input.

        Returns
        -------
        False

        """
        return False


@dc.dataclass
class CausalConvResidConfig(AbstractCellConfig):
    """Config for a `CausalConvResidCell`."""

    kernel_size: int
    dilation: int
    stride: int
    num_convs: int = 2
    num_pointwise_convs: int = 0
    op_norm: Literal["weight_norm", "batch_norm", "layer_norm"] = "weight_norm"
    dropout: float = 0
    output_relu: bool = False
    output_norm: Literal["none", "batch_norm", "layer_norm"] = "none"

    def create_cell(self, input_channels: int, prev_cells: CellInputs) -> CausalConvResidCell:
        """Instantiates a cell based on the specified config.

        Parameters
        ----------
        input_channels: int
            The number of channels the cell should expect as input and also output
        prev_cells: Sequence[AbstractCell] or AbstractCell
            A single abstract cell (either in a list or as itself); used for computing the cell's receptive field

        Returns
        -------
        CausalConvResidCell
            A cell matching the desired specifications

        """
        return CausalConvResidCell(self, input_channels, prev_cells)

    def __post_init__(self) -> None:
        """Validates the cell's config."""
        super().__post_init__()
        if self.kernel_size < 1:
            raise ValueError("`kernel_size` must be >= 1")
        if self.stride < 1:
            raise ValueError("`stride` must be >= 1")
        if self.dilation < 1:
            raise ValueError("`dilation` must be >= 1")
        if self.num_convs < 1:
            raise ValueError("`num_convs` must be >= 1")
        if self.num_prev_cell_inputs != 1:
            raise ValueError("`num_prev_cell_inputs` must be 1 for class `CausalConvResidConfig`")
        if self.num_pointwise_convs < 0 or self.num_pointwise_convs > self.num_convs:
            raise ValueError("`num_pointwise_convs` must be in range [0, num_convs]")
        if self.dropout < 0 or self.dropout >= 1:
            raise ValueError("`dropout_rate` must be between 0 and 1")
