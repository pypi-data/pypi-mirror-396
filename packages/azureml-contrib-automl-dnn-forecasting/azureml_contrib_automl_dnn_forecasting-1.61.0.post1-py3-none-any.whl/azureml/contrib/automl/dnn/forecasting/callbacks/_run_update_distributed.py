# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Callbacks which uploads metric and model to run."""
import logging
from typing import MutableMapping, Any

from overrides import overrides
import numpy as np
from azureml.automl.core.shared.exceptions import ClientException
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.core.shared._diagnostics.automl_error_definitions import TCNModelNotConvergent
from azureml.core.run import Run
from azureml.contrib.automl.dnn.forecasting.constants import ForecastConstant
from azureml.contrib.automl.dnn.forecasting.callbacks._global_loss_callback import GLOBAL_VAL_LOSS
from azureml.contrib.automl.dnn.forecasting.callbacks._run_update_base import RunUpdateCallbackBase
from azureml.contrib.automl.dnn.forecasting.metrics.metrics import save_metric
from azureml.contrib.automl.dnn.forecasting.wrapper.forecast_wrapper import DNNForecastWrapper, DNNParams
from azureml._common._error_definition import AzureMLError
logger = logging.getLogger(__name__)


class DistributedRunUpdateCallback(RunUpdateCallbackBase):
    """Wraps AutoML metric and model upload in a callback."""

    def __init__(self,
                 model_wrapper: DNNForecastWrapper,
                 run_context: Run,
                 params: DNNParams):
        """Initialize callback to upload metric and model to the run context.

        :param model_wrapper: DNNForecastWrapper Model that is being trained
        :param run_context: AutoML run context to be used for uploading model/metrices
        :param params: DNNParams
        """
        super().__init__(model_wrapper, run_context, params)

    @overrides
    def on_val_end(self, epoch: int, loss: float, metrics: MutableMapping[str, Any]) -> None:
        """On each validation epoch end upload metrics.

        :param epoch: Current epoch number
        :param loss: current loss
        :param metrics: metrics already computed
        """
        if self.forecaster.distribution_strategy.rank() == 0:
            self.telemetry_logger.send_usage_telemetry_log(
                prefix_message="[RunId:{}][After DNN Validation epoch {} completed]".format(
                    self.automl_run_context.run_id, epoch
                )
            )
            # set the current epoch for unit testing.
            self.params.set_parameter(ForecastConstant.CURRENT_EPOCH, epoch)
            scores = self._validate_loss_and_metrics(loss=metrics[GLOBAL_VAL_LOSS], metrics=metrics)
            logger.info("Scores: '{0}'".format(scores))
            self._last_epoch_scores = scores
            if self._exception_count == 0:  # To avoid loading model with bad score for inference.
                save_metric(self.run_context, scores)
            else:
                logger.info("Skip logging score due to number of exceptions: '{0}'".format(self._exception_count))

    def _validate_loss_and_metrics(self, loss: float, metrics: MutableMapping[str, Any]) -> None:
        """Validate loss and metrics for exceptions.

        :param loss: current loss
        :param metrics: current validation metrics
        """
        exception_raised = False

        scores = metrics.copy()
        scores[ForecastConstant.Loss] = loss
        exception_raised = np.isnan(loss) or np.isinf(loss)
        if exception_raised:
            self._exception_count += 1
        else:
            self._exception_count = 0
        # Raise exception if the model training is not converging for more than two continuous epochs.
        if self._exception_count > 2:
            raise ClientException._with_error(
                AzureMLError.create(
                    TCNModelNotConvergent, target="loss",
                    reference_code=ReferenceCodes._TCN_MODEL_NON_CONVERGENT_DISTRIBUTED,
                    inner_exception="NaN or Infinite loss for 2 continuous epochs.")
            )
        return scores

    @overrides
    def _is_validation_data_available(self) -> bool:
        # For distributed TCN, we will always have a validation dataset.
        return True

    @overrides
    def _get_sample_data_json(self) -> str:
        # create input data json from the first row of sample data
        # this input_data is used by the swagger to infer the input data for aci inference.
        return self.model_wrapper.raw_data_sample
