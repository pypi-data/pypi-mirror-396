# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import MutableMapping
from overrides import overrides

import torch

from azureml.contrib.automl.dnn.forecasting.callbacks._all_rank_callback import _AllRankCallback
from forecast.distributed import Communicator


GLOBAL_TRAIN_LOSS = "train_loss"
GLOBAL_VAL_LOSS = "valid_loss"


class LossCallback(_AllRankCallback):
    """Calculates global loss using losses from all machines and makes them available using metrics."""

    def __init__(self) -> None:
        super().__init__()
        # Saving training loss so that we can make it available in the validation metrics as well.
        self.train_loss = None

    @overrides
    def on_train_epoch_end(self, epoch: int, loss: float, metrics: MutableMapping[str, float]) -> None:
        """Invoked after a training epoch but before a evaluating the validation dataset in `model.fit()`."""
        loss = _average_loss(loss, self.communicator)
        metrics[GLOBAL_TRAIN_LOSS] = loss
        self.train_loss = loss

    @overrides
    def on_val_end(self, epoch: int, loss: float, metrics: MutableMapping[str, float]) -> None:
        """Invoked after evaluating the val dataset in `model.fit()`."""
        loss = _average_loss(loss, self.communicator)
        metrics[GLOBAL_VAL_LOSS] = loss
        metrics[GLOBAL_TRAIN_LOSS] = self.train_loss


def _average_loss(loss: float, comm: Communicator) -> float:
    """Returns the average loss using local loss on all machines."""
    t = torch.tensor([loss], dtype=torch.float32)
    with torch.no_grad():
        loss = comm.allreduce(t)
    return loss.item()
