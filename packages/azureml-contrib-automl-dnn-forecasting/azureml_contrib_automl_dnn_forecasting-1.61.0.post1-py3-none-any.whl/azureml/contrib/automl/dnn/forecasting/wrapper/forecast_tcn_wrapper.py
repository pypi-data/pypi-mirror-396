# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module for creating a model based on TCN."""
import argparse
import math
import os
import sys
import logging
from typing import Any, Union, cast, Dict, List, Optional, Sequence, Tuple
import numpy as np
import pandas as pd
import torch
import time

from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared.reference_codes import ReferenceCodes
import azureml.automl.runtime.featurizer.transformer.timeseries as automl_transformer
from azureml.automl.runtime.shared.model_wrappers import ForecastingPipelineWrapper
from azureml.automl.core.shared.constants import TimeSeries, TimeSeriesInternal, MLTableDataLabel
from azureml.automl.core.shared.exceptions import ClientException
from azureml.automl.core.shared.limit_function_call_exceptions import TimeoutException
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (
    ExperimentTimedOut,
    IterationTimedOut,
    TCNWrapperRuntimeError,
    TCNWrapperDeadlockError)
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.runtime.experiment_store import ExperimentStore
from azureml.automl.runtime.featurizer.transformer.timeseries.timeseries_transformer import TimeSeriesTransformer
from azureml.contrib.automl.dnn.forecasting.callbacks._horovod_callback import _HorovodCallback
from azureml.contrib.automl.dnn.forecasting.callbacks._global_loss_callback import LossCallback
from azureml.contrib.automl.dnn.forecasting.datasets._timeseries_dataset_config import \
    TimeseriesDatasetConfig, get_dataset_config
from azureml.contrib.automl.dnn.forecasting.datasets._timeseries_numpy_dataset import TimeSeriesNumpyDataset
from azureml.contrib.automl.dnn.forecasting._distributed._metrics._supported_metrics import (
    get_supported_metrics_for_distributed_forecasting
)
from azureml.contrib.automl.dnn.forecasting._distributed._distributed_util import (
    get_grain_summary,
    get_column_names,
    get_dataset_future_features,
    load_datasets,
    log_warning_for_gaps_in_train_val_dataset
)
from azureml.contrib.automl.dnn.forecasting._distributed._data_for_inference import \
    get_lookback_data_for_inference_from_partitioned_datasets
from azureml.contrib.automl.dnn.forecasting.callbacks._run_update_distributed import \
    DistributedRunUpdateCallback
from azureml.contrib.automl.dnn.forecasting.callbacks._global_loss_callback import GLOBAL_VAL_LOSS
from azureml.contrib.automl.dnn.forecasting.wrapper._distributed_helper import DistributedHelper
from azureml.contrib.automl.dnn.forecasting.wrapper import _wrapper_util
from azureml.core.run import Run
from azureml.data import TabularDataset
from azureml.train.automl._azureautomlsettings import AzureAutoMLSettings
from azureml.train.hyperdrive.run import HyperDriveRun
import azureml.automl.core   # noqa: F401
from torch.utils.data.dataloader import DataLoader
from ._wrapper_util import log_transform
from .forecast_wrapper import DNNForecastWrapper, DNNParams
from .tcn_model_utl import build_canned_model
from ..constants import (
    ForecastConstant,
    TCNForecastParameters,
    PROCESSES_SYNC_TIMEOUT_SEC,
    PROCESSES_SYNC_FAIL,
    PAUSE_EXECUTION_SEC
)
from ..callbacks.run_update import RunUpdateCallback

from ..datasets.timeseries_datasets import TimeSeriesDataset
from ..datasets.timeseries_datasets_utils import create_timeseries_datasets, DNNTimeseriesDatasets
from ..metrics.primary_metrics import get_supported_metrics
from ..types import DataInputType
from forecast.callbacks.optimizer import (  # noqa: F401
    EarlyStoppingCallback, ReduceLROnPlateauCallback,
    PreemptTimeLimitCallback
)
from forecast.data.batch_transforms import (
    BatchFeatureTransform,
    BatchSubtractOffset,
    FeatureTransform,
    GenericBatchTransform,
)
from forecast.data.sources.data_source import DataSourceConfig
from forecast.forecaster import Forecaster
from forecast.losses import QuantileLoss
from forecast.models import ForecastingModel
from forecast.utils import create_timestamped_dir

from forecast.data.batch_transforms import BatchNormalizer,\
    Normalizer, NormalizationMode
from azureml.automl.runtime.shared.forecasting_utils import get_pipeline_step
from scipy.interpolate import PchipInterpolator
from scipy.special import erfinv
from azureml.automl.core.shared.exceptions import ValidationException
from azureml.automl.core.shared._diagnostics.automl_error_definitions import QuantileRange

logger = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stderr)
handler.setLevel(logging.INFO)
logger.addHandler(handler)

# If the remaining time is less than a minute, we will
# raise the timeout exception.
REMAINING_TIME_TOLERANCE = pd.Timedelta(minutes=1)


class ForecastTCNWrapper(DNNForecastWrapper):
    """Wrapper for TCN model adapted to work with automl Forecast Training."""

    required_params = [ForecastConstant.Learning_rate, ForecastConstant.Lookback,
                       ForecastConstant.Batch_size, ForecastConstant.num_epochs, ForecastConstant.Loss,
                       ForecastConstant.Device, ForecastConstant.primary_metric]
    loss = QuantileLoss(ForecastConstant.QUANTILES)
    default_params = {ForecastConstant.Loss: loss,  # torch.distributions.StudentT,
                      ForecastConstant.Device: 'cuda' if torch.cuda.is_available() else 'cpu'}
    # configure our loss function

    # _modules, _parameters and _buffers are needed for torch.nn.Module
    _modules = {}
    _parameters = {}
    _buffers = {}

    # Static fields, used by indexer function.
    _s_numericalized_grain_cols: List[int] = []
    _s_grain_map: Dict[Tuple[np.number], int] = {}

    def __init__(self, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Construct the new instance of ForecastTCNWrapper."""
        super().__init__(metadata)
        self._numericalized_grain_cols: List[int] = []
        self._grain_map: Dict[Tuple[np.number], int] = {}
        self._quantiles: List[float] = [0.5]
        self._target_quantile = 0.5  # attribute to loop over the set of quantiles

    def _set_static_fields(self) -> None:
        """Set the static fields on the ForecastTCNWrapper."""
        # Set these fields to static fields.
        # They will not be stored after pickling.
        ForecastTCNWrapper._s_numericalized_grain_cols = self._numericalized_grain_cols
        ForecastTCNWrapper._s_grain_map = self._grain_map

    def train_model(self, n_epochs: int, X: DataInputType = None, y: DataInputType = None,
                    X_train: DataInputType = None, y_train: DataInputType = None,
                    X_valid: DataInputType = None, y_valid: DataInputType = None,
                    featurizer: TimeSeriesTransformer = None) -> None:
        """
        Start the DNN training.

        :param n_epochs: number of epochs to try.
        :param X: data for training.
        :param y: target data for training.
        :param X_train: training data to use.
        :param y_train: training target to use.
        :param X_valid: validation data to use.
        :param y_valid: validation target to use.
        :param featurizer: trained featurizer.
        :param automl_settings: dictionary of automl settings
        """
        settings = self.automl_settings
        # Mitigation for auto cv. The fact that TCN is using n_cross_validations is
        # confusing since TCN doesn't do cross-validations.
        if ForecastConstant.cross_validations in settings and settings[ForecastConstant.cross_validations] is not None:
            # Mitigation for auto cv. The fact that TCN is using n_cross_validations is
            # confusing since TCN doesn't do cross-validations.
            # TODO: https://msdata.visualstudio.com/Vienna/_workitems/edit/1835174
            if settings[ForecastConstant.cross_validations] == TimeSeries.AUTO:
                settings[ForecastConstant.cross_validations] = ForecastConstant.NUM_EVALUATIONS_DEFAULT

        assert (ForecastConstant.primary_metric in self.automl_settings)
        num_samples = 0
        ds = None
        ds_train = None
        ds_valid = None
        run_update_callback = None
        self._pre_transform = featurizer
        self._update_params(self._pre_transform)
        horizon, _ = self._get_metadata_from_featurizer()
        self.params.set_parameter(ForecastConstant.Horizon, horizon)
        if "_enable_future_regressors" in settings:
            self.params.set_parameter(ForecastConstant.enable_future_regressors, settings['_enable_future_regressors'])
        if "features_unknown_at_forecast_time" in settings:
            self.params.set_parameter(ForecastConstant.features_unknown_at_forecast_time,
                                      settings['features_unknown_at_forecast_time'])
        if X_train is None:
            X_train = X
            y_train = y

        numericalized_grain_colnames = self._get_numericalized_column_names()
        apply_log_transform_for_label = self.params.get_value(ForecastConstant.apply_log_transform_for_label, True)
        ds = create_timeseries_datasets(X_train,
                                        y_train,
                                        X_valid,
                                        y_valid,
                                        horizon=horizon,
                                        step=1,
                                        has_past_regressors=True,
                                        one_hot=False,
                                        save_last_lookback_data=True,
                                        featurized_ts_id_names=numericalized_grain_colnames,
                                        use_label_log_transform=apply_log_transform_for_label,
                                        embedding_enabled=False,
                                        **settings)
        dset_config = ds.dset_config
        if self._pre_transform.has_unique_target_grains_dropper:
            self._fit_naive(True)

        if self.forecaster is None:
            run_update_callback = self._create_runupdate_callback()
            # Hack for indexer.
            # We will save numericalized_grain_cols and grain_map in the private
            # fields.
            self._numericalized_grain_cols = ds.dataset.numericalized_grain_cols
            self._grain_map = ds.dataset.grain_map
            # Set these fields to static fields.
            # They will not be stored after pickling.
            self._set_static_fields()

            # set the grain info if embedding is needed from the model
            self._build_model_forecaster(
                run_update_callback, dset_config, ds,
                self._numericalized_grain_cols, False, ds._future_channels,
            )

        # set the lookback as the receptive field of the model for the dataset
        if ds.dataset.lookback is None:
            # We may have set lookback at _build_model_forecaster.
            ds.set_lookback(self.forecaster.model.receptive_field)
        # store history with the model to use later for inference that comes with out history.
        self._data_for_inference = ds.get_last_lookback_items()

        # set the transformations used along with the wrapper, so can be used during validation and inference.
        self.set_transforms(ds.dataset.feature_count(), ds.dataset.sample_transform)
        ds_train, ds_valid = ds.ds_train, ds.ds_valid
        num_samples = len(ds_train)

        ds_valid._unknown_columns_to_drop = ds.dataset._unknown_columns_to_drop
        if run_update_callback is not None:
            run_update_callback.set_evaluation_dataset(ds_train, ds_valid)

        batch_size = self._get_batch_size_from_sample_count(num_samples)
        while True:
            Contract.assert_true(batch_size > 0,
                                 "Cannot proceed with batch_size: {}".format(batch_size), log_safe=True)
            try:
                logger.info("Trying with batch_size: {}".format(batch_size))
                if torch.cuda.is_available():
                    logger.info("Using CUDA")
                else:
                    logger.info("Using CPU")
                dataloader_train = self.create_data_loader(ds_train, shuffle=True, batch_size=batch_size,
                                                           drop_last=True)
                dataloader_valid = self.create_data_loader(ds_valid, shuffle=False, batch_size=batch_size)
                assert len(dataloader_train) > 0, "Training Dataloader has zero length"
                assert len(dataloader_valid) > 0, "Validation Dataloader has zero length"
                self.forecaster.fit(
                    dataloader_train=dataloader_train,
                    loss=self.loss,
                    optimizer=self.optimizer,
                    epochs=n_epochs,
                    dataloader_val=dataloader_valid)
                break
            except RuntimeError as e:
                if 'out of memory' in str(e):
                    logger.info("Couldn't allocate memory for batch_size: {}".format(batch_size))
                    batch_size = batch_size // 2
                else:
                    raise ClientException._with_error(
                        AzureMLError.create(
                            TCNWrapperRuntimeError, target="TCNWrapper",
                            reference_code=ReferenceCodes._TCN_WRAPPER_RUNTIME_ERROR,
                            inner_exception=e)) from e

        self.batch_size = batch_size

        # Reset the distributed optimizer.
        # (The optimizer is no longer needed since trainng has completed. Also, the optimizer may not be
        # serializable, which is needed when saving the model.)
        self.optimizer = None

        # At the end of the training upload the tabular metric and model.
        if run_update_callback is not None:
            run_update_callback.upload_model_and_tabular_metrics()

    def _get_future_columns(
            self,
            columns: List[str],
            columns_to_drop: Optional[List[str]]) -> List[str]:
        """
        Return the future columns to be used as an input to TCN.

        :param columns: All columns, present in the data frame.
        :param columns_to_drop: The list of columns unknown in the future.
        :return: The list of columns known into the future.
        """
        if columns_to_drop is not None:
            # We are not doing set operations here to preserve the column order.
            drop_set = set(columns_to_drop)
            return list(filter(lambda x: x not in drop_set, columns))
        return columns

    def _distributed_train(self,
                           num_epochs: int,
                           train_featurized_dataset: TabularDataset,
                           valid_featurized_dataset: TabularDataset,
                           expr_store: ExperimentStore,
                           automl_settings: AzureAutoMLSettings) -> None:
        """
        Train a model in a distributed fashion.

        :param num_epochs: number of epochs to train.
        :param train_featurized_dataset: The featurized training tabular dataset.
        :param valid_featurized_dataset: The featurized validation tabular dataset.
        :param expr_store: The experiment store.
        :param automl_settings_obj: The automl settings object.
        """
        data_profile = expr_store.metadata.timeseries.get_featurized_data_profile()
        self._pre_transform = expr_store.transformers.get_timeseries_transformer()
        train_grain_summaries, valid_grain_summaries = get_grain_summary(
            train_featurized_dataset,
            valid_featurized_dataset,
            data_profile
        )
        log_warning_for_gaps_in_train_val_dataset(data_profile, self._pre_transform.freq_offset)
        columns = get_column_names(
            data_profile,
            automl_settings.time_column_name,
            automl_settings.grain_column_names
        )

        assert (ForecastConstant.primary_metric in self.automl_settings)
        run_update_callback = None
        self._update_params(self._pre_transform)
        horizon, _ = self._get_metadata_from_featurizer()
        self.params.set_parameter(ForecastConstant.Horizon, horizon)
        numericalized_grain_colnames = self._get_numericalized_column_names()
        apply_log_transform_for_target = self.params.get_value(ForecastConstant.apply_log_transform_for_label, True)
        dset_config = DataSourceConfig(feature_channels=len(columns) - 1,
                                       forecast_channels=1,
                                       encodings=None)
        if self._pre_transform.has_unique_target_grains_dropper:
            self._fit_naive(True)
        if "_enable_future_regressors" in self.automl_settings:
            self.params.set_parameter(ForecastConstant.enable_future_regressors,
                                      self.automl_settings['_enable_future_regressors'])
        if "features_unknown_at_forecast_time" in self.automl_settings:
            self.params.set_parameter(ForecastConstant.features_unknown_at_forecast_time,
                                      self.automl_settings['features_unknown_at_forecast_time'])
        _, future_channels, columns_to_drop = get_dataset_future_features(
            train_featurized_dataset.take(1),
            columns,
            self.automl_settings.get('features_unknown_at_forecast_time', None),
        )
        future_columns = self._get_future_columns(columns, columns_to_drop)
        numericalized_grain_columns = [columns.index(gcol) for gcol in numericalized_grain_colnames]
        # If some features are unknown in future, we need to make sure that the grain index
        # in known future columns is correct.
        if columns_to_drop:
            future_numericalized_grain_columns = []
            for grain_column in numericalized_grain_columns:
                Contract.assert_true(
                    len(columns) > grain_column,
                    message="The column list is too short.",
                    reference_code=ReferenceCodes._TCN_DISTRIBUTED_COLUMN_LIST_SHORT)
                num_grain = columns[grain_column]
                Contract.assert_true(
                    num_grain.startswith(TimeSeriesInternal.PREFIX_FOR_GRAIN_FEATURIZATION),
                    message="The numericalized grain ordinal points to the wrong column.",
                    reference_code=ReferenceCodes._TCN_DISTRIBUTED_WRONG_NUM_GRAIN_ORD)
                Contract.assert_true(
                    num_grain in future_columns,
                    message="The numericalised grain column was dropped from columns known in future.",
                    reference_code=ReferenceCodes._TCN_DISTRIBUTED_NUM_GRAIN_DROPPED)
                future_numericalized_grain_columns.append(future_columns.index(num_grain))
        else:
            future_numericalized_grain_columns = numericalized_grain_columns

        if self.forecaster is None:
            dataset_config = get_dataset_config(
                numericalized_grain_colnames,
                apply_log_transform_for_target,
                columns,
                train_grain_summaries,
                self._pre_transform,
                data_profile,
                expr_store
            )
            # data_profile can take a lot of memory that can be freed as it is no longer needed.
            del data_profile
            self._numericalized_grain_cols = dataset_config.dataset.numericalized_grain_cols
            self._grain_map = dataset_config.dataset.grain_map
            self._set_static_fields()
            run_update_callback = self._create_runupdate_callback(is_distributed=True)
            self._build_model_forecaster(run_update_callback,
                                         dset_config,
                                         dataset_config,
                                         future_numericalized_grain_columns,
                                         True,
                                         future_channels=future_channels)
        # set the lookback as the receptive field of the model for the dataset
        logger.info(f"Receptive field is: {self.forecaster.model.receptive_field}")

        lookback = self.forecaster.model.receptive_field
        validation_step_size = horizon
        data_load_config = load_datasets(
            train_featurized_dataset,
            valid_featurized_dataset,
            train_grain_summaries,
            valid_grain_summaries,
            dataset_config.dataset.numericalized_grain_cols,
            future_numericalized_grain_columns,
            columns,
            future_columns,
            lookback,
            horizon,
            validation_step_size,
            self.automl_settings.get('features_unknown_at_forecast_time', None)
        )

        train_ds = TimeSeriesNumpyDataset(
            data_load_config.train_data,
            data_load_config.train_data_fut,
            data_load_config.train_offsets,
            horizon,
            lookback,
            step=1,
            future_channels=data_load_config.future_channels,
        )
        valid_ds = TimeSeriesNumpyDataset(
            data_load_config.valid_data,
            data_load_config.valid_data_fut,
            data_load_config.valid_offsets,
            horizon,
            lookback,
            step=validation_step_size,
            future_channels=data_load_config.future_channels,
        )

        num_train_samples = len(train_ds)
        DistributedHelper.assert_same_across_all_nodes(num_train_samples)
        # set the transformations used along with the wrapper, so can be used during validation and inference.
        self.set_transforms(train_ds.feature_count(), train_ds.sample_transform)

        batch_size = self._get_batch_size_from_sample_count(num_train_samples)
        is_retraining = False
        while True:
            try:
                logger.info("Trying with batch_size: {}".format(batch_size))
                if is_retraining:
                    # set the model and optimizer to None. We will free the GPU (if available)
                    # of their space and recreate them to ensure they do not contain any partial updates.
                    logger.info("Rebuilding model started.")
                    self.forecaster = None
                    self.optimizer = None
                    DistributedHelper.clear_gpu_cache()
                    self._build_model_forecaster(
                        run_update_callback,
                        dset_config, dataset_config,
                        future_numericalized_grain_columns,
                        True, data_load_config.future_channels)
                    logger.info("Rebuilding mode completed.")
                dataloader_train = self.create_data_loader(
                    train_ds,
                    batch_size=batch_size,
                    drop_last=True,
                    sampler=DistributedHelper.get_distributed_sampler(
                        train_ds,
                        num_replicas=data_load_config.num_replicas[MLTableDataLabel.TrainData],
                        rank=data_load_config.replica_id[MLTableDataLabel.TrainData],
                        shuffle=True
                    )
                )
                dataloader_valid = self.create_data_loader(
                    valid_ds,
                    batch_size=batch_size,
                    sampler=DistributedHelper.get_distributed_sampler(
                        valid_ds,
                        num_replicas=data_load_config.num_replicas[MLTableDataLabel.ValidData],
                        rank=data_load_config.replica_id[MLTableDataLabel.ValidData],
                        shuffle=False
                    )
                )
                self.forecaster.fit(
                    dataloader_train=dataloader_train,
                    loss=self.loss,
                    optimizer=self.optimizer,
                    epochs=num_epochs,
                    dataloader_val=dataloader_valid)
                break
            except RuntimeError as e:
                # If batch size is 1, we cannot retry retraining the model because batch size
                # will become 0. Hence, we should rethrow the error in this case.
                if 'out of memory' in str(e) and batch_size > 1:
                    is_retraining = True
                    logger.info("Couldn't allocate memory for batch_size: {}".format(batch_size))
                    batch_size = batch_size // 2
                    # Raise exception to avoid deadlock if processes can't sync within PROCESSES_SYNC_TIMEOUT_SEC.
                    start_time = time.time()
                    handle = DistributedHelper.wait_for_all_processes_async(name="oom_sync")
                    while not DistributedHelper.poll(handle):
                        if time.time() - start_time > PROCESSES_SYNC_TIMEOUT_SEC:
                            logger.warn(PROCESSES_SYNC_FAIL)
                            raise ClientException._with_error(
                                AzureMLError.create(
                                    TCNWrapperDeadlockError, target="TCNWrapper",
                                    reference_code=ReferenceCodes._TCN_WRAPPER_DEADLOCK_ERROR_DISTRIBUTED,
                                    inner_exception=e)) from e
                        else:
                            logger.info("Waiting for other horovod processes to synchronize for out of memory.")
                            time.sleep(PAUSE_EXECUTION_SEC)
                else:
                    raise ClientException._with_error(
                        AzureMLError.create(
                            TCNWrapperRuntimeError, target="TCNWrapper",
                            reference_code=ReferenceCodes._TCN_WRAPPER_RUNTIME_ERROR_DISTRIBUTED,
                            inner_exception=e)) from e

        self.batch_size = batch_size

        # Reset the distributed optimizer.
        # (The optimizer is no longer needed since trainng has completed. Also, the optimizer may not be
        # serializable, which is needed when saving the model.)
        self.optimizer = None

        # store history with the model to use later for inference that comes with out history.
        if DistributedHelper.is_master_node():
            self._data_for_inference = get_lookback_data_for_inference_from_partitioned_datasets(
                train_grain_summaries,
                valid_grain_summaries,
                train_featurized_dataset,
                valid_featurized_dataset,
                self.forecaster.model.receptive_field
            )
        else:
            self._data_for_inference = None

        # At the end of the training upload the tabular metric and model.
        if run_update_callback is not None:
            run_update_callback.upload_model_and_tabular_metrics()

    def _create_runupdate_callback(self, is_distributed: bool = False) -> Optional[RunUpdateCallback]:
        # Only instantiate the callbaack to update the run from the master node. This ensures that
        # only one worker uploads the model, metrics, run properties, etc.
        if not DistributedHelper.is_master_node():
            return None
        if is_distributed:
            return DistributedRunUpdateCallback(
                model_wrapper=self, run_context=Run.get_context(), params=self.params)
        return RunUpdateCallback(
            model_wrapper=self, run_context=Run.get_context(), params=self.params, featurizer=self._pre_transform)

    def _get_batch_size_from_sample_count(self, num_samples: int) -> int:
        """
        Get the batch size from the number of samples in the training dataset.

        :param num_samples: number of samples in the training dataset.

        :returns: the batch size.
        """
        fraction_samples = math.floor(num_samples * 0.05 / DistributedHelper.local_processes_count())
        if fraction_samples <= 1:
            return 1
        return int(math.pow(2, math.floor(math.log(fraction_samples, 2)))) if fraction_samples < 1024 else 1024

    def _raise_timeout_err(self, ref_code: str, experiment_timeout: bool = True) -> None:
        """
        Raise the timeout error.

        :param ref_code: the reference code to use for raised exception.
        :param experiment: If True, the ExperimentTimedOut,
                           otherwise IterationTimedOut will be raised.
        :raises: TimeoutException.
        """
        raise TimeoutException._with_error(
            AzureMLError.create(
                ExperimentTimedOut if experiment_timeout else IterationTimedOut,
                target="DNN child run",
                reference_code=ref_code
            ))

    def _build_model_forecaster(self, run_update_callback: RunUpdateCallback,
                                dset_config: DataSourceConfig,
                                ds: Union[DNNTimeseriesDatasets, TimeseriesDatasetConfig],
                                future_featurized_grain_indices: Sequence[int],
                                is_distributed: bool = False,
                                future_channels: int = 0,
                                ) -> None:
        logger.info('Building model')

        dist_strat = DistributedHelper.get_distribution_strategy(is_distributed)
        # create a model based on the hyper parameters.
        self._enable_future_regressors = self.params.get_value(ForecastConstant.enable_future_regressors,
                                                               False)

        # set the grain info if embedding is needed from the model
        embedding_column_info = ds.embedding_col_infos
        model = build_canned_model(params=self.params, dset_config=dset_config,
                                   horizon=self.params.get_value(ForecastConstant.Horizon),
                                   num_quantiles=len(ForecastConstant.QUANTILES),
                                   embedding_column_info=embedding_column_info,
                                   enable_future_regressors=self._enable_future_regressors,
                                   future_channels=future_channels)

        ds.set_lookback(model.receptive_field)

        device = self.params.get_value(ForecastConstant.Device)
        model = model.to(device)
        # checkpoint directory to save model state.
        chkpt_base = create_timestamped_dir('./chkpts')
        out_dir = create_timestamped_dir(chkpt_base)
        model.to_json(os.path.join(out_dir, 'model_arch.json'))

        # set callbacks.
        lr = self.params.get_value(ForecastConstant.Learning_rate, 0.001)
        self.optimizer = torch.optim.Adam(model.parameters(), lr=lr)

        # number epochs to wait before early stopping evaluation start.
        self.patience = self.params.get_value(TCNForecastParameters.EARLY_STOPPING_DELAY_STEPS,
                                              TCNForecastParameters.EARLY_STOPPING_DELAY_STEPS_DEFAULT)
        # learning rate reduction with adam optimizer
        self.lr_factor = self.params.get_value(TCNForecastParameters.LR_DECAY_FACTOR,
                                               TCNForecastParameters.LR_DECAY_FACTOR_DEFAULT)
        # minimum improvement from the previous epoch to continue experiment, we are using relative improvement.
        self.min_improvement = self.params.get_value(TCNForecastParameters.EARLY_STOPPING_MIN_IMPROVEMENTS,
                                                     TCNForecastParameters.EARLY_STOPPING_MIN_IMPROVEMENTS_DEFAULT)
        # metric to use for early stopping.
        metric = self.primary_metric
        if metric not in get_supported_metrics().keys():
            metric = ForecastConstant.DEFAULT_EARLY_TERM_METRIC
            logger.warn(f'Selected primary metric is not supported for early stopping, using {metric} instead')

        # metric object that computes the training and validation metric
        if is_distributed:
            # For distributed training, we use dataset config instead of DNNTImeseriesDatasets.
            Contract.assert_type(ds, "TimeseriesDatasetConfig", TimeseriesDatasetConfig, log_safe=True)
            train_valid_metrics = get_supported_metrics_for_distributed_forecasting(
                ds.dataset.grain_map,
                future_featurized_grain_indices,
                ds.y_min,
                ds.y_max
            )
            reduce_lr_criteria = GLOBAL_VAL_LOSS
            # Additional seconds are required to download the lookback data for inference.
            # Assuming each grain takes 1 second to download in the worst case and all of
            # the CPU cores are used to download, we estimate how many additional seconds are required
            # to download the whole lookback data for inference so that the experiment does not
            # timeout when download the data leading to experiment getting cancelled and no model
            # being saved. In future, we need a better solution for this or remove lookback_data_for_inference
            # altogether as it is not a scalable idea.
            additional_seconds_required = len(ds.dataset.grain_map) // os.cpu_count()
        else:
            train_valid_metrics = {metric: get_supported_metrics()[metric]}
            reduce_lr_criteria = ForecastConstant.Loss
            additional_seconds_required = 0
        callbacks = [
            LossCallback(),
            # LR reduction was performing with loss metric than any of the custom metric specified.
            ReduceLROnPlateauCallback(reduce_lr_criteria, patience=int(self.patience / 2), factor=self.lr_factor),
            EarlyStoppingCallback(patience=self.patience, min_improvement=self.min_improvement, metric=metric),
        ]
        if is_distributed:
            callbacks.append(_HorovodCallback())

        if run_update_callback is not None:
            callbacks.append(run_update_callback)

        # Get the remaining time for this experiment.
        run_obj = Run.get_context()
        hd_run_obj = None
        # Handle the situation, when run_obj is _OfflineRun.
        if hasattr(run_obj, 'parent'):
            hd_run_obj = run_obj.parent
        if isinstance(hd_run_obj, HyperDriveRun):
            # Calculate the end time in UTC time zone.
            start_time = pd.Timestamp(hd_run_obj._run_dto['start_time_utc'])
            end_time = start_time + pd.Timedelta(minutes=hd_run_obj.hyperdrive_config._max_duration_minutes) \
                - pd.Timedelta(seconds=additional_seconds_required)
            if (end_time - pd.Timestamp.now(tz=start_time.tzinfo)) < REMAINING_TIME_TOLERANCE:
                self._raise_timeout_err(ReferenceCodes._TCN_HD_RUN_TIMEOUT)
            preempt_callback = PreemptTimeLimitCallback(
                end_time=end_time.to_pydatetime())
            callbacks.append(preempt_callback)
            logger.info(f'Start time: {hd_run_obj._run_dto["start_time_utc"]}, '
                        f'latest permissible end time: {end_time.to_pydatetime()}')

        logger.info(f'the name of the metric used EarlyStoppingCallback {metric}')
        logger.info(f'The patience used in used EarlyStoppingCallback {self.patience}')
        logger.info(f'the name of the improvement passed to EarlyStoppingCallback {self.min_improvement}')
        logger.info(f'LR Factor {self.lr_factor}')

        # Create batch transforms
        feature_transforms = None
        label_index = 0

        norm = Normalizer(
            feature_indices=ds.dataset.get_feature_indices_for_normalization(),
            offset=ds.dataset.offsets,
            scale=ds.dataset.scales,
            mode=NormalizationMode.PER_SERIES
        )
        norm_y = Normalizer(
            feature_indices=0,
            offset=ds.dataset.offsets_y,
            scale=ds.dataset.scales_y,
            mode=NormalizationMode.PER_SERIES
        )
        batch_normalizer = BatchNormalizer(
            past_regressor=norm,
            past_regressand=norm_y,
            future_regressand=norm_y,
        )

        logger.info(f'Apply log transform to label during training: {ds.dataset.use_label_log_transform}')
        if ds.dataset.use_label_log_transform:
            label_log_tranform = FeatureTransform(label_index, log_transform, self._exp)
            feature_transforms = BatchFeatureTransform(past_regressand=label_log_tranform,
                                                       future_regressand=label_log_tranform)

        batch_transform = GenericBatchTransform(feature_transforms=feature_transforms,
                                                subtract_offset=BatchSubtractOffset(label_index),
                                                normalizer=batch_normalizer,
                                                series_indexer=ForecastTCNWrapper.indexer
                                                )
        self.batch_transform = batch_transform

        # set up the model for training.
        self.forecaster = Forecaster(model=model,
                                     device=device,
                                     metrics=train_valid_metrics,
                                     callbacks=callbacks,
                                     batch_transform=batch_transform,
                                     distribution_strategy=dist_strat)

    def predict(self, X: DataInputType, y: DataInputType, n_samples: int = 1) -> np.ndarray:
        """
        Return the predictions for the passed in `X` and `y` values.

        :param X: data values.
        :param y: label for look back and nan for the rest.
        :param n_samples: number of samples to be returned with each prediction.
        :return: numpy ndarray with shape (n_samples, n_rows, horizon).
        """
        X, y = _wrapper_util.convert_X_y_to_pandas(X, y)
        assert (ForecastConstant.primary_metric in self.automl_settings)
        if y is None:
            y = pd.DataFrame([None] * X.shape[0])
        time_column = self.automl_settings[ForecastConstant.time_column_name]
        grains = None
        if ForecastConstant.automl_constants.TimeSeries.GRAIN_COLUMN_NAMES in self.automl_settings:
            grains = self.automl_settings[ForecastConstant.automl_constants.TimeSeries.GRAIN_COLUMN_NAMES]
        grains_list = grains if grains else []
        X, y = ForecastingPipelineWrapper.static_preaggregate_data_set(self._pre_transform, time_column,
                                                                       grains_list, X, y)
        featurized_ts_id_names = None
        grain_featurizer = get_pipeline_step(self._pre_transform.pipeline,
                                             TimeSeriesInternal.MAKE_GRAIN_FEATURES)
        if grain_featurizer is not None:
            featurized_ts_id_names = grain_featurizer._preview_grain_feature_names_from_grains(grains)
        X, y = _wrapper_util.transform_data(self._pre_transform, X, y)

        ds = self._get_timeseries(X, y, featurized_ts_id_names=featurized_ts_id_names)
        return self._predict(ds).reshape(-1)

    def _get_metadata_from_featurizer(self) -> Tuple[int, str]:
        """Get metadata from the trained featurizer."""
        max_horizon = self._pre_transform.max_horizon

        grain_feature_col_prefix = None
        grain_index_featurizer = [a[1] for a in self._pre_transform.pipeline.steps
                                  if isinstance(a[1], automl_transformer.GrainIndexFeaturizer)]
        if grain_index_featurizer:
            grain_feature_col_prefix = grain_index_featurizer[0].grain_feature_prefix + \
                grain_index_featurizer[0].prefix_sep

        return max_horizon, grain_feature_col_prefix

    def _get_timeseries(self, X: DataInputType, y: DataInputType, step: str = None,
                        featurized_ts_id_names: Optional[List[str]] = None) -> TimeSeriesDataset:
        """
        Get timeseries for given inputs and set_lookback for model.

        :param X: data values
        :param y: label for lookback and nan for rest
        :param n_samples: number of samples to be returned with each prediction.
        :param step: number of samples to skip to get to the next block of data(lookback+horzon)
        :param featurized_ts_id_names: the numericalized grain column names.
        :return: Timeseries dataset
        """
        if step is None:
            step = self.params.get_value(ForecastConstant.Horizon)
        X_df, y_df = _wrapper_util.convert_X_y_to_pandas(X, y)
        ds = TimeSeriesDataset(X_df,
                               y_df,
                               horizon=self.params.get_value(ForecastConstant.Horizon),
                               step=step,
                               has_past_regressors=True,
                               one_hot=False,
                               sample_transform=self._sample_transform,
                               featurized_ts_id_names=featurized_ts_id_names,
                               **self.automl_settings)
        ds.set_lookback(self.forecaster.model.receptive_field)
        return ds

    def _predict(
            self,
            ds: Optional[TimeSeriesDataset] = None,
            data_loader: Optional[DataLoader] = None) -> np.ndarray:
        """
        Return the predictions for the passed timeseries dataset.

        :param ds: TimeSeriesDataset to use for prediction.
        :param data_loader: the data loader to use for prediction.
        :return: numpy ndarray with shape (1, 1, horizon).
        """
        if data_loader is None:
            data_loader = self.create_data_loader(ds, False)
        predictions = np.asarray(self.forecaster.predict(data_loader))
        return_predict_index = ForecastConstant.QUANTILES.index(0.5)
        return cast(np.ndarray, predictions[return_predict_index:return_predict_index + 1])

    def get_lookback(self):
        """Get lookback used by model."""
        if self.forecaster is not None:
            return self.forecaster.model.receptive_field
        else:
            return self.params.get_value(ForecastConstant.Lookback)

    @property
    def name(self):
        """Name of the Model."""
        return ForecastConstant.ForecastTCN

    def parse_parameters(self) -> DNNParams:
        """
        Parse parameters from command line.

        return: returns the  DNN  param object from the command line arguments
        """
        parser = argparse.ArgumentParser()

        parser.add_argument(DNNForecastWrapper.get_arg_parser_name(ForecastConstant.num_epochs), type=int,
                            default=25, help='number of epochs to train')
        parser.add_argument(DNNForecastWrapper.get_arg_parser_name(ForecastConstant.Lookback), type=int,
                            default=8, help='lookback for model')
        parser.add_argument(DNNForecastWrapper.get_arg_parser_name(ForecastConstant.Horizon), type=int,
                            default=4, help='horizon for prediction')
        parser.add_argument(DNNForecastWrapper.get_arg_parser_name(ForecastConstant.Batch_size), type=int,
                            default=8, help='batch_size for training')
        parser.add_argument(DNNForecastWrapper.get_arg_parser_name(ForecastConstant.primary_metric), type=str,
                            default='', help='primary metric for training')
        parser.add_argument(DNNForecastWrapper.get_arg_parser_name(ForecastConstant.enable_future_regressors),
                            type=bool, default=False, help='enable future features')

        # Model hyper-parameters
        parser.add_argument(DNNForecastWrapper.get_arg_parser_name(ForecastConstant.Learning_rate), type=float,
                            default=0.001, help='learning rate')
        parser.add_argument(DNNForecastWrapper.get_arg_parser_name(TCNForecastParameters.NUM_CELLS), type=int,
                            help='num cells')
        parser.add_argument(DNNForecastWrapper.get_arg_parser_name(TCNForecastParameters.MULTILEVEL), type=str,
                            help='multilevel')
        parser.add_argument(DNNForecastWrapper.get_arg_parser_name(TCNForecastParameters.DEPTH), type=int,
                            help='depth')
        parser.add_argument(DNNForecastWrapper.get_arg_parser_name(TCNForecastParameters.NUM_CHANNELS), type=int,
                            help='number of channels')
        parser.add_argument(DNNForecastWrapper.get_arg_parser_name(TCNForecastParameters.DROPOUT_RATE), type=float,
                            help='dropout rate')
        parser.add_argument(DNNForecastWrapper.get_arg_parser_name(TCNForecastParameters.DILATION), type=int,
                            default=TCNForecastParameters.DILATION_DEFAULT, help='tcn dilation')
        parser.add_argument(DNNForecastWrapper.get_arg_parser_name(TCNForecastParameters.FUTURE_LAYERS), type=int,
                            default=TCNForecastParameters.FUTURE_LAYERS_DEFAULT, help='future layers')
        parser.add_argument(DNNForecastWrapper.get_arg_parser_name(TCNForecastParameters.FUTURE_EXPANSION_FACTOR),
                            type=int, default=TCNForecastParameters.FUTURE_EXPANSION_FACTOR_DEFAULT,
                            help='future expansion factor')

        # EarlyStopping Parameters
        parser.add_argument(DNNForecastWrapper.
                            get_arg_parser_name(TCNForecastParameters.EARLY_STOPPING_MIN_IMPROVEMENTS),
                            type=float,
                            default=TCNForecastParameters.EARLY_STOPPING_MIN_IMPROVEMENTS_DEFAULT,
                            help='min improvement required between epochs to continue training')
        parser.add_argument(DNNForecastWrapper.get_arg_parser_name(TCNForecastParameters.LR_DECAY_FACTOR),
                            type=float,
                            default=TCNForecastParameters.LR_DECAY_FACTOR_DEFAULT,
                            help='LR decay factor used in reducing Learning Rate by LR schedular.')

        # Embedding defaults
        parser.add_argument(DNNForecastWrapper.
                            get_arg_parser_name(TCNForecastParameters.MIN_GRAIN_SIZE_FOR_EMBEDDING),
                            type=int,
                            default=TCNForecastParameters.MIN_GRAIN_SIZE_FOR_EMBEDDING_DEFAULT,
                            help='min grain size to enable grain embedding')
        parser.add_argument(DNNForecastWrapper.
                            get_arg_parser_name(TCNForecastParameters.EMBEDDING_TARGET_CALC_TYPE),
                            type=str,
                            default=TCNForecastParameters.EMBEDDING_TARGET_CALC_TYPE_DEFAULT,
                            help='method to use when computing embedding output size')
        parser.add_argument(DNNForecastWrapper.
                            get_arg_parser_name(TCNForecastParameters.EMBEDDING_MULT_FACTOR),
                            type=float,
                            default=TCNForecastParameters.EMBEDDING_MULT_FACTOR_DEFAULT,
                            help='multiplaction factor to use output size when MULT method is selected')
        parser.add_argument(DNNForecastWrapper.
                            get_arg_parser_name(TCNForecastParameters.EMBEDDING_ROOT),
                            type=float,
                            default=TCNForecastParameters.EMBEDDING_ROOT_DEFAULT,
                            help='the number to use as nth root for output sise when ROOT method is selectd')

        args, unknown = parser.parse_known_args()
        arg_dict = vars(args)
        arg_dict[ForecastConstant.n_layers] = max(int(math.log2(args.lookback)), 1)
        dnn_params = DNNParams(ForecastTCNWrapper.required_params, arg_dict, ForecastTCNWrapper.default_params)
        return dnn_params

    def __getstate__(self):
        """
        Get state picklable objects.

        :return: state
        """
        state = super(ForecastTCNWrapper, self).__getstate__()
        state['model_premix_config'] = self.forecaster.model.premix_config
        state['model_backbone_config'] = self.forecaster.model.backbone_config
        state['model_head_configs'] = self.forecaster.model.head_configs
        state['model_state_dict'] = self.forecaster.model.state_dict()
        state['batch_transform'] = self.batch_transform
        return state

    def __setstate__(self, state):
        """
        Set state for object reconstruction.

        :param state: pickle state
        """
        super(ForecastTCNWrapper, self).__setstate__(state)
        model = ForecastingModel(state['model_premix_config'],
                                 state['model_backbone_config'],
                                 state['model_head_configs'])
        model.load_state_dict(state['model_state_dict'])
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.batch_transform = state['batch_transform']
        # Make sure that if we are doing normalization, our offsets and scales are
        # not on GPU.
        self._move_normalizer_tensors_to_ram_maybe(self.batch_transform._normalizer.past_regressor)
        self._move_normalizer_tensors_to_ram_maybe(self.batch_transform._normalizer.past_regressand)
        self._move_normalizer_tensors_to_ram_maybe(self.batch_transform._normalizer.future_regressor)
        self._move_normalizer_tensors_to_ram_maybe(self.batch_transform._normalizer.future_regressand)
        self.forecaster = Forecaster(model=model,
                                     device=device,
                                     batch_transform=self.batch_transform)
        # Set the internal state to the static fields, so that indexer will be able
        # to use it after pickling.
        self._set_static_fields()

    def _move_normalizer_tensors_to_ram_maybe(self, normalizer: Optional[Normalizer]) -> None:
        """
        Move normalizer's offset and scale to regular RAM if it is on gpu.

        In case if we have loaded models with pytorch, all the offsets and scales will
        be on cuda device, which will brake as input tensor will be on CPU. If
        :param normalizer: The normalizer of batch transform.
        """
        if normalizer is None:
            return
        if normalizer.offset.device != 'cpu':
            normalizer.offset = normalizer.offset.to('cpu')
        if normalizer.scale.device != 'cpu':
            normalizer.scale = normalizer.scale.to('cpu')

    @staticmethod
    def indexer(tensor_data: torch.Tensor) -> torch.Tensor:
        """
        Return tensor, mapping offsets/scales to input tensor.

        Maps an input tensor containing integer encoded timeseries id columns
        into a tensor where each entry is an index into the scale factor arrays used for normalization.
        Input shape: (n_examples, n_features, *), output shape: (n_examples).

        :param tensor_data: input tensor containing integer encoded timeseries id columns.
        :return: tensor where each entry is an index into the scale
                 factor arrays used for normalization.
        """
        if not ForecastTCNWrapper._s_numericalized_grain_cols:
            # No grains.
            return torch.from_numpy(np.repeat(0, tensor_data.shape[0])).long()
        # For each batch determine the grain mapping.
        tensor_order = []
        for i in range(tensor_data.shape[0]):
            grain_num = tuple(tensor_data[i, ForecastTCNWrapper._s_numericalized_grain_cols, 0].numpy())
            Contract.assert_true(grain_num in ForecastTCNWrapper._s_grain_map,
                                 "One of the time series was not found in the data set.",
                                 target='batch', reference_code=ReferenceCodes._TCN_TS_ID_ABSENT)
            tensor_order.append(ForecastTCNWrapper._s_grain_map[grain_num])
        return torch.tensor(tensor_order).long()

    @staticmethod
    def _log(x: torch.Tensor):
        """
        Log natural log of the tensor used in batch transform in base forecaster package.

        :param x: the value to transform, which is the subset of feature[index]
        tensors based on index in feature transform.
        """
        return torch.log(1 + x)

    @staticmethod
    def _exp(x: torch.Tensor):
        """
        Exponential of the tensor used in batch transform in base forecaster package.

        :param x: the value to transform/reverse transform.
        """
        return torch.exp(x) - 1

    @property
    def quantiles(self) -> List[float]:
        """Quantiles for the pipeline to predict."""
        return self._quantiles

    @quantiles.setter
    def quantiles(self, quantiles: Union[float, List[float]]) -> None:
        if not isinstance(quantiles, list):
            quantiles = [quantiles]
        if min(quantiles) <= 0 or max(quantiles) >= 1:
            raise ValidationException._with_error(
                AzureMLError.create(QuantileRange, target="quantiles", quantile=str(max(quantiles)))
            )
        self._quantiles = quantiles

    def _predict_quantile(
            self,
            ds: Optional[TimeSeriesDataset] = None,
            data_loader: Optional[DataLoader] = None) -> np.ndarray:
        """
        Return quantile prediction for passed timeseries dataset.

        The prediction is made by estimating the PPF from the direct TCN quantile forecasts by -
        1) extrapolating the left and right tails from matching normal ditribution if given quantile<0.1
        or greater than 0.9, and 2) interpolating the interior quantiles via spline fitting using Piecewise
        Cubic Hermite Interpolating Polynomial algorithm.

        :param ds: TimeSeriesDataset to use for prediction.
        :param data_loader: the data loader to use for prediction.
        :return: numpy ndarray with shape (1, 1, horizon).
        """
        if data_loader is None:
            data_loader = self.create_data_loader(ds, False)
        predictions = np.asarray(self.forecaster.predict(data_loader))
        median_index = ForecastConstant.QUANTILES.index(0.5)
        # post process the TCN output to force the quantile forecasts to be in non-decreasing order
        for i in range(median_index - 1, -1, -1):
            updated_predictions = np.amin(predictions[i:i + 2], axis=0)
            predictions[i] = updated_predictions
        for i in range(median_index + 1, len(ForecastConstant.QUANTILES)):
            updated_predictions = np.amax(predictions[i - 1:i + 1], axis=0)
            predictions[i] = updated_predictions
        # TCN quantile forecasts for a positive target can be negatively valued.
        # In such cases, set TCN quantile forecasts to 0 and forgo the normal left tail extrapolation
        if self.params.get_value('apply_log_transform_for_label'):
            predictions = np.where(predictions < 0, 0, predictions)
        preds_at_50 = predictions[median_index]
        preds_at_10 = predictions[ForecastConstant.QUANTILES.index(0.1)]
        preds_at_90 = predictions[ForecastConstant.QUANTILES.index(0.9)]
        sqrt_of_2 = np.sqrt(2)
        q = self._target_quantile
        if q < 0.1:
            # Cases where predictions at 10th equals to one to at 50th, estimated normal variance would be 0.
            # So, return the forecast made at 10th percentile and forego the tail extrapolation.
            if np.all(preds_at_10 == 0):
                return preds_at_10
            # Else extrpolate tail region from a normal distribution that matches the 10th and 50th
            # percentile TCN forecasts
            dev = (preds_at_50 - preds_at_10) / (erfinv(0.8) * sqrt_of_2)
            preds_at_q = preds_at_50 - (dev * sqrt_of_2 * erfinv(1 - (2 * q)))
            if self.params.get_value('apply_log_transform_for_label'):
                preds_at_q = np.where(preds_at_q < 0, 0, preds_at_q)
        elif q > 0.9:
            # Cases where predictions at 50th equals to one to at 90th, estimated normal variance would be 0.
            # So, return the forecast made at 90th percentile and forego the tail extrapolation.
            if np.array_equal(preds_at_50, preds_at_90):
                return preds_at_90
            # Else extrpolate tail region from a normal distribution that matches the 50th and 90th
            # percentile TCN forecasts
            dev = (preds_at_90 - preds_at_50) / (erfinv(0.8) * sqrt_of_2)
            preds_at_q = preds_at_50 + (dev * sqrt_of_2 * erfinv((2 * q) - 1))
        else:
            # interpolate interior quantiles via spline fitting
            interploated_function = PchipInterpolator(np.asarray(ForecastConstant.QUANTILES),
                                                      predictions, axis=0)
            preds_at_q = interploated_function(q)
        return preds_at_q
