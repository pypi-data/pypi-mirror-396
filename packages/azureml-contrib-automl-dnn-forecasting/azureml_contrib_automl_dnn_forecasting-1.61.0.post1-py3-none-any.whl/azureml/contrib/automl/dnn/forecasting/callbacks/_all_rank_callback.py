# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from overrides import overrides

from forecast.callbacks.callback import Callback
from forecast.callbacks.utils import CallbackDistributedExecMode


class _AllRankCallback(Callback):

    @staticmethod
    @overrides
    def get_distributed_exec_mode() -> CallbackDistributedExecMode:
        """Get the execution mode of callback."""
        return CallbackDistributedExecMode.ALL
