# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Callbacks which computes and uploads metric to run."""
import logging
from typing import MutableMapping, Any, Set, Optional

from overrides import overrides
import numpy as np
from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared.exceptions import ClientException
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.core.shared import logging_utilities
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.runtime.data_transformation import _get_data_snapshot
from azureml.automl.runtime.featurizer.transformer.timeseries.timeseries_transformer import TimeSeriesTransformer
from azureml.contrib.automl.dnn.forecasting.callbacks._run_update_base import RunUpdateCallbackBase
from azureml.automl.core.shared._diagnostics.automl_error_definitions import TCNModelNotConvergent
from azureml.core.run import Run
from azureml.automl.runtime.shared.score.scoring import aggregate_scores
from azureml.automl.runtime.shared.score.constants import (
    FORECASTING_SET, REGRESSION_SET,
    FORECASTING_SCALAR_SET, REGRESSION_SCALAR_SET, FORECASTING_NONSCALAR_SET, REGRESSION_NONSCALAR_SET)

from ..constants import ForecastConstant
from ..datasets.timeseries_datasets import TimeSeriesDataset
from ..datasets.eval_timeseries_datasets import (  # noqa: F401
    AbstractValidationTimeSeriesDataset, ValidationTimeSeriesDatasetFromTrainValid
)
from ..metrics.metrics import compute_metrics_using_evalset, save_metric, compute_aggregate_score
from ..wrapper.forecast_wrapper import DNNForecastWrapper, DNNParams

logger = logging.getLogger(__name__)


class RunUpdateCallback(RunUpdateCallbackBase):
    """Wraps AutoML metric computation and upload in a callback."""

    def __init__(self,
                 model_wrapper: DNNForecastWrapper,
                 run_context: Run,
                 params: DNNParams,
                 featurizer: TimeSeriesTransformer):
        """Initialize callback to compute and upload metric to the run context.

        :param model_wrapper: DNNForecastWrapper Model that is being trained
        :param run_context:AutoML run context to be used for uploading model/metrices
        :param X_valid: X validation data used for computing metrices
        :param y_valid: y validation data used for computing metrices
        :param params: DNNParams
        :param featurizer: Trained featurizer
        """
        super().__init__(model_wrapper, run_context, params)
        self.ds_valid = None
        self._scores = None
        self._samples = None
        self.eval_datsets = None
        self._featurizer = featurizer

    def set_evaluation_dataset(self, ds_train: TimeSeriesDataset,
                               ds_valid: TimeSeriesDataset) -> None:
        """Set the dataset to evaluate the metric.

        :param ds_train: dataset for training
        :param ds_valid: dataset for validation
        """
        self.ds_valid = ds_valid
        if isinstance(ds_valid, AbstractValidationTimeSeriesDataset):
            self.ds_valid = ds_valid
        else:
            self.ds_valid = ValidationTimeSeriesDatasetFromTrainValid(ds_train, ds_valid)

    @overrides
    def on_val_end(self, epoch: int, loss: float, metrics: MutableMapping[str, Any]) -> None:
        """On each val epoch end set to compute scalar metric and upload.

        :param epoch: Current epoch number
        :param loss: current loss
        :param metrics: metrics already computed
        """
        # TODO move this to different Telemetry callback
        self.telemetry_logger.send_usage_telemetry_log(
            prefix_message="[RunId:{}][After DNN Validation epoch {} completed]".format(
                self.automl_run_context.run_id, epoch
            )
        )
        # set the current epoch for unit testing.
        self.params.set_parameter(ForecastConstant.CURRENT_EPOCH, epoch)
        if self._is_validation_data_available():
            scores = self._score_metrics(loss=loss, metrics=FORECASTING_SCALAR_SET | REGRESSION_SCALAR_SET)
            self._validate_loss(loss)
            logger.info("Scores: '{0}'".format(scores))
            self._last_epoch_scores = scores
            if self._exception_count == 0:  # To avoid loading model with bad score for inference.
                save_metric(self.run_context, scores)
            else:
                logger.info(
                    "Skip logging scalar score due to number of exceptions: '{0}'".format(self._exception_count))

    @overrides
    def on_train_end(self) -> None:
        """On train end set to compute nonscalar metric and upload."""
        # TODO move this to different Telemetry callback
        self.telemetry_logger.send_usage_telemetry_log(
            prefix_message="[RunId:{}][After DNN Train completed]".format(
                self.automl_run_context.run_id
            )
        )
        if self._is_validation_data_available():
            # nonscalar metrics must be saved only once to avoid "Resource Conflict" issue
            # and hence we save them separately after the training has ended
            scores = self._score_metrics(metrics=FORECASTING_NONSCALAR_SET | REGRESSION_NONSCALAR_SET)
            logger.info("Scores: '{0}'".format(scores))
            if self._exception_count == 0:  # To avoid loading model with bad score for inference.
                save_metric(self.run_context, scores)
            else:
                logger.info(
                    "Skip logging nonscalar score due to number of exceptions: '{0}'".format(self._exception_count))

    def _validate_loss(self, loss) -> None:
        """Validate loss and metrics for exceptions.

        :param loss: current loss
        :param metrics: current validation metrics
        """
        is_nan = np.isnan(loss) or np.isinf(loss)
        if is_nan:
            self._exception_count += 1
        else:
            self._exception_count = 0
        # Raise exception if the model training is not converging for more than two continuous epochs.
        if self._exception_count > 2:
            raise ClientException._with_error(
                AzureMLError.create(
                    TCNModelNotConvergent, target="loss",
                    reference_code=ReferenceCodes._TCN_MODEL_NOT_CONVERGENT,
                    inner_exception="NaN or Infinite loss for more than 2 continuous epochs.")
            )

    def _score_metrics(
        self,
        loss: Optional[float] = None,
        metrics: Set[str] = FORECASTING_SET | REGRESSION_SET
    ) -> None:
        """Compute metric using the validation set and the model in training.

        :param loss: current loss.
        :param metrics: a set of metrics to compute.
        """
        # Raise exception if the model training is not converging after the first epoch.
        # Metrics calculation error out due to nan or inf predictions from the model
        # due to training not converging. Giving a pass for the first epoch, to see
        # if second epoch succeeds. if second epoch or any later epoch has issue
        # model is saved after the latest epoch and that should not error out on prediction.
        eval_list = np.arange(self.ds_valid.cross_validation) if self.ds_valid.cross_validation else [None]
        if self.ds_valid.cross_validation:
            cv_scores = []
            for i in eval_list:
                eval_set = self.ds_valid.get_eval_dataset(self._featurizer, i)
                data_loader = self.model_wrapper.create_data_loader(eval_set.val_dataset, False, num_workers=0)
                y_pred = self.model_wrapper._predict(data_loader=data_loader).reshape(-1)
                Contract.assert_true(y_pred.shape[0] == eval_set.y_valid.reshape(-1).shape[0],
                                     "invalid predict dimension, y shape {}, pred shape {}, len of reader {}".format
                                     (eval_set.y_valid.reshape(-1).shape[0], y_pred.shape[0],
                                      len(eval_set.val_dataset)),
                                     log_safe=True)
                slice_scores = compute_metrics_using_evalset(eval_set, y_pred, metrics)
                cv_scores.append(slice_scores)
            scores = compute_aggregate_score(cv_scores)
        else:
            eval_set = self.ds_valid.get_eval_dataset(self._featurizer)
            y_pred = self.model_wrapper._predict(self.ds_valid)
            horizon = self.model_wrapper.params.get_value(ForecastConstant.Horizon)
            assert horizon == y_pred.shape[-1], "h={0} y={1}".format(horizon, y_pred.shape)
            scores = compute_metrics_using_evalset(eval_set, y_pred.reshape(-1), metrics)
            # We need to aggregate scores to make sure that all data structures are
            # same as in CV scenario while training for forecasting
            scores = aggregate_scores([scores])
        if loss is not None:
            scores[ForecastConstant.Loss] = loss
        return scores

    @overrides
    def _is_validation_data_available(self) -> bool:
        return self.ds_valid is not None or (self.X_valid is not None and self.y_valid is not None)

    @overrides
    def _get_sample_data_json(self) -> str:
        # create input data json from the first row of sample data
        # this input_data is used by the swagger to infer the input data for aci inference.
        sample_str = "None"
        try:
            if self._samples is None:
                self._samples = self.model_wrapper.raw_data_sample.copy()
            sample_str = _get_data_snapshot(self._samples, is_forecasting=True)
        except Exception as e:
            logger.warning("Failed to create score inference file.")
            logging_utilities.log_traceback(e, logger, is_critical=False)

        return sample_str
