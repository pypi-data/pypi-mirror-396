# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module for creating training dataset from dapaprep Dataflow object."""
import dataclasses
import logging
import math
from typing import Any, Callable, Dict, List, Optional, Sequence, Set, Tuple, Union

import forecast.data.transforms as tfs
import numpy as np
import pandas as pd
import torch
from azureml._common._error_definition import AzureMLError
from azureml._common._error_definition.user_error import ArgumentBlankOrEmpty, NotReady

from forecast.data import FUTURE_DEP_KEY, FUTURE_IND_KEY, PAST_DEP_KEY, PAST_IND_KEY
from forecast.data.sources.data_source import DataSourceConfig
from forecast.data.sources.data_source import EncodingSpec
from torch.utils.data import Dataset

from azureml.automl.core.shared.constants import TimeSeries
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.core.shared._diagnostics.automl_error_definitions import TCNExtraColumnInPrediction
from azureml.automl.core.shared.constants import TimeSeriesInternal
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.core.shared.exceptions import ClientException, DataException
from azureml.automl.runtime.column_purpose_detection import ColumnPurposeDetector
from azureml.contrib.automl.dnn.forecasting.wrapper import _wrapper_util

from ..constants import FeatureType, ForecastConstant, DROP_COLUMN_LIST, TCNForecastParameters
from azureml.automl.runtime.experiment_store import ExperimentStore
from azureml.dataprep.api.dataprofile import ColumnProfile, DataProfile

logger = logging.getLogger(__name__)


class EmbeddingColumnInfo:
    """This class holds a name, index and unique number of items in the column."""

    def __init__(self,
                 name: str,
                 index: int,
                 distinct_values: int):
        """
        Create a structure with grain name, index in the transformed dataset and count of distinct grain values.

        :param name: Name of a column in the timeseries grain.
        :param index: Index of the grain column in the transformed data.
        :param distinct_values: Number of distinct values in the grain column.
        """
        self.name = name
        self.index = index
        self.distinct_values = distinct_values


class _DataGrainItem:
    """This class holds a slice of feature and label."""

    def __init__(self,
                 X_df: pd.DataFrame,
                 y: np.ndarray,
                 grain_id: Tuple[np.number],
                 lookup_start_ix: int = 0,
                 lookup_end_ix: int = None,
                 offset: int = 0,
                 unknown_columns_to_drop: List[str] = None):
        self.X_df = X_df
        self.y = y
        self.grain_id = grain_id
        self.lookup_start_ix = lookup_start_ix
        self.lookup_end_ix = lookup_end_ix
        self.offset = offset
        self._unknown_columns_to_drop = unknown_columns_to_drop

        Contract.assert_true(self.X_df.shape[0] == self.y.shape[-1],
                             "X({}) and y({}) have inconsistent shapes.".format(X_df.shape[0], y.shape[-1]),
                             log_safe=True)

        if lookup_end_ix:
            Contract.assert_true(self.lookup_end_ix > self.lookup_start_ix,
                                 "lookup_end_ix ({}) should be greater than lookup_start_ix ({})".format(
                                     lookup_end_ix, lookup_start_ix), log_safe=True)
        self.X_T = _DataGrainItem._transpose_to_np(X_df.iloc[:, 1:], dtype=np.float32)
        if unknown_columns_to_drop is not None:
            self.X_T_future = _DataGrainItem._transpose_to_np(
                X_df.drop(unknown_columns_to_drop, inplace=False, axis=1).iloc[:, 1:], dtype=np.float32)
        else:
            self.X_T_future = self.X_T.copy()

    @property
    def X(self):
        """Get the numeric array of data frame needed for training sample."""
        return self.X_df.to_numpy()

    @staticmethod
    def _transpose_to_np(X: pd.DataFrame, dtype: np.dtype):
        """
        Convert the pandas dataframe to transposed numpy array.

        Use this method can avoid numpy/pandas inferring data types during transpose. It will also convert to the
        corresponding datatypes when doing conversion.
        """
        return X.to_numpy(dtype=dtype).T


@dataclasses.dataclass
class _GrainAndStatistics:
    """The class, keeping grain statistics."""

    grain_item: _DataGrainItem
    offsets: np.ndarray
    offset_y: np.number
    scales: np.ndarray
    scale_y: np.number

    def __post_init__(self):
        """Validate scales and offsets."""
        Contract.assert_true(len(self.offsets.shape) == 1, target="offsets_rows",
                             message='Regressor means have wrong number of rows.',
                             reference_code=ReferenceCodes._TCN_DATASET_OFFSETS_WRONG_ROWS)
        Contract.assert_true(len(self.scales.shape) == 1, target="scales_rows",
                             message="Regressor standard deviations have wrong number of rows.",
                             reference_code=ReferenceCodes._TCN_DATASET_SCALES_WRONG_ROWS)
        # Check that offsets are numbers.
        Contract.assert_true(all(np.isfinite(self.offsets)), target='offsets_nan_inf',
                             message='Mean of regressor is nan of inf.',
                             reference_code=ReferenceCodes._TCN_DATASET_OFFSETS_NAN_OR_INF)
        Contract.assert_true(np.isfinite(self.offset_y), target='offset_y_nan_inf',
                             message='Mean of target is nan of inf.',
                             reference_code=ReferenceCodes._TCN_DATASET_OFFSET_Y_NAN_OR_INF)
        # Check that scales are numberes.
        Contract.assert_true(all(np.isfinite(self.scales)), target='scales_nan_inf',
                             message='Standard deviation of regressor is nan of inf.',
                             reference_code=ReferenceCodes._TCN_DATASET_SCALES_NAN_OR_INF)
        Contract.assert_true(np.isfinite(self.scale_y), target='scale_y_nan_inf',
                             message='Standard deviation of target is nan of inf.',
                             reference_code=ReferenceCodes._TCN_DATASET_SCALE_Y_NAN_OR_INF)
        # Check scale is non negative
        Contract.assert_true(all(scale >= 0 for scale in self.scales), target='scales',
                             message='Standard deviation of regressor is negative.',
                             reference_code=ReferenceCodes._TCN_DATASET_SCALES_NEGATIVE)
        Contract.assert_true(self.scale_y > 0, target='scale_y',
                             message='Standard deviation of target is negative.',
                             reference_code=ReferenceCodes._TCN_DATASET_SCALE_Y_NEGATIVE)
        # Check if scales and offsets has the same shape.
        Contract.assert_true(self.offsets.shape == self.scales.shape, target='offset_scale_shape',
                             message='Regressors standard deviations and means have different dimensions.',
                             reference_code=ReferenceCodes._TCN_DATASET_SCALES_OFFSETS_DIFF_SHAPE)

# Copied here temporarily, it will be imported from automl.client.core.runner.model_wrappers.


class ForecastingErrors:
    """Forecasting errors."""

    # Constants for errors and warnings
    # Non recoverable errors.
    FATAL_WRONG_DESTINATION_TYPE = ("The forecast_destination argument has wrong type, "
                                    "it is a {}. We expected a datetime.")
    FATAL_DATA_SIZE_MISMATCH = "The length of y_pred is different from the X_pred"
    FATAL_WRONG_X_TYPE = ("X_pred has unsupported type, x should be pandas.DataFrame, "
                          "but it is a {}.")
    FATAL_WRONG_Y_TYPE = ("y_pred has unsupported type, y should be numpy.array or pandas.DataFrame, "
                          "but it is a {}.")
    FATAL_NO_DATA_CONTEXT = ("No y values were provided for one of grains. "
                             "We expected non-null target values as prediction context because there "
                             "is a gap between train and test and the forecaster "
                             "depends on previous values of target. ")
    FATAL_NO_DESTINATION_OR_X_PRED = ("Input prediction data X_pred and forecast_destination are both None. "
                                      "Please provide either X_pred or a forecast_destination date, but not both.")
    FATAL_DESTINATION_AND_X_PRED = ("Input prediction data X_pred and forecast_destination are both set. "
                                    "Please provide either X_pred or a forecast_destination date, but not both.")
    FATAL_X_Y_XOR = "X_pred and y_pred should both be None or both not None."
    FATAL_NO_LAST_DATE = ("The last training date was not provided."
                          "One of grains in scoring set was not present in training set.")
    FATAL_EARLY_DESTINATION = ("Input prediction data X_pred or input forecast_destination contains dates "
                               "prior to the latest date in the training data. "
                               "Please remove prediction rows with datetimes in the training date range "
                               "or adjust the forecast_destination date.")
    FATAL_NO_TARGET_IN_Y_DF = ("The y_pred is a data frame, "
                               "but it does not contain the target value column")
    FATAL_WRONG_QUANTILE = "Quantile should be a number between 0 and 1 (not inclusive)."
    FATAL_NO_TS_TRANSFORM = ("The time series transform is absent. "
                             "Please try training model again.")

    FATAL_NO_GRAIN_IN_TRAIN = ("One of grains was not present in the training data set. "
                               "Please remove it from the prediction data set to proceed.")
    FATAL_NO_TARGET_IMPUTER = 'No target imputers were found in TimeSeriesTransformer.'
    FATAL_NONPOSITIVE_HORIZON = "Forecast horizon must be a positive integer."


class DNNTimeSeriesDatasetBase(Dataset):
    """This class provides a base class for Time Series datasets."""

    @staticmethod
    def _drop_extra_columns(X: pd.DataFrame, inplace: bool = False) -> pd.DataFrame:
        drop_columns = []
        for col in X.columns:
            if col in DROP_COLUMN_LIST:
                drop_columns.append(col)
        if drop_columns:
            return X.drop(drop_columns, inplace=inplace, axis=1)
        return X

    def __init__(self,
                 horizon: int,
                 lookback: Optional[int],
                 step: int = 1,
                 thinning: float = 1.0,
                 has_past_regressors: bool = False,
                 sample_transform: Any = None,
                 fetch_y_only: bool = False,
                 training_data: tuple = None,
                 dset_config: DataSourceConfig = None,
                 data_grains: List[_DataGrainItem] = None,
                 embedding_col_infos: List[EmbeddingColumnInfo] = [],
                 sample_count: int = None,
                 cross_validation: int = None,
                 unknown_columns_to_drop: List[str] = None
                 ):
        """
        Take a training data(X) and label(y) and provides access to windowed subseries for torch DNN training.

        :param horizon: Number of time steps to forecast.
        :param lookback: lookback for this class.
        :param step: Time step size between consecutive examples.
        :param thinning: Fraction of examples to include.
        :param has_past_regressors: data to populate past regressors for each sample
        :param sample_transform: per-sample feature transforms to use
        :param fetch_y_only: Get only the target value.
        :param training_data: X and Y and settings saved in dataset if needed to created lookback.
        :param dset_config: Get only the target value.
        :param data_grain: Slices of data grain and the indexes to lookup the training sample.
        :param embedding_col_infos: List of grain columns index, count and name.
        :param sample_count: Number of samples in the dataset(with lookback and horizon).
        :param cross_validation: Sliding test data used for metrics.
        """
        self.horizon = horizon
        self.step = step
        self.thinning = thinning
        self.sample_transform = sample_transform
        self._keep_untransformed = False
        self.has_past_regressors = has_past_regressors
        self._len = sample_count
        self.lookback = lookback
        self.fetch_y_only = fetch_y_only
        self._training_data = training_data
        self.dset_config = dset_config
        self._cache = {}
        self._data_grains = data_grains
        self.embedding_col_infos = embedding_col_infos
        self.cross_validation = cross_validation
        self.numericalized_grain_cols: List[int] = []
        # The `forecast` submodule / library requires this property to be set
        self.transform = None
        self._unknown_columns_to_drop = unknown_columns_to_drop

    @property
    def keep_untransformed(self):
        """Whether to return data untransformed."""
        return self._keep_untransformed

    def __len__(self) -> int:
        """Return the number of samples in the dataset.

        :return: number of samples.
        """
        return self._len

    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        """
        Get the idx-th training sample item from the dataset.

        :param idx: the item to get the sample.
        :return: returns the idx-th sample.
        """
        if self._len is None:
            raise ClientException._with_error(AzureMLError.create(
                NotReady, argument_name="Dataset not initialized, lookback for the dataset is not set",
                target="lookback", reference_code=ReferenceCodes._TCN_LOOKBACK_DATASET_NOT_SET)
            )
        idx2, data_grain = self._get_index_grain_from_lookup(idx)
        sample = self._getitem_from_df(data_grain, idx2)
        return sample

    def _get_data_grain_for_sample_idx(self, idx: int) -> _DataGrainItem:
        """
        Get the data grain corresponding to the idx-th sample index.

        This logic was pulled from / inspired by
        https://github.com/python/cpython/blob/6a1e9c26736259413b060b01d1cb52fcf82c0385/Lib/bisect.py#L26-L35.
        """
        lo = 0
        hi = len(self._data_grains)
        while lo < hi:
            mid = (lo + hi) // 2
            if idx < self._data_grains[mid].lookup_end_ix:
                hi = mid
            else:
                lo = mid + 1

        data_grain = self._data_grains[lo]
        Contract.assert_true(
            data_grain.lookup_start_ix <= idx < data_grain.lookup_end_ix,
            "Located data grain with lookup_start_idx ({}) and lookup_end_ix ({}) does not contain the \
                requested sample index ({}).".format(data_grain.lookup_start_ix, data_grain.lookup_end_ix, idx),
            log_safe=True)

        return data_grain

    def _get_index_grain_from_lookup(self, idx) -> Tuple[int, _DataGrainItem]:
        located_grain = self._get_data_grain_for_sample_idx(idx)

        # lookup index from the grain is the offset +
        # steps size * distance to the index from lookup start.
        lookup_index = located_grain.offset + self.step * (idx - located_grain.lookup_start_ix)
        return lookup_index, located_grain

    def _getitem_from_df(self, data_grain: _DataGrainItem, idx: int) -> Dict[str, torch.Tensor]:
        """
        Get the idx-th training sample item from the given grain.

        :param X: feature ndarray
        :param y: target array
        :param idx: the item to get the sample.
        :return: returns the idx-th sample.
        """
        if self.lookback is None:
            raise ClientException._with_error(
                AzureMLError.create(
                    ArgumentBlankOrEmpty, target="_getitem_from_df", argument_name="lookback",
                    reference_code=ReferenceCodes._TCN_LOOKBACK_NOT_SET)
            )
        # Get time series
        # The data values are transformed so the result is of the shape nfeatures X lookback for X
        # and 1 X horizon for y
        start_index = idx
        X = data_grain.X_df
        y = data_grain.y
        X_T = data_grain.X_T
        X_T_future = data_grain.X_T_future

        if self.has_past_regressors:
            y_past_tensor, y_fut_tensor = self._get_past_future_tensor(y, start_index)
            sample = {PAST_DEP_KEY: y_past_tensor, FUTURE_DEP_KEY: y_fut_tensor}
            if not self.fetch_y_only:
                X_past_tensor, x_fut_tensor = self._get_past_future_tensor(
                    X_T, start_index, X_T_future,
                    numericalized_grain_cols=self.numericalized_grain_cols)
                sample[PAST_IND_KEY] = X_past_tensor
                sample[FUTURE_IND_KEY] = x_fut_tensor
        else:
            # for evaluation use only. X and y won't get transposed.
            y_tensor = self._get_tensor(y[:, start_index + self.lookback:start_index + self.lookback + self.horizon])
            X_tensor = None
            if not self.fetch_y_only:
                X_tensor = self._get_tensor(X.to_numpy()[:, start_index:start_index + self.lookback])
            # Create the input and output for the sample
            sample = {'X': X_tensor, 'y': y_tensor}
        if self.sample_transform and not self.keep_untransformed:
            sample = self.sample_transform(sample)
        return sample

    def _get_past_future_tensor(
            self,
            X_T: np.ndarray,
            start_index: int,
            X_T_future: np.ndarray = None,
            numericalized_grain_cols: Optional[List[int]] = None,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Get past and future tensor from the grain.

        While start_index is being increased, we first are taking the slices of
        tensors if we have enough data. If the sum of lookback, start index and
        horizon is larger then the length of a tensor, we are jumping to the begin of a tensor
        and starting to pad. So if we have not enough data the tensors with higher indices
        will be at the begin of a data set and will be padded.
        :param X_T: The whole grain in a form of tensor.
        :param start_index: The starting index.
        :param X_T_future: The whole grain of future features in a form of tensor.
        :param numericalized_grain_cols: The indices of numericaized grain columns.
                                         The tensor is transposed so it will be a row.
        :return: The tuple with past and future tensor.
        """
        tensor_past_T, tensor_fut_T = self._get_past_future_tensor_helper(X_T, start_index, numericalized_grain_cols)
        if X_T_future is not None:
            _, tensor_fut_T = self._get_past_future_tensor_helper(X_T_future, start_index, numericalized_grain_cols)
        return tensor_past_T, tensor_fut_T

    def _get_past_future_tensor_helper(
            self,
            array_T: np.ndarray,
            start_index: int,
            numericalized_grain_cols: Optional[List[int]] = None,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Get past and future tensor from the grain.

        While start_index is being increased, we first are taking the slices of
        tensors if we have enough data. If the sum of lookback, start index and
        horizon is larger then the length of a tensor, we are jumping to the begin of a tensor
        and starting to pad. So if we have not enough data the tensors with higher indices
        will be at the begin of a data set and will be padded.
        :param array_T: The whole grain in a form of tensor.
        :param start_index: The starting index.
        :param numericalized_grain_cols: The indices of numericaized grain columns.
                                         The tensor is transposed so it will be a row.
        :return: The tuple with past and future tensor.
        """
        required_length = self.lookback + start_index + self.horizon
        if array_T.shape[-1] < required_length:
            padding = np.zeros_like(array_T[:, [0]])
            if numericalized_grain_cols:
                padding[numericalized_grain_cols, 0] = array_T[numericalized_grain_cols, 0]
            array_T = np.pad(
                array_T,
                pad_width=((0, 0), (required_length - array_T.shape[-1], 0)),
                mode='constant',
                constant_values=((0, 0), (padding, 0))
            )
            array_past_T = array_T[:, :self.lookback]
            array_fut_T = array_T[:, self.lookback:self.lookback + self.horizon]
        else:
            end_index = start_index + self.lookback + self.horizon
            array_item_T = array_T[:, start_index:end_index]
            array_past_T = array_item_T[:, :self.lookback]
            array_fut_T = array_item_T[:, self.lookback:]
        return self._get_tensor(array_past_T), self._get_tensor(array_fut_T)

    def _get_tensor(self, array: np.ndarray) -> torch.Tensor:
        return torch.tensor(array.astype(np.float32), dtype=torch.float)

    def get_sample_data_from_idx(self, idx: int) -> Tuple[pd.DataFrame, np.ndarray]:
        """
        Get the feature data frame and target array for the given sample index.

        This method is useful for assigning arrays of DNN forecasts to their corresponding timeseries IDs
        and aligning them to a time axis.
        """
        start_row, data_grain = self._get_index_grain_from_lookup(idx)
        end_row = start_row + self.lookback + self.horizon
        return data_grain.X_df.iloc[start_row:end_row], data_grain.y.reshape(-1)[start_row:end_row]

    def is_small_dataset(self) -> bool:
        """Return true if dataset is small."""
        if self._len is not None:
            return self._len < ForecastConstant.SMALL_DATASET_MAX_ROWS
        return True

    def feature_count(self) -> int:
        """Return the number of features in the dataset."""
        return self._data_grains[0].X_df.shape[1]

    def set_lookback(self, lookback: int) -> None:
        """
        Set lookback to be used with this dataset.

        :param lookback: Number of time steps used as input for forecasting.
        """
        self.lookback = lookback
        self._len = 0
        for item in self._data_grains:
            start_index = self._len
            size = self._get_size(item.y)
            self._len += size
            item.lookup_start_ix = start_index
            item.lookup_end_ix = self._len

    @property
    def grain_count(self) -> int:
        """Return the number of grains in the dataset."""
        return len(self._data_grains)


class TimeSeriesDataset(DNNTimeSeriesDatasetBase):
    """This class provides a dataset for training timeseries model with dataprep features and label."""

    _NO_GRAIN = (-1, )

    def __init__(self,
                 X_df: pd.DataFrame,
                 y_df: pd.DataFrame,
                 horizon: int,
                 step: int = 1,
                 thinning: float = 1.0,
                 has_past_regressors: bool = False,
                 one_hot: bool = False,
                 sample_transform: Any = None,
                 fetch_y_only: bool = False,
                 save_last_lookback_data: bool = False,
                 embedding_enabled: Optional[bool] = True,
                 featurized_ts_id_names: Optional[Sequence[str]] = None,
                 use_label_log_transform: bool = False,
                 is_train_set: bool = True,
                 **settings: Any
                 ):
        """
        Take a training data(X) and label(y) and provides access to windowed subseries for torch DNN training.

        :param X_dflow: Training features in pandas dataframe.
        :param y_dflow: Training label in in pandas dataframe with shape(row_count, 1).
        :param horizon: Number of time steps to forecast.
        :param step: Time step size between consecutive examples.
        :param thinning: Fraction of examples to include.
        :param has_past_regressors: data to populate past regressors for each sample
        :param one_hot: one_hot encode or not
        :param sample_transform: feature transforms to use
        :param fetch_y_only: read y only, so the rest of features are not untransformed.
        :param save_last_lookback_data: save last lookbackup from training for inference.
        :param embedding_enabled: embeding state, embedding will only applied if the embedding_calc_type is set
        :param featurized_ts_id_names: The names of the numericalized time series ID columns.
        :param use_label_log_transform: If true, we will use the log transform of a label.
        :param is_train_set: If it is a train data set, we will calculate the statistics,
                             otherwise offsets will be 0 and scale will be 1.
        :param settings:  series settings
        """
        super(TimeSeriesDataset, self).__init__(horizon,
                                                None,
                                                step=step,
                                                thinning=thinning,
                                                has_past_regressors=has_past_regressors,
                                                sample_transform=sample_transform,
                                                fetch_y_only=fetch_y_only,
                                                )
        # Grain map maps numericalize grain name to position in offsets and scales tensor.
        self.grain_map: Dict[Tuple[np.number], int] = {}
        self.embedded_columns: List[int] = []
        self.indicator_columns: List[int] = []
        self.use_label_log_transform: bool = use_label_log_transform

        if save_last_lookback_data:
            self._training_data = (X_df.copy(), y_df.copy(), settings)

        get_encodings, encodings = False, []
        if ForecastConstant.cross_validations in settings and settings[ForecastConstant.cross_validations] is not None:
            # Mitigation for auto cv. The fact that TCN is using n_cross_validations is
            # confusing since TCN doesn't do cross-validations.
            # TODO: https://msdata.visualstudio.com/Vienna/_workitems/edit/1835174
            if settings[ForecastConstant.cross_validations] == TimeSeries.AUTO:
                settings[ForecastConstant.cross_validations] = ForecastConstant.NUM_EVALUATIONS_DEFAULT
                logging.warning(
                    f"TCNs do not support cross-validation, defaulting to a validation set of 10 forecast horizons \
                    ({horizon + 9} timesteps)."
                )
            self.cross_validation = int(settings[ForecastConstant.cross_validations])
        if one_hot:
            get_encodings = True
        self._drop_extra_columns(X_df, inplace=True)

        grains = settings.get(ForecastConstant.grain_column_names, None) if settings else None

        self._unknown_features = settings.get(
            ForecastConstant.features_unknown_at_forecast_time, None) if settings else None

        if get_encodings:
            encodings = self._get_encoding(X_df)

        if embedding_enabled:
            self.embedding_col_infos = self._get_embedding(X_df, TCNForecastParameters.EMBEDDING_THRESHOLD)
            embed_col_list = [embed_col.name for embed_col in self.embedding_col_infos]
            self.embedded_columns = [
                i for i, col in enumerate(
                    X_df.columns) for embed_col in embed_col_list if col == embed_col]

        exp_store = self._get_experiment_store_maybe()
        if is_train_set:
            # If the column consists only from 1-s and 0-s, we call it an
            # indicator. These columns have to be excluded from normalization.
            # In the code below we first check if data, obtained
            # from data profile contains information about each column and if it does not,
            # we check the values to figure out if it is an indicator column.
            dict_indicator_col_data = {}
            if exp_store is not None:
                dict_indicator_col_data = exp_store.metadata.timeseries.get_indicator_columns_data()
            non_indicator_columns = {ForecastConstant.automl_constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN,
                                     settings.get(ForecastConstant.automl_constants.TimeSeries.TIME_COLUMN_NAME)}
            if featurized_ts_id_names:
                non_indicator_columns = non_indicator_columns.union(set(featurized_ts_id_names))

            for i, col in enumerate(X_df.columns):
                if col in non_indicator_columns:
                    continue
                if (
                    dict_indicator_col_data.get(col, False)
                    or (
                        col not in dict_indicator_col_data
                        and np.array_equal(np.sort(X_df[col].unique()), np.array([0, 1]))
                    )
                ):
                    self.indicator_columns.append(i)
        if self._unknown_features is not None:
            if isinstance(self._unknown_features, str):
                self._unknown_features = [self._unknown_features]
            columns_to_drop = list(set(self._unknown_features).intersection(set(X_df.columns)))
            featurized_columns_to_drop = []
            for column in columns_to_drop:
                featurized_columns_to_drop.append(column + "_WASNULL")
            columns_to_drop = list(set(columns_to_drop + featurized_columns_to_drop).intersection(set(X_df.columns)))
            self._unknown_columns_to_drop = columns_to_drop
            X_df_fut = X_df.drop(self._unknown_columns_to_drop, inplace=False, axis=1)
            self._future_channels = X_df_fut.shape[1]
        else:
            self._unknown_columns_to_drop = None
            self._future_channels = X_df.shape[1]
        self.dset_config = DataSourceConfig(feature_channels=X_df.shape[1],
                                            forecast_channels=1,
                                            encodings=encodings)

        self._data_grains = []

        offsets_list, offsets_list_y = [], []
        scales_list, scales_list_y = [], []
        Contract.assert_true(ForecastConstant.automl_constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN not in X_df,
                             message='Target is present in regressors.', target='X',
                             reference_code=ReferenceCodes._TCN_TARGET_PRESENT)
        X_df.insert(0, ForecastConstant.automl_constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN,
                    y_df.values)

        if grains:
            if isinstance(grains, str):
                grains = [grains]
            self._grain_column_names = grains
            Contract.assert_value(featurized_ts_id_names, 'featurized_grain_column_names',
                                  reference_code=ReferenceCodes._TCN_NUMERICALIZED_TS_ID_ABSENT)
            # In the next lines we are temporarily adding target into a data frame.
            # We need to remember the indices of numericalized grain_num columns.
            # We decrease values by one, because target was inserted into position 0.
            self.numericalized_grain_cols = [
                i - 1 for gcol in featurized_ts_id_names for i, col in enumerate(X_df.columns) if col == gcol]

            # Note, we will group the data frame by the numericalized grain columns.
            for grain_num, X_one in X_df.groupby(featurized_ts_id_names):
                if not isinstance(grain_num, tuple):
                    grain_num = (grain_num, )
                grain_and_stats = self._get_or_calculate_statistics(
                    X_one, grains, grain_num, exp_store, is_train_set=is_train_set)
                self._data_grains.append(grain_and_stats.grain_item)
                offsets_list.append(grain_and_stats.offsets)
                offsets_list_y.append(grain_and_stats.offset_y)
                scales_list.append(grain_and_stats.scales)
                scales_list_y.append(grain_and_stats.scale_y)
                self.grain_map[grain_num] = len(self._data_grains) - 1

        else:
            self._grain_column_names = [TimeSeriesInternal.DUMMY_GRAIN_COLUMN]
            grain_and_stats = self._get_or_calculate_statistics(
                X_df, [TimeSeriesInternal.DUMMY_GRAIN_COLUMN],
                TimeSeriesDataset._NO_GRAIN, exp_store, is_train_set=is_train_set)
            self._data_grains.append(grain_and_stats.grain_item)
            offsets_list.append(grain_and_stats.offsets)
            offsets_list_y.append(grain_and_stats.offset_y)
            scales_list.append(grain_and_stats.scales)
            scales_list_y.append(grain_and_stats.scale_y)
            self.grain_map[TimeSeriesDataset._NO_GRAIN] = len(self._data_grains) - 1

        self.offsets = torch.from_numpy(np.array(offsets_list))  # type: torch.tensor
        self.scales = torch.from_numpy(np.array(scales_list))  # type: torch.tensor
        self.offsets_y = torch.from_numpy(np.array(offsets_list_y).reshape((-1, 1)))  # type: torch.tensor
        self.scales_y = torch.from_numpy(np.array(scales_list_y).reshape((-1, 1)))  # type: torch.tensor

        self.has_past_regressors = has_past_regressors
        if self.sample_transform is None and not self.fetch_y_only:
            self.sample_transform = self._get_sample_transform(one_hot)

    def _get_experiment_store_maybe(self) -> Optional[ExperimentStore]:
        """
        Return the experiment store if we have an instance or None otherwise.

        :return: ExperimentStore or None.
        """
        exp_store = None
        if ExperimentStore.has_instance():
            exp_store = ExperimentStore.get_instance()
        return exp_store

    def _get_or_calculate_statistics(
            self, X_one_grain: pd.DataFrame,
            grains: Sequence[str],
            grain: Tuple[np.number],
            exp_store: Optional[ExperimentStore],
            offset_fun: Callable[[np.ndarray], Union[np.ndarray, np.number]] = np.mean,
            scale_fun: Optional[Callable[[np.ndarray], Union[np.ndarray, np.number]]] = None,
            is_train_set: bool = True):
        """
        Get the statistics from dataprofile or calculate it if it is absent.

        :param X_df: The data frame to know the order of columns.
        :param grain: The tuple, denoting grain values.
        :param exp_store: The experiment store, which may contain the data profile.
        :param offset: The function to be applied to grain to get offset.
        :param scale: The function to be applied to grain to get scale.
        :param is_train_set: If it is a train data set, we will calculate the statistics,
                             otherwise offsets will be 0 and scale will be 1.
        :return: The class, holding grain item, offsets and scales of regressors and target.
        """
        if not is_train_set:
            # Do not calculate statistics if we are not on the train set.
            return self._get_validation_statistics(X_one_grain, grain)

        return self._get_statistics(X_one_grain, grain)

    def _get_columns_to_exclude_from_normalization(self) -> Set[str]:
        """
        Return the set of columns to be excluded from normalization.

        :return: The set of columns to be excluded from normalization.
        """
        return set(self.numericalized_grain_cols + self.embedded_columns + self.indicator_columns)

    def _get_stats_from_profile(
            self, X_one_grain: pd.DataFrame,
            grain: Tuple[np.number],
            data_profile: DataProfile,
            offset_fun: Callable[[np.ndarray], Union[np.ndarray, np.number]] = np.mean,
            scale_fun: Optional[Callable[[np.ndarray], Union[np.ndarray, np.number]]] = None
    ) -> _GrainAndStatistics:
        """
        Get the statistics from the profile.

        :param X_df: The data frame to know the order of columns.
        :param grain: The tuple, denoting grain values.
        :param data_profile: The data profile to take statistics from.
        :param offset: The function to be applied to grain to get offset.
        :param scale: The function to be applied to grain to get scale.
        :return: The class, holding grain item, offsets and scales of regressors and target.
        """
        Contract.assert_true(
            data_profile.shape[0] > 0, 'The training data set length is zero.',
            reference_code=ReferenceCodes._TST_PROFILE_NO_ROWS,
            target='data profile')
        y = X_one_grain[[ForecastConstant.automl_constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN]].values
        y = y.reshape((1, y.shape[0]))
        grain_item = _DataGrainItem(X_one_grain, y, grain, self._unknown_columns_to_drop)
        # We need to skip the first column, because it is target.
        offset = []  # type: List[float]
        scale = []  # type: List[float]
        # Remove the numericalized grain columns and columns we want to embed.
        columns_to_exclude = self._get_columns_to_exclude_from_normalization()
        for col_num, col in enumerate(X_one_grain.columns[1:]):
            if col_num in columns_to_exclude:
                continue
            if col not in data_profile.columns:
                # If we see column not present in the profile, it means we are
                # on the test set and it contains extra column, because profile
                # is generated on the train set.
                raise DataException._with_error(AzureMLError.create(
                    TCNExtraColumnInPrediction, column=col,
                    target="X_test", reference_code=ReferenceCodes._TCN_EXTRA_COLUMNS_IN_TEST)
                )
            col_profile = data_profile.columns[col]
            offset.append(col_profile.mean)
            scale.append(TimeSeriesDataset._recalculate_std(col_profile, data_profile.shape[0]))

        col_profile = data_profile.columns[TimeSeriesInternal.DUMMY_TARGET_COLUMN]
        if self.use_label_log_transform:
            if scale_fun is None:
                scale_fun = TimeSeriesDataset._std_scale_safe
            offset_y, scale_y = self._get_target_stats(y, offset_fun, scale_fun)
        else:
            offset_y = col_profile.mean
            scale_y = TimeSeriesDataset._recalculate_std(col_profile, data_profile.shape[0])
        return _GrainAndStatistics(
            grain_item,
            np.array(offset),
            offset_y,
            np.array(scale),
            scale_y)

    @staticmethod
    def _recalculate_std(col_profile: ColumnProfile, length: int) -> float:
        """
        Recalculate the standard deviation for given column.

        Dataprep is calculating standard deviation with degrees of freedom number
        equals to one, while for scikit-learn Standard Scaler it is zero.
        We will mimic the behavior of Standard Scaler and recalculate this number.
        :param col_profile: The column profile to calculate standard deviation for.
        :param length: the length of a column.
        :return: The standard deviation with degrees of freedom equal to zero.
        """
        safe_scale = np.sqrt((length - 1) * (col_profile.std ** 2) / length)
        if safe_scale < 10 * np.finfo(safe_scale.dtype).eps:
            safe_scale = 1
        return safe_scale

    @staticmethod
    def _std_scale_safe(x: np.ndarray, axis: Optional[int] = None) -> np.ndarray:
        """
        Return the standard deviation if it is not zero, otherwise return one.

        :param x: The matrix to calculate standard deviation for.
        :param axis: The axis parameter for np.std
        :return: The array of standard deviations.
        """
        stdevs = np.std(x, axis=axis)
        if isinstance(stdevs, np.ndarray):
            for i in range(stdevs.shape[0]):
                # Mimic the Scikit learn standard scaler limitation on
                # infinitesimal numbers.
                if stdevs[i] < 100 * np.finfo(stdevs.dtype).eps:
                    stdevs[i] = 1
            return stdevs
        return 1 if stdevs == 0 else stdevs

    def _get_target_stats(self,
                          y: np.ndarray,
                          offset_fun: Callable[[Any], Union[np.ndarray, np.number]],
                          scale_fun: Callable[[Any], Union[np.ndarray, np.number]]
                          ) -> Tuple[np.number, np.number]:
        """
        Calculate the offset and scale for target value amd return it as a tuple.

        :param y: The arroy of target values.
        :param offset_fun: The function to be applied to grain to get offset.
        :param scale_fun: The function to be applied to grain to get scale.
        :return: The tuple with offset and scale for target value.
        """
        # If log transformation is desired, we need to log transform y.
        if self.use_label_log_transform:
            y = _wrapper_util.log_transform(y).numpy()
        return offset_fun(y), scale_fun(y)

    def _get_validation_statistics(self, X: pd.DataFrame, grain: Tuple[np.number]) -> _GrainAndStatistics:
        """
        Retuen the statistics with offsets equal to 0 and scale equal to 1.

        :param X: the DataFrame.
        :param grain: The tuple, denoting grain values.
        :return: The _GrainAndStatistics object.
        """
        y = X[[ForecastConstant.automl_constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN]].values
        y = y.reshape((1, y.shape[0]))
        grain_item = _DataGrainItem(X, y, grain, unknown_columns_to_drop=self._unknown_columns_to_drop)
        # We have inserted target column into position 0.
        # Hence we need to remove it.
        colnum = X.shape[1] - 1
        colnum -= len(set(self.numericalized_grain_cols + self.embedded_columns))
        return _GrainAndStatistics(
            grain_item,
            np.zeros(colnum),
            0.,
            np.repeat(1., colnum),
            1.)

    def _get_statistics(
            self,
            X_df: pd.DataFrame,
            grain: Tuple[np.number],
            offset_fun: Callable[[Any], Union[np.ndarray, np.number]] = np.mean,
            scale_fun: Optional[Callable[[Any], Union[np.ndarray, np.number]]] = None
    ) -> _GrainAndStatistics:
        """
        Calculate the scale and offset for the grain defined by grain.

        :param X_df: The data frame with regressors and target. Target is the first column.
        :param grain: The tuple, denoting grain values.
        :param offset_fun: The function to be applied to grain to get offset.
        :param scale_fun: The function to be applied to grain to get scale.
        :return: The class, holding grain item, offsets and scales of regressors and target.
        """
        y = X_df[[ForecastConstant.automl_constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN]].values
        y = y.reshape((1, y.shape[0]))
        grain_item = _DataGrainItem(X_df, y, grain, unknown_columns_to_drop=self._unknown_columns_to_drop)

        if scale_fun is None:
            scale_fun = TimeSeriesDataset._std_scale_safe
        # We have inserted target column into position 0.
        # Hence we need to remove it.
        X = grain_item.X[:, 1:]
        if not np.issubdtype(X.dtype, np.float):
            X = X.astype('float')
        # Remove the numericalized grain columns and columns we want to embed.
        columns_to_remove = self._get_columns_to_exclude_from_normalization()
        X = np.delete(X, list(columns_to_remove), axis=1)

        offset_y, scale_y = self._get_target_stats(y, offset_fun, scale_fun)
        return _GrainAndStatistics(
            grain_item,
            offset_fun(X, axis=0),
            offset_y,
            scale_fun(X, axis=0),
            scale_y)

    def get_last_lookback_items(self, X_valid_df: Optional[pd.DataFrame] = None,
                                y_valid_df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """Return the lookback items from each grain in dataset."""
        if not self._training_data:
            raise ClientException._with_error(
                AzureMLError.create(
                    ArgumentBlankOrEmpty, target="save_data", argument_name="X_df/y_df/settings",
                    reference_code=ReferenceCodes._TCN_EMPTY_SAVE_DATA)
            )
        if self.lookback is None:
            raise ClientException._with_error(
                AzureMLError.create(
                    ArgumentBlankOrEmpty, target="lookback", argument_name="lookback",
                    reference_code=ReferenceCodes._TCN_EMPTY_LOOKBACK)
            )
        X_df, y_df, settings = self._training_data
        if settings is None:
            raise ClientException._with_error(
                AzureMLError.create(
                    ArgumentBlankOrEmpty, target="time_column", argument_name="settings",
                    reference_code=ReferenceCodes._TCN_EMPTY_SETTINGS)
            )

        if X_valid_df is not None:
            X_df = X_df.append(X_valid_df)
            y_df = y_df.append(y_valid_df)

        grains, index = None, None
        if ForecastConstant.automl_constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN not in X_df:
            # Use assign method to add the target so that we don't modify self._training_data in place
            X_df = X_df.assign(**{ForecastConstant.automl_constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN:
                                  y_df.to_numpy()})

        if ForecastConstant.automl_constants.TimeSeries.TIME_COLUMN_NAME in settings:
            index = settings[ForecastConstant.automl_constants.TimeSeries.TIME_COLUMN_NAME]
            if ForecastConstant.automl_constants.TimeSeries.GRAIN_COLUMN_NAMES in settings:
                grains = settings[ForecastConstant.automl_constants.TimeSeries.GRAIN_COLUMN_NAMES]

        if index is None:
            ret_df = X_df.iloc[-self.lookback:]
        else:
            if grains:
                ret_df = []
                groupby = X_df.groupby(grains)
                for grain in groupby.groups:
                    X_dfg = groupby.get_group(grain)
                    ret_df.append(X_dfg.iloc[-self.lookback:])
                ret_df = pd.concat(ret_df).reset_index()
            else:
                ret_df = X_df.iloc[-self.lookback:].reset_index()
        return ret_df.set_index(X_df.index.names)[X_df.columns]

    def _get_size(self, y) -> None:
        """
        Set lookback to be used with this dataset.

        :param lookback: Number of time steps used as input for forecasting.
        """
        # If timeseries is smaller than lookback + horizon, we would need to pad
        if self.lookback is None:
            raise ClientException._with_error(
                AzureMLError.create(
                    ArgumentBlankOrEmpty, target="get_size", argument_name="lookback",
                    reference_code=ReferenceCodes._TCN_LOOKBACK_NOT_SET_GET_SIZE)
            )
        if y.shape[-1] < self.lookback + self.horizon:
            sample_count = 1
        else:
            sample_count = (y.shape[-1] - self.lookback - self.horizon + self.step) // self.step
        return max(1, int(self.thinning * sample_count))

    @staticmethod
    def _get_embedding(data: pd.DataFrame, threshold: int) -> List[EmbeddingColumnInfo]:

        embedding_infos = []
        if data.shape[1] == 0:
            return embedding_infos
        if data.columns[0] == ForecastConstant.automl_constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN:
            index = 0
        else:
            index = 1
        column_purpose_detector = ColumnPurposeDetector()
        column_purpose = column_purpose_detector.get_raw_stats_and_column_purposes(data)
        for stats, featureType, name in column_purpose:
            if featureType == FeatureType.Categorical and stats.num_unique_vals > threshold:
                if name != ForecastConstant.automl_constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN:
                    max_num_features = math.ceil(data[name].max()) + 1
                    embedding_info = EmbeddingColumnInfo(name,
                                                         index,
                                                         max_num_features)
                    embedding_infos.append(embedding_info)
            index = index + 1
        return embedding_infos

    @staticmethod
    def _get_encoding(data: pd.DataFrame) -> List[EncodingSpec]:
        index = 0
        encodings = []
        column_purpose_detector = ColumnPurposeDetector()
        column_purpose = column_purpose_detector.get_raw_stats_and_column_purposes(data)
        for stats, featureType, name in column_purpose:
            if featureType == FeatureType.Categorical and stats.num_unique_vals > 2:
                # TODO remove this and replace this with label encoder
                max_num_features = int(data[name].max().astype(int) + 1)
                # embedding = EncodingSpec(feature_index=index, num_vals=stats.num_unique_vals)
                embedding = EncodingSpec(feature_index=index, num_vals=max_num_features)
                encodings.append(embedding)
            index = index + 1
        return encodings

    def _get_sample_transform(self, one_hot) -> tfs.ComposedTransform:
        if one_hot and self.dset_config.encodings:
            drop_first = False
            drop = True if drop_first else False
            tf_list = [tfs.OneHotEncode([e.feature_index for e in self.dset_config.encodings],
                                        [e.num_vals for e in self.dset_config.encodings],
                                        drop_first=drop),
                       tfs.OneHotEncode([e.feature_index for e in self.dset_config.encodings],
                                        [e.num_vals for e in self.dset_config.encodings],
                                        drop_first=drop,
                                        key=FUTURE_IND_KEY)]
            return tfs.ComposedTransform(tf_list)
        return None

    def _get_test_size(self, grain_size):
        Contract.assert_value(self.cross_validation, 'cross_validation', log_safe=True)
        # horizon itself is one part of the validation split, so we need only extra cv - 1
        # rows to slide and get cv parts. Say horizon 3 and cv 2 we need only 4 rows to get
        # we need only 4 rows to get two consecutive parts(0-2 and 1-3) with 3 rows each.
        grain_test_size = self.horizon + self.cross_validation - 1
        # Number of samples to be at least cv count to be included in validation set..
        # total number of samples in the dataset should be more that test size
        # with one horizon gap so that the training set have no horizon in common
        # with test data.
        if grain_size <= grain_test_size + self.horizon:
            grain_test_size = 0
        return grain_test_size

    def get_train_valid_split_from_cv(self):
        """
        Split the dataset into train and validation parts according to cross-validation settings.

        For cross-validation scenarios, split the input data into train and validation sets
        by assigning the latest h + cv - 1 observations of each timeseries to the validation set,
        where h is the horizon and cv is the number of CV folds.
        The validation data loader then has cv samples for each timeseries.
        """
        Contract.assert_value(self.cross_validation, 'cross_validation', log_safe=True)
        if self.lookback is None:
            raise ClientException._with_error(
                AzureMLError.create(
                    ArgumentBlankOrEmpty, target="lookback", argument_name="lookback",
                    reference_code=ReferenceCodes._TCN_EMPTY_LOOKBACK_GET_SPLIT))
        self._len = 0
        test_size = 0
        test_data_grains = []
        train_data_grains = []
        step = 1
        for item in self._data_grains:
            # total samples in the grain.
            grain_size = item.lookup_end_ix - item.lookup_start_ix
            grain_test_size = self._get_test_size(grain_size)
            grain_train_size = grain_size
            if grain_test_size != 0:
                grain_train_size -= grain_test_size
            train_item = _DataGrainItem(item.X_df, item.y, item.grain_id,
                                        self._len, self._len + grain_train_size,
                                        unknown_columns_to_drop=self._unknown_columns_to_drop)
            self._len += grain_train_size
            train_data_grains.append(train_item)
            if grain_test_size > 0:
                grain_num_test_samples = self.cross_validation
                # offset of test grain starts after the grain_train_size + horizon.
                test_item = _DataGrainItem(item.X_df, item.y, item.grain_id, test_size,
                                           test_size + grain_num_test_samples,
                                           offset=(grain_train_size + self.horizon - 1),
                                           unknown_columns_to_drop=self._unknown_columns_to_drop)
                test_size += grain_num_test_samples
                test_data_grains.append(test_item)

        if len(test_data_grains) == 0:
            # not enough data for full test and train, take the one sample from a grain that has at least twice
            # horizon and remove last horizon from training data + cv.
            mod_index = 0
            grainitem_to_split = train_data_grains[0]
            for index, item in enumerate(train_data_grains):
                if item.X_df.shape[0] >= 2 * self.horizon + self.cross_validation:
                    grainitem_to_split = item
                    mod_index = index
            test_item = _DataGrainItem(grainitem_to_split.X_df, grainitem_to_split.y,
                                       item.grain_id, 0,
                                       self.cross_validation, offset=0,
                                       unknown_columns_to_drop=self._unknown_columns_to_drop)

            number_of_items_needed_for_validation = self.horizon + self.cross_validation - 1
            if grainitem_to_split.X_df.shape[0] > number_of_items_needed_for_validation:
                grainitem_to_split.X_df = grainitem_to_split.X_df.iloc[: -number_of_items_needed_for_validation, :]
                grainitem_to_split.y = grainitem_to_split.y[:, : -number_of_items_needed_for_validation]
                grainitem_to_split.X_T = grainitem_to_split.X_T[:, : -number_of_items_needed_for_validation]
                grainitem_to_split.X_T_future = grainitem_to_split.X_T_future[
                    :, : -number_of_items_needed_for_validation]
                grainitem_to_split.lookup_end_ix = grainitem_to_split.lookup_start_ix + \
                    self._get_size(grainitem_to_split.y)
                train_data_grains[mod_index] = grainitem_to_split
                test_data_grains.append(test_item)
                test_size += self.cross_validation
                # After we have modified the element, we need to modify the rest of lookup index.
                self._len = grainitem_to_split.lookup_end_ix
                for ix in range(mod_index + 1, len(train_data_grains)):
                    size = train_data_grains[ix].lookup_end_ix - train_data_grains[ix].lookup_start_ix
                    train_data_grains[ix].lookup_start_ix = self._len
                    self._len += size
                    train_data_grains[ix].lookup_end_ix = self._len

        train_dataset = DNNTimeSeriesDatasetBase(horizon=self.horizon,
                                                 lookback=self.lookback,
                                                 sample_count=self._len,
                                                 dset_config=self.dset_config,
                                                 step=self.step,
                                                 has_past_regressors=self.has_past_regressors,
                                                 sample_transform=self.sample_transform,
                                                 fetch_y_only=self.fetch_y_only,
                                                 data_grains=train_data_grains)
        train_dataset.numericalized_grain_cols = self.numericalized_grain_cols

        if len(test_data_grains) > 0:
            # We need to recalculate statistics to avoid data leak.
            # The offsets and scales from this data set will be used
            # during training.
            offsets_list, offsets_list_y = [], []
            scales_list, scales_list_y = [], []
            self.grain_map = {}
            input_grains = self._data_grains
            self._data_grains = []
            exp_store = self._get_experiment_store_maybe()
            Contract.assert_true(
                len(input_grains) == len(train_data_grains),
                message=('The number of training items after CV split '
                         'has been changed.'),
                reference_code=ReferenceCodes._TCN_DATASET_TRAIN_ITEMS_CHANGED,
            )
            for input_item, item in zip(input_grains, train_data_grains):
                grain_len = item.lookup_end_ix - item.lookup_start_ix
                if grain_len == input_item.lookup_end_ix - \
                        input_item.lookup_start_ix and input_item.X_df.shape[0] == item.X_df.shape[0]:
                    # If we did not changed this grain, just calculate statistics.
                    new_grain_stats = self._get_or_calculate_statistics(
                        item.X_df, self._grain_column_names, item.grain_id, exp_store, is_train_set=True)
                else:
                    last_row = self.step * (grain_len - 1) + self.lookback + self.horizon
                    grain_df = item.X_df[:last_row]
                    # In this case we do not have correct statistics in the profile and have to
                    # calculate it.
                    new_grain_stats = self._get_statistics(grain_df, item.grain_id)
                offsets_list.append(new_grain_stats.offsets)
                offsets_list_y.append(new_grain_stats.offset_y)
                scales_list.append(new_grain_stats.scales)
                scales_list_y.append(new_grain_stats.scale_y)
                self._data_grains.append(item)
                self.grain_map[item.grain_id] = len(self._data_grains) - 1

            self.offsets = torch.from_numpy(np.array(offsets_list))  # type: torch.tensor
            self.scales = torch.from_numpy(np.array(scales_list))  # type: torch.tensor
            self.offsets_y = torch.from_numpy(np.array(offsets_list_y).reshape((-1, 1)))  # type: torch.tensor
            self.scales_y = torch.from_numpy(np.array(scales_list_y).reshape((-1, 1)))  # type: torch.tensor

        valid_dataset = DNNTimeSeriesDatasetBase(horizon=self.horizon,
                                                 lookback=self.lookback,
                                                 sample_count=test_size,
                                                 dset_config=self.dset_config,
                                                 step=step,
                                                 has_past_regressors=self.has_past_regressors,
                                                 sample_transform=self.sample_transform,
                                                 fetch_y_only=self.fetch_y_only,
                                                 cross_validation=self.cross_validation,
                                                 data_grains=test_data_grains)
        valid_dataset.numericalized_grain_cols = self.numericalized_grain_cols

        Contract.assert_true(len(test_data_grains) <= len(train_data_grains),
                             'Found more series in the test split than in train split.', log_safe=True)
        if len(test_data_grains) == 0:
            msg = "length of test grain {0}, train size = {1}".\
                format(len(test_data_grains), len(train_data_grains))
            Contract.assert_true(len(test_data_grains) > 0, msg, log_safe=True)

        return train_dataset, valid_dataset

    def get_feature_indices_for_normalization(self) -> torch.Tensor:
        """
        Exclude the indices of numericalized grain features, embeddings and indicator columns.

        :return: The indices of features.
        """
        exclude_indices = self._get_columns_to_exclude_from_normalization()
        indices = set(range(self.offsets.shape[1] + len(exclude_indices)))
        if exclude_indices:
            indices = indices.difference(exclude_indices)
        return list(indices)
