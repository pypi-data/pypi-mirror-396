# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module containing abstract class for DNNForecastWrapper and DNNParams."""
from abc import abstractmethod
from datetime import datetime
import sys

import azureml.dataprep as dprep
import numpy as np
import pandas as pd
import torch
from torch.utils.data.distributed import DistributedSampler
from typing import Any, Dict, List, Optional, Tuple, Union, cast
from torch.utils.data import DataLoader

from ..constants import ForecastConstant
from ..datasets.timeseries_inference_datasets import TimeSeriesInferenceDataset
from ..datasets.timeseries_datasets import TimeSeriesDataset
from ..types import DataInputType
from azureml._common._error_definition import AzureMLError
from azureml._common._error_definition.user_error import ArgumentBlankOrEmpty
from azureml.automl.core.shared import constants
from azureml.automl.core.shared._diagnostics.automl_error_definitions import TimeseriesNothingToPredict
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.core.shared._diagnostics.validation import Validation
from azureml.automl.core.shared.exceptions import ClientException, ConfigException, DataException
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.runtime.experiment_store import ExperimentStore
from azureml.automl.runtime.featurizer.transformer.timeseries.timeseries_transformer import TimeSeriesTransformer
from azureml.automl.runtime.shared.forecast_model_wrapper_base import ForecastModelWrapperBase
from azureml.automl.runtime.shared.model_wrappers import ForecastingPipelineWrapper
from azureml.contrib.automl.dnn.forecasting.wrapper._distributed_helper import DistributedHelper
from azureml.contrib.automl.dnn.forecasting.wrapper import _wrapper_util
from azureml.data import TabularDataset
from azureml.train.automl._azureautomlsettings import AzureAutoMLSettings
from azureml.automl.core.shared._diagnostics.automl_error_definitions import NotSupported
from azureml.training.tabular.models.forecasting_pipeline_wrapper_base \
    import ForecastingPipelineWrapperBase


class DNNParams:
    """This class is used in storing the DNN parameters for various forecast models."""

    def __init__(self,
                 required: List[str],
                 params: Dict[str, Any],
                 defaults: Optional[Dict[str, Any]] = None):
        """Initialize the object with required, default and passed in parameters.

        :param required: Required parameters for this Model, used in validation.
        :param params:  parameters passed.
        :param defaults: Default parameter if a required parameter is not passed.
        """
        self._required = required.copy() if required else {}
        self._params = params.copy() if params else {}
        self._data_for_inference = None
        self._init_defaults_for_missing_required_parameters(defaults if defaults else {})

    def set_parameter(self, name: str, value: Any) -> None:
        """Set the parameter with the passed in value.

        :param name: name of the parameter to set/update.
        :param value: value to set.
        :return: None
        """
        self._params[name] = value

    def _init_defaults_for_missing_required_parameters(self, defaults) -> None:
        """Set default values for missing required parameters.

        :return:
        """
        for name in self._required:
            if name not in self._params:
                if name in defaults:
                    self._params[name] = defaults[name]
                else:
                    raise ClientException._with_error(AzureMLError.create(
                        ArgumentBlankOrEmpty, target="defaults", argument_name=name,
                        reference_code=ReferenceCodes._TCN_EMPTY_REQUIRED_PARAMETER)
                    )

    def get_value(self, name: str, default_value: Any = None) -> Any:
        """Get the value from the parameter or default dictionary.

        :param name: name of the parameter to get the values for.
        :param default_value: default value to use in case param is unset or not found
        :return:
        """
        if name in self._params:
            value = self._params.get(name)
            if value is None:
                value = default_value
            return value
        return default_value

    def __str__(self) -> str:
        """Return the string printable representation of the DNNParams.

        :return:
        """
        return str(self._params)


class _InferenceGrainContext:
    """This class is used in storing the DNN parameters for various forecast models."""

    def __init__(self,
                 grain: List[str],
                 forecast_origin: datetime,
                 context_grain_df: Optional[pd.DataFrame] = None,
                 transformed_grain_df: Optional[pd.DataFrame] = None):
        """Initialize the object with required, default and passed in parameters.

        :param grain: List of keys for the grain.
        :param grain_df:  a dataframe contains a grain
        :param forecast_origin: forecast origin for the series/grain.
        :param context_grain_df: context for prediction coming from data saved with model for lookback.
        :param transformed_grain_df: context for prediction coming from data saved with model for lookback.
        """
        self.grain = grain
        self.forecast_origin = forecast_origin
        self.context_grain_df = context_grain_df
        self.transformed_grain_df = transformed_grain_df


class DNNForecastWrapper(torch.nn.Module, ForecastModelWrapperBase):
    """This is the abstract class for Forecast DNN Wrappers."""

    def __init__(self, metadata: Dict[str, Any]):
        """Initialize with defaults."""
        super(torch.nn.Module, self).__init__(metadata=metadata)
        super(ForecastModelWrapperBase, self).__init__()
        self.input_channels = None
        self.params = None
        self.output_channels = 1
        self._pre_transform = None
        self._sample_transform = None
        self.forecaster = None
        self._data_for_inference = None
        self.raw_data_sample = None
        self.batch_transform = None

    @abstractmethod
    def train_model(self, n_epochs: int, X: DataInputType = None, y: DataInputType = None,
                    X_train: DataInputType = None, y_train: DataInputType = None,
                    X_valid: DataInputType = None, y_valid: DataInputType = None,
                    featurizer: Optional[TimeSeriesTransformer] = None) -> None:
        """Start the DNN training.

        :param n_epochs: number of epochs to try.
        :param X: full set of data for training.
        :param y: fullsetlabel for training.
        :param X_train: training data to use.
        :param y_train: validation data to use.
        :param X_valid: validation data to use.
        :param y_valid: validation target  data to use.
        :param featurizer: The trained featurizer.
        :param automl_settings: dictionary of automl settings.

        :return: Nothing, the model is trained.
        """
        raise NotImplementedError

    def _distributed_train(self,
                           num_epochs: int,
                           train_featurized_dataset: TabularDataset,
                           valid_featurized_dataset: TabularDataset,
                           expr_store: ExperimentStore,
                           automl_settings_obj: AzureAutoMLSettings) -> None:
        """
        Train a model in a distributed fashion.

        :param num_epochs: number of epochs to train.
        :param train_featurized_dataset: The featurized training tabular dataset.
        :param valid_featurized_dataset: The featurized validation tabular dataset.
        :param expr_store: The experiment store.
        :param automl_settings_obj: The automl settings object.
        """
        raise NotImplementedError

    @abstractmethod
    def predict(self, X: DataInputType, y: DataInputType, n_samples: int) -> np.ndarray:
        """Return the predictions for the passed in X and y values.

        :param X: data values
        :param y: label for look back and nan for the rest.
        :param n_samples:  number samples to be retured with each prediction.
        :return: a tuple containing one dimentional prediction of ndarray and tranformed X dataframe.
        """
        raise NotImplementedError

    def get_lookback(self):
        """Return the lookback."""
        raise NotImplementedError

    def _predict(self,
                 ds: Optional[TimeSeriesDataset] = None,
                 n_samples: int = 1,
                 data_loader: Optional[DataLoader] = None) -> np.ndarray:
        """Get DNN forecasts for all samples in the input torch Dataset."""
        raise NotImplementedError

    def _update_params(self, ts_transformer: TimeSeriesTransformer) -> None:
        """
        Set object timeseries metadata from the ts_transformer.

        This is an override of the base class update method to allow for forecast origin times
        later than the end of the training set.
        """
        super()._update_params(ts_transformer)
        if self._data_for_inference is not None:
            # Set forecast origin times from the cached inference data
            # This is necessary in train-valid scenarios when the forecast origin is at the end
            # of the validation set instead of the training set
            time_in_index = self.time_column_name in self._data_for_inference.index.names
            Contract.assert_true(time_in_index or self.time_column_name in self._data_for_inference.columns,
                                 'Cached inference data is missing the time column.', log_safe=True)
            for tsid, df_one in self._data_for_inference.groupby(self.grain_column_names):
                times = df_one.index.get_level_values(self.time_column_name) \
                    if time_in_index else df_one[self.time_column_name]
                self.forecast_origin[tsid] = times.max()

    def _update_params_for_forecast(self):
        self._update_params(self._pre_transform)

    def _pipeline_forecast_internal(
            self,
            X_pred: Optional[pd.DataFrame] = None,
            y_pred: Optional[Union[pd.DataFrame, np.ndarray]] = None,
            Xy_pred_in: Optional[pd.DataFrame] = None,
            dict_rename_back: Optional[Dict[str, str]] = None,
            forecast_destination: Optional[pd.Timestamp] = None,
            ignore_data_errors: bool = False,
            preprocessors: Optional[List[Any]] = None,
            forecaster: Optional[Any] = None,
            **kwargs
    ) -> tuple:
        """Return the predictions for the passed in X and y values.

        :param X_pred: data values
        :param y_pred: label for look back and nan for the rest.
        :return: a ndarray of samples X rows X horizon
        """
        Validation.validate_value(X_pred, 'X')
        Validation.validate_type(X_pred, 'X', (pd.DataFrame, dprep.Dataflow))
        Contract.assert_value(self._pre_transform, '_pre_transform', log_safe=True)
        settings = self.automl_settings
        time_column = settings[ForecastConstant.time_column_name]
        horizon = self.params.get_value(ForecastConstant.Horizon)
        looback = self.get_lookback()
        target_column = ForecastConstant.automl_constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN
        saved_data = self._data_for_inference
        grains = settings.get(ForecastConstant.automl_constants.TimeSeries.GRAIN_COLUMN_NAMES)
        y = pd.DataFrame([np.nan] * X_pred.shape[0]) if y_pred is None else y_pred.copy()

        X, y = _wrapper_util.convert_X_y_to_pandas(X_pred, y)
        X = self._try_set_time_column_data_type(X, time_column)
        # Fix the frequency first.
        grains_list = grains if grains else []
        X, y = ForecastModelWrapperBase.static_preaggregate_data_set(self._pre_transform, time_column,
                                                                     grains_list, X, y)
        if not isinstance(y, pd.DataFrame):
            y = pd.DataFrame(y)
        X[target_column] = y.values
        X_orig = X.copy()
        index_names = [time_column] + grains if grains else [time_column]

        # get the forcast origin for each of the grain and grain data frame.
        grain_inf_conext_list = self._get_inference_grain_context_list(grains, X, y, time_column,
                                                                       target_column, saved_data)
        X_predicted_labels = self._recursive_forecast(grain_inf_conext_list, looback,
                                                      horizon, time_column, target_column, **kwargs)
        # set the frames with same data type on date and with no index for merge.
        X_orig.reset_index(inplace=True)
        X_predicted_labels.reset_index(inplace=True)
        X_orig = self._try_set_time_column_data_type(X_orig, time_column)
        X_predicted_labels = self._try_set_time_column_data_type(X_predicted_labels, time_column)
        ts_transformer = self._get_not_none_ts_transformer()
        unique_grain_target_dropper = ts_transformer.unique_target_grain_dropper \
            if ts_transformer.has_unique_target_grains_dropper else None
        result = _wrapper_util.align_results(
            X_orig, X_predicted_labels, target_column, True, index_names,
            unique_grain_target_dropper, self.grain_column_list)
        y_pred = self._convert_target_type_maybe(result.pop(target_column).values)
        result[target_column] = y_pred
        return result[target_column].values, result

    def _right_pad_transformed_data(self, df_transformed_one: pd.DataFrame, padding_length: int) -> pd.DataFrame:
        """
        Pad a transformed, single series DataFrame on the right.

        The input is assumed to be a single series DataFrame where the time, and possibly, series IDs are in the index.
        The padding will simply repeat the final row of the input to get the required padding length.
        However, the time index will be continued according to the timeseries frequency and padded target
        values will be set to np.nan.
        """
        input_end_time = df_transformed_one.index.get_level_values(self.time_column_name)[-1]
        padding_times = pd.date_range(input_end_time, periods=(padding_length + 1), freq=self.data_frequency)[1:]
        df_padding_one = df_transformed_one.iloc[-1:].sample(n=padding_length, replace=True)
        df_padding_one.reset_index(inplace=True)
        df_padding_one[self.time_column_name] = padding_times
        if self.target_column_name in df_padding_one.columns:
            df_padding_one[self.target_column_name] = np.nan
        df_padding_one.set_index(df_transformed_one.index.names, inplace=True)
        return pd.concat([df_transformed_one, df_padding_one])

    def _pipeline_fit_internal(self, X: pd.DataFrame, y: np.ndarray) -> 'ForecastingPipelineWrapper':
        raise ConfigException._with_error(
            AzureMLError.create(
                NotSupported,
                target="fit",
                scenario_name="forecasting TCN model",
                reference_code=ReferenceCodes._TCN_FIT_UNSUPPORT)
        )

    def _pipeline_forecast_quantiles_internal(
            self,
            X_pred: pd.DataFrame,
            Xy_pred_in: pd.DataFrame,
            ignore_data_errors: Optional[bool] = False
    ) -> pd.DataFrame:
        quantile_forecast_df = pd.DataFrame()
        target_column = ForecastConstant.automl_constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN
        for q in self.quantiles:
            self._target_quantile = q
            fc, forecast_df = self._pipeline_forecast_internal(
                X_pred, ignore_data_errors=ignore_data_errors, if_forecast_quantile=True
            )
            if len(quantile_forecast_df) == 0:
                quantile_forecast_df = forecast_df.copy()
                quantile_forecast_df.rename(columns={target_column: f"{str(q)}"}, inplace=True)
            else:
                quantile_forecast_df[f"{str(q)}"] = forecast_df[target_column]
        return quantile_forecast_df

    def _get_inference_grain_context_list(self, grains: List[str], X: pd.DataFrame, y: pd.DataFrame,
                                          time_column: str, target_column: str,
                                          saved_data: pd.DataFrame) -> List[_InferenceGrainContext]:
        """Return the list of grain details for inference.

        :param X: data values
        :param y: label for look back and nan for the rest.
        :param time_column: time_column name.
        :param target_column: target column nanem.
        :return: a list of InferenceGrainContexts
        """
        grain_inf_conext_list = []
        if grains:
            grouped_X = X.groupby(grains)
            for grain, grain_df in grouped_X:
                forecast_origin = self._get_grain_forecast_origin(grain_df, time_column, target_column)
                grain_inf_conext_list.append(_InferenceGrainContext(grain, forecast_origin))
        else:
            forecast_origin = self._get_grain_forecast_origin(X, time_column, target_column)
            grain_inf_conext_list.append(_InferenceGrainContext(None, forecast_origin))

        X_transformed, y_transformed = _wrapper_util.transform_data(self._pre_transform, X, y)

        new_grain_inf_context_list = grain_inf_conext_list
        if target_column not in X_transformed.columns:
            X_transformed[target_column] = y_transformed.values
            if grains:
                grouped_X_transformed = X_transformed.groupby(grains)
                grouped_saved_data = saved_data.groupby(grains)

                # Some grains may be removed by the grain_dropper, so here only the grains which are in the
                # transformed data are used.
                new_grain_inf_context_list = []
                for context in grain_inf_conext_list:
                    if context.grain in grouped_X_transformed.groups:
                        new_grain_inf_context_list.append(context)

            for grain_inf_context in new_grain_inf_context_list:
                if grain_inf_context.grain:
                    grain_inf_context.transformed_grain_df = grouped_X_transformed.get_group(grain_inf_context.grain)
                    if grain_inf_context.grain in grouped_saved_data.groups:
                        grain_inf_context.context_grain_df = grouped_saved_data.get_group(grain_inf_context.grain)
                    else:
                        grain_inf_context.context_grain_df = saved_data[0:0]
                else:
                    grain_inf_context.transformed_grain_df = X_transformed
                    grain_inf_context.context_grain_df = saved_data
        return new_grain_inf_context_list

    def _recursive_forecast(self, grain_inf_context_list: List[Dict],
                            looback: int, horizon: int, time_column: str,
                            target_column: str, **kwargs) -> pd.DataFrame:
        """Return the predictions for the passed in X and y values.

        :param grain_inf_context: list of inference contexts.
        :param looback: look back of the data.
        :param horizon: horizon related to this model.
        :param time_column: Time column name in the dataset.
        :param target_column: label to predict.
        :return: a data frame contains the prediction in target column.
        """
        result_list = []
        for grain_inf_context in grain_inf_context_list:
            result_list.append(self._recursive_forecast_grain(grain_inf_context, looback,
                                                              horizon, time_column, target_column, **kwargs))
        X_with_predicted_y = result_list[0] if len(result_list) == 1 else pd.concat([item for item in result_list])
        return X_with_predicted_y

    def _recursive_forecast_grain(self, grain_inf_context: Dict,
                                  lookback: int, horizon: int, time_column: str,
                                  target_column: str, **kwargs) -> pd.DataFrame:
        """Return the predictions for the passed in X and y values.

        :param grain_inf_context: inference contextx for a grain
        :param looback: look back of the data.
        :param horizon: horizon related to this model.
        :param time_column: time_column name.
        :param target_column: target column nanem.
        :return: a data frame contains the prediction in target column.
        """
        settings = self.automl_settings
        X_transformed = grain_inf_context.transformed_grain_df
        forecast_origin = grain_inf_context.forecast_origin
        required_horizon = (X_transformed.reset_index()[time_column] >= forecast_origin).sum()
        saved_data = grain_inf_context.context_grain_df
        y_transformed = X_transformed.pop(target_column)

        target_column = ForecastConstant.automl_constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN
        time_column = settings[ForecastConstant.time_column_name]
        y_pred = y_transformed.copy()
        if isinstance(y_pred, pd.DataFrame):
            y_pred = y_pred.values

        window_index = len(y_pred) - required_horizon  # forecast origin for the first horizon.
        horizons_left = required_horizon

        partial_horizon = required_horizon % horizon
        padding_len = 0
        # need to pad X_transform and y_transform to full horizon.
        if (partial_horizon > 0):
            # Since we do not predict the series beyond the required
            # replicating last data item to complete the model horizon
            # as the model predict one horizon at a time and we need less
            # than horizon to return back.
            padding_len = horizon - partial_horizon
            y_pad = np.empty(padding_len)
            y_pad.fill(np.nan)
            y_pred = np.concatenate((y_pred, y_pad), axis=0)
            X_transformed = self._right_pad_transformed_data(X_transformed, padding_len)
        while horizons_left > 0:
            start_index = window_index - lookback if window_index > lookback else 0
            end_index = window_index + horizon
            X_infer = X_transformed.iloc[start_index:end_index]
            y_infer = y_pred[start_index:end_index]
            y_pred_horizon = self._predict_horizon(X_infer, y_infer, lookback, horizon, saved_data, **kwargs)
            y_pred[window_index:window_index + horizon] = y_pred_horizon.reshape(-1)
            horizons_left -= horizon
            window_index += horizon
        X_transformed[target_column] = y_pred
        return X_transformed

    def _predict_horizon(self, X_transformed: pd.DataFrame, y_transformed: pd.DataFrame,
                         looback: int,
                         horizon: int,
                         saved_data,
                         **kwargs) -> np.ndarray:
        """Return the predictions for the passed in X and y values.

        :param X_transformed: Tramsformed DataFrame
        :param y_tranformed: label values corresponding to the transformed data.
        :param looback: look back of the data.
        :param horizon: horizon related to this model.
        :param saved_data: saved context if dataset does not have enough context.
        :return: a ndarray of one horizon predictions
        """
        assert X_transformed.shape[0] >= 1
        inference_dataset = TimeSeriesInferenceDataset(X_transformed, y_transformed, saved_data, horizon, looback,
                                                       None, True, self._sample_transform, **self.automl_settings)
        if kwargs.get('if_forecast_quantile'):
            return self._predict_quantile(inference_dataset)
        return self._predict(inference_dataset)

    def _rolling_forecast_internal(self, preprocessors: List[Any], forecaster: Any,
                                   Xy_ts_features: pd.DataFrame,
                                   step: int,
                                   ignore_data_errors: bool) -> pd.DataFrame:
        """
        Produce forecasts on a rolling origin over a test set.

        This method contains the internal logic for making a rolling forecast for a DNN model.
        The input data frame is assumed to contain regular, full, featurized timeseries. That is, no observation
        gaps or missing target values and all features needed by the model should be present.
        """
        # append context from training and pad the end so we have full horizon windows
        Contract.assert_value(self._data_for_inference, '_data_for_inference', log_safe=True)
        lookback = self.get_lookback()
        horizon = self.max_horizon
        df_list: List[pd.DataFrame] = []
        X_lb_gby = self._data_for_inference.groupby(self.grain_column_names)
        for tsid, df_one in Xy_ts_features.groupby(self.grain_column_names):
            Contract.assert_true(tsid in X_lb_gby.groups,
                                 'Missing lookback data for at least one series in the test data.', log_safe=True)
            df_lb_one = X_lb_gby.get_group(tsid)

            # Make sure context has the expected index
            if set(df_lb_one.index.names) != set(df_one.index.names):
                Contract.assert_true(set(df_one.index.names) <= set(df_lb_one.columns),
                                     'Lookback data missing required columns for index.', log_safe=True)
                df_lb_one.set_index(df_one.index.names, inplace=True)

            Contract.assert_true(set(df_one.columns) == set(df_lb_one.columns),
                                 'Expected prediction data and context data to have same column set.',
                                 log_safe=True)
            df_combined_one = pd.concat([df_lb_one, df_one])

            # Check if the end of the series needs padding
            # Padding is used internally so that the data loader returns tensors with a consistent size.
            # The padded values and forecasts associated with padded rows are not returned to the user.
            # We will right pad the data only if the number of rows in df_one is not divisible by
            # horizon.
            n_windows = np.ceil((df_one.shape[0] - horizon) / step + 1).astype(int)
            required_len = (n_windows - 1) * step + horizon if n_windows > 0 else horizon
            padding_len = required_len - df_one.shape[0]
            if padding_len > 0:
                df_combined_one = self._right_pad_transformed_data(df_combined_one, padding_len)
            df_list.append(df_combined_one)

        Xy_pred = pd.concat(df_list)

        # Make a torch-compatible dataset
        X_pred = Xy_pred
        y_pred = X_pred.pop(self.target_column_name).to_frame()

        # Define the numericalized columns
        numericalized_grain_colnames = self._get_numericalized_column_names()
        ds_pred = TimeSeriesDataset(X_pred, y_pred, horizon,
                                    step=step,
                                    has_past_regressors=True,
                                    sample_transform=self._sample_transform,
                                    is_train_set=False,
                                    featurized_ts_id_names=numericalized_grain_colnames,
                                    **self.automl_settings)
        ds_pred.set_lookback(lookback)

        # Create a torch DataLoader that will not shuffle the samples
        dl_pred = self.create_data_loader(ds_pred, False)

        # Send the samples through the DNN and get an array of forecasts
        fcsts = self._predict(data_loader=dl_pred).squeeze()
        # If we have one grain and we are predicting for one forecast horizon,
        # squeeze call will result in 1D array, which is not expected
        # in the code below.
        if len(ds_pred) == 1:
            fcsts = np.array([fcsts])

        # Post-process the forecasts array
        # Assume that the Dataset index can be used as a row index in the forecasts array.
        # This should be safe since the data loader did not shuffle the samples.
        Contract.assert_true(fcsts.shape[0] == len(ds_pred),
                             'Unexpected number of forecasts in forecasts array', log_safe=True)
        Contract.assert_true(fcsts.shape[1] == horizon,
                             'Unexpected forecast horizon in forecasts array', log_safe=True)
        df_fcst_list: List[pd.DataFrame] = []
        for idx in range(len(ds_pred)):
            y_fcst = fcsts[idx, :]
            df_samp, _ = ds_pred.get_sample_data_from_idx(idx)
            df_samp_lb = df_samp.iloc[:-horizon]
            df_samp_pred = df_samp.iloc[-horizon:]
            Contract.assert_true(df_samp_pred.shape[0] == y_fcst.shape[0],
                                 'Sample prediction frame length does not match DNN forecast length.', log_safe=True)
            Contract.assert_true(df_samp_pred.index.names == X_pred.index.names,
                                 'Sample prediction frame missing required index levels.', log_safe=True)
            fcst_origin_time = df_samp_lb.index.get_level_values(self.time_column_name)[-1]

            df_samp_fcst = pd.DataFrame({self.forecast_origin_column_name: fcst_origin_time,
                                         self.forecast_column_name: y_fcst}, index=df_samp_pred.index)
            # Inversing the predictions for each batch and update the reference point for next batch.
            # We are not supporting stationarity transform in TCN and hence setting stationarity
            # transform to None.
            y = df_samp_fcst.pop(self.forecast_column_name).values
            df_samp_fcst[self.forecast_column_name] = self._convert_target_type_maybe(y)
            df_fcst_list.append(df_samp_fcst)

        X_fcst = pd.concat(df_fcst_list)
        X_fcst.reset_index(inplace=True)
        return X_fcst

    def _get_numericalized_column_names(self) -> Optional[List[str]]:
        """
        Return the names of numericalized grain columns.

        :return: The list of column names or None.
        """
        numericalized_grain_colnames = None
        for step in self._pre_transform.pipeline.steps:
            if step[0] == constants.TimeSeriesInternal.MAKE_GRAIN_FEATURES:
                numericalized_grain_colnames = step[
                    1]._preview_grain_feature_names_from_grains(self._pre_transform.grain_column_names)
        return numericalized_grain_colnames

    @classmethod
    def _try_set_time_column_data_type(cls, X: pd.DataFrame, time_column):
        try:
            if X.dtypes[time_column] != np.dtype('datetime64[ns]'):
                X = X.astype({time_column: 'datetime64[ns]'}, )
        except ValueError:
            pass
        return X

    @classmethod
    def _get_grain_forecast_origin(
            cls, X: pd.DataFrame, time_column: str, target_column: str) -> int:
        if np.any(np.isnan(X[target_column])):
            return min(X[pd.isnull(X[target_column])][time_column])
        else:
            raise DataException._with_error(
                AzureMLError.create(TimeseriesNothingToPredict), target="X",
                reference_code=ReferenceCodes._TCN_NOTHING_TO_PREDICT
            )

    def parse_parameters(self) -> DNNParams:
        """Parse parameters from command line.

        :return: returns the  DNN  param object from the command line arguments
        """
        raise NotImplementedError

    def init_model(self, settings: dict = None) -> None:
        """Initialize the model using the command line parse method.

        :param settings: automl settings such as lookback and horizon etc.
        :return:
        """
        self.params = self.parse_parameters()
        for item in settings if settings else {}:
            self.params.set_parameter(item, settings[item])

    def set_transforms(self, input_channels: int, sample_transform: Any = None) -> None:
        """Set the the training data set transformations and channels.

        :param input_channels: Number of features in tne dataset.
        :param sample_transform: transformations applied as part of tcn dataset processing.
        :return:
        """
        if self.input_channels is None:
            self.input_channels = input_channels

        if self._sample_transform is None:
            self._sample_transform = sample_transform

    def create_data_loader(
            self,
            ds: TimeSeriesDataset,
            shuffle: Optional[bool] = None,
            batch_size: Optional[int] = None,
            sampler: Optional[DistributedSampler] = None,
            num_workers: Optional[int] = None,
            drop_last: Optional[bool] = False) -> DataLoader:
        """Create the dataloader from time series dataset.

        :param ds: TimeseriesDataset
        :param shuffle: to shuffle the data for batching. If set to None, sampler should be provided.
        :param batch_size:  batch size for the training.
        :param sampler: data sampler.
        :param num_workers: number of workers for the data loader.
        :return:
        """
        # Both shuffle and sampler cannot be provided. This is because pyTorch throws an error in
        # this case. If sampler is provided, it knows how to shuffle the data. Hence, shuffle is not
        # needed.
        if shuffle is not None:
            Contract.assert_true(
                sampler is None,
                "Shuffle should not be set with sampler",
                reference_code=ReferenceCodes._TS_SHUFFLE_AND_SAMPLER_PROVIDED_TOGETHER,
                target="timeseries_dnn_dataloader",
                log_safe=True
            )
        if batch_size is None:
            batch_size = self.params.get_value(ForecastConstant.Batch_size)

        self.set_transforms(ds.feature_count(), ds.sample_transform)

        if num_workers is None:
            num_workers = self._get_num_workers_data_loader(dataset=ds)

        return DataLoader(
            ds,
            batch_size=batch_size,
            shuffle=shuffle,
            num_workers=num_workers,
            pin_memory=True,
            sampler=sampler,
            drop_last=drop_last)

    def _check_data(self, X_pred: pd.DataFrame,
                    y_pred: Union[pd.DataFrame, np.ndarray],
                    forecast_destination: Optional[pd.Timestamp] = None) -> None:
        # bypass check data for dnn model here.
        if forecast_destination is not None:
            raise ConfigException._with_error(
                AzureMLError.create(
                    NotSupported,
                    target="forecast_destination",
                    scenario_name="forecasting TCN model",
                    reference_code=ReferenceCodes._TCN_INFER_FORECAST_DESTINATION_UNSUPPORT)
            )

    def _get_preprocessors_and_forecaster(self) -> Tuple[List[Any], Any]:
        """Get list of preprocessors and forecaster."""
        # In this case, the forecaster is the wrapper object itself as it owns the predict method.
        # For DNN this method is really just a placeholder since it doesn't need to support the
        # classical model extension API
        return [self._pre_transform], self

    def _forecast_internal(self, preprocessors: List[Any], forecaster: Any, X_in: pd.DataFrame,
                           ignore_data_errors: bool) -> pd.DataFrame:
        """Get the forecast on the input data."""
        # For the DNN, there is no extension necessary (TCN is extendable by default) so just call
        # the TCN forecaster here and ignore preproc list and forecaster input.
        y = X_in.pop(self.target_column_name)
        return self.forecast(X_in, y)[1]

    def _get_not_none_ts_transformer(self) -> TimeSeriesTransformer:
        return self.ts_transformer

    @staticmethod
    def _get_num_workers_data_loader(dataset: TimeSeriesDataset) -> int:
        """Get count of number of workers to use for loading data.

        :param dataset: TimeseriesDataset that will be loaded with num workers.
        :return: returns number of workers to use
        """
        # on win using num_workers causes spawn of processes which involves pickling
        # loading data in main process is faster in that case
        if sys.platform == 'win32':
            return 0
        num_cpu_core = None
        try:
            import psutil
            num_cpu_core = psutil.cpu_count(logical=False)
        except Exception:
            import os
            num_cpu_core = os.cpu_count()
            if num_cpu_core is not None:
                # heuristics assuming 2 hyperthreaded logical cores per physical core
                num_cpu_core /= 2

        if num_cpu_core is None:
            # Default to 0 to load data in main thread memory
            return 0
        else:
            # Divide the number of cpu cores by number of horovod processes.
            return int(num_cpu_core / DistributedHelper.local_processes_count())

    @staticmethod
    def get_arg_parser_name(arg_name: str):
        """Get the argument name needed for arg parse.(prefixed with --).

        :param arg_name: argument name to convert to argparser format.
        :return:

        """
        return "--{0}".format(arg_name)

    @property
    def automl_settings(self) -> Dict[str, Any]:
        """Get automl settings for data that model is trained on."""
        settings = self.params.get_value(ForecastConstant.automl_settings)
        return settings.copy() if settings else {}

    @property
    def primary_metric(self) -> str:
        """Get the primary the model is trained on."""
        metric = self.automl_settings.get(ForecastConstant.primary_metric, None)
        if metric is None:
            metric = self.params.get(ForecastConstant.primary_metric)
        return metric

    @property
    def name(self):
        """Name of the Model."""
        raise NotImplementedError

    @property
    def ts_transformer(self) -> 'TimeSeriesTransformer':
        """Timeseries transformer for data featurization."""
        return self._pre_transform

    def __getstate__(self) -> Dict[str, Any]:
        """
        Get state pickle-able objects.

        :return: state
        """
        state = dict(self.__dict__)

        # This is assuming that model is used for inference.
        # callbacks need to be created and set on the forecaster for retraining
        # with the new dataset
        state['loss_dict'] = {}
        state['optimizer_dict'] = {}
        if self.forecaster:
            if self.forecaster.loss:
                state['loss_dict'] = self.forecaster.loss.state_dict()
            if self.forecaster.optimizer:
                state['optimizer_dict'] = self.forecaster.optimizer.state_dict()
        state['forecaster'] = None
        return state

    def __setstate__(self, state) -> None:
        """
        Set state for object reconstruction.

        :param state: pickle state
        """
        self.__dict__.update(state)

    def forecast_quantiles(
            self,
            X_pred: Optional[pd.DataFrame] = None,
            y_pred: Optional[Union[pd.DataFrame, np.ndarray]] = None,
            quantiles: Optional[Union[float, List[float]]] = None,
            forecast_destination: Optional[pd.Timestamp] = None,
            ignore_data_errors: bool = False) -> pd.DataFrame:
        """
        Get the predictions at the requested quantiles from the fitted pipeline.

        :param X_pred: The prediction dataframe combining X_past and X_future in a time-contiguous manner.
                       Empty values in X_pred will be imputed.
        :param y_pred: The target value combining definite values for y_past and missing values for Y_future.
                       If None the predictions will be made for every X_pred.
        :param quantiles: The list of quantiles at which we want to forecast.
        :type quantiles: float or list of floats
        :param forecast_destination: Forecast_destination: a time-stamp value.
                                     Forecasts will be made all the way to the forecast_destination time,
                                     for all grains. Dictionary input { grain -> timestamp } will not be accepted.
                                     If forecast_destination is not given, it will be imputed as the last time
                                     occurring in X_pred for every grain.
        :type forecast_destination: pandas.Timestamp
        :param ignore_data_errors: Ignore errors in user data.
        :type ignore_data_errors: bool
        :return: A dataframe containing the columns and predictions made at requested quantiles.
        """
        default_quantiles = self.quantiles
        if quantiles:
            self.quantiles = quantiles
        _, forecast_df = self._scenario_forecast(
            ForecastingPipelineWrapperBase._FORECAST_SCENARIO_FORECAST_QUANTILES,
            X_pred, y_pred,
            forecast_destination=forecast_destination, ignore_data_errors=ignore_data_errors,
            pred=None, transformed_data=None
        )
        self.quantiles = default_quantiles
        return forecast_df

    def _scenario_forecast_automl(
            self,
            forecast_scenario: str,
            X_pred: Optional[pd.DataFrame],
            y_pred: Optional[Union[pd.DataFrame, np.ndarray]],
            Xy_pred_in: pd.DataFrame,
            ignore_data_errors: bool,
            step: int,
            dict_rename_back: Optional[Dict[str, Any]],
            forecast_destination: Optional[pd.Timestamp] = None,
            preprocessors: Optional[List[Any]] = None,
            forecaster: Optional[Any] = None,
            pred: Optional[np.ndarray] = None,
            transformed_data: Optional[np.ndarray] = None
    ) -> Tuple[Optional[np.ndarray], pd.DataFrame]:
        forecast = None
        if forecast_scenario == ForecastingPipelineWrapperBase._FORECAST_SCENARIO_ROLLING_FORECAST:
            Contract.assert_non_empty(preprocessors, "preprocessors", log_safe=True)
            forecast_df = self._pipeline_rolling_forecast_internal(
                Xy_pred_in, step, cast(List[Any], preprocessors), forecaster, ignore_data_errors)
        elif forecast_scenario == ForecastingPipelineWrapperBase._FORECAST_SCENARIO_FORECAST_QUANTILES:
            forecast_df = self._pipeline_forecast_quantiles_internal(
                X_pred, Xy_pred_in, ignore_data_errors)
        else:
            forecast, forecast_df = self._pipeline_forecast_internal(
                X_pred, y_pred, Xy_pred_in, dict_rename_back, forecast_destination,
                ignore_data_errors, preprocessors, forecaster)
        return forecast, forecast_df

    def _get_forecast_columns_in_results(self, forecast_scenario: str, X_pred: pd.DataFrame) -> Optional[List[str]]:
        columns_in_results = None
        if forecast_scenario == ForecastingPipelineWrapperBase._FORECAST_SCENARIO_ROLLING_FORECAST:
            effective_ts_ids = self._get_effective_time_series_ids(X_pred)
            # Sort by tsid, forecasting origin, and time, respectively.
            sort_columns: List[Any] = effective_ts_ids.copy() if effective_ts_ids is not None else []
            sort_columns.extend([self.forecast_origin_column_name, self.time_column_name])
            columns_in_results = sort_columns + [self.forecast_column_name, self.actual_column_name]
        elif forecast_scenario == ForecastingPipelineWrapperBase._FORECAST_SCENARIO_FORECAST_QUANTILES:
            pass
        return columns_in_results
