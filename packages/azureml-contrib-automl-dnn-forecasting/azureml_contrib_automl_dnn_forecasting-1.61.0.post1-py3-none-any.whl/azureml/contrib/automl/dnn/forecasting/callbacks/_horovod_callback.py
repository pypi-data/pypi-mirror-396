# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
from overrides import overrides
from typing import MutableMapping

from azureml.contrib.automl.dnn.forecasting.callbacks._all_rank_callback import _AllRankCallback

try:
    import horovod.torch as hvd
except ImportError:
    hvd = None


class _HorovodCallback(_AllRankCallback):

    def __init__(self) -> None:
        super().__init__()

    @overrides
    def on_train_begin(self) -> None:
        """Invoked prior to the beginning of training in `model.fit()`."""
        if hvd:
            logging.info(f"Beginning training with {hvd.size()} processes.")
            logging.info(f"Global rank: {hvd.rank()}.")
            logging.info(f"Local rank: {hvd.local_rank()}.")
            logging.info(f"Local size: {hvd.local_size()}.")
        else:
            logging.info("Beginning training without horovod.")

    @overrides
    def on_train_end(self) -> None:
        """Invoked just prior to completion of training in `model.fit()`."""
        logging.info("training ended.")

    @overrides
    def on_train_epoch_begin(self, epoch: int) -> None:
        """Invoked prior to the beginning of an epoch in `model.fit()`."""
        logging.info(f"training epoch {epoch} started.")

    @overrides
    def on_train_epoch_end(self, epoch: int, loss: float, metrics: MutableMapping[str, float]) -> None:
        """Invoked after a training epoch but before a evaluating the validation dataset in `model.fit()`."""
        logging.info(f"training epoch {epoch} ended. loss: {loss} metrics: {metrics}")

    @overrides
    def on_val_begin(self, epoch: int) -> None:
        """Invoked prior to evaluating the val dataset in `model.fit()`."""
        logging.info(f"validation epoch: {epoch} begin.")

    @overrides
    def on_val_end(self, epoch: int, loss: float, metrics: MutableMapping[str, float]) -> None:
        """Invoked after evaluating the val dataset in `model.fit()`."""
        logging.info(f"validation epoch {epoch} ended. loss: {loss} metrics: {metrics}")

    @overrides
    def on_train_val_epoch_end(self, epoch: int) -> None:
        """Invoked after a train/val on an epoch, regardless of whether a val dataset is provided."""
        logging.info(f"training and validation epoch {epoch} ended.")
