# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module for creating dataset config for distributed TCN training."""

import enum
import numpy as np
import pandas as pd
import torch
from typing import Any, Mapping, Sequence, Tuple, Optional, Callable, Union
from dataclasses import dataclass

from azureml.automl.core.shared.constants import TimeSeriesInternal
from azureml.automl.runtime.experiment_store import ExperimentStore
from azureml.automl.runtime.featurizer.transformer.timeseries.timeseries_transformer import TimeSeriesTransformer
from azureml.automl.runtime.shared.forecasting_utils import get_pipeline_step
from azureml.automl.runtime._time_series_data_set import TimeSeriesDataSet as TSDataSet
from azureml.contrib.automl.dnn.forecasting.constants import TCNForecastParameters
from azureml.contrib.automl.dnn.forecasting.datasets.timeseries_datasets import EmbeddingColumnInfo
from azureml.contrib.automl.dnn.forecasting._distributed._grain_summary import GrainSummary
from azureml.training.tabular.featurization.timeseries.grain_index_featurizer import GrainIndexFeaturizer
from azureml.training.tabular.featurization.timeseries.numericalize_transformer import NumericalizeTransformer
from azureml.training.tabular.featurization.timeseries._distributed.timeseries_data_profile import \
    AggregatedTimeSeriesDataProfile


@dataclass
class NormalizationConfig:
    scales: torch.tensor
    scale_y: torch.tensor
    offsets: torch.tensor
    offset_y: torch.tensor


@dataclass
class TimeseriesDatasetProperties:
    numericalized_grain_cols: Sequence[int]
    grain_map: Mapping[Tuple, int]
    get_feature_indices_for_normalization: Callable[[], Sequence[int]]
    offsets: torch.tensor
    scales: torch.tensor
    offsets_y: torch.tensor
    scales_y: torch.tensor
    use_label_log_transform: bool


class EmbeddingOption(enum.Enum):
    NO_EMBEDDINGS = enum.auto()
    ALL_CATEGORICAL_COLUMNS = enum.auto()
    ONLY_TSID_COLUMNS = enum.auto()


class TimeseriesDatasetConfig:
    """Computes the required configurations of the dataset for forecasting model training."""

    def __init__(
        self,
        use_target_log_transform: bool,
        numericalized_grain_column_indices: Sequence[int],
        grain_map: Mapping[Tuple, int],
        normalization_config: NormalizationConfig,
        embeddings: Sequence[EmbeddingColumnInfo],
        embedded_column_indices: Sequence[int],
        indicator_column_indices: Sequence[int],
        y_min: Sequence[float],
        y_max: Sequence[float],
    ) -> None:
        """
        Compute the required configurations of the dataset for forecasting model training.

        :param use_target_log_transform: Boolean indicating if log transform for target is enabled.
        :param numericalized_grain_column_indices: Index of numericalized grain columns.
        :param grain_map: Mapping of grain to index.
        :param normalization_config: Normalization config for the dataset.
        :param embeddings: Sequence of embeddings for the datset.
        :param embedded_column_indices: Index of columns that have to be embedded.
        :param indicator_column_indices: Index of columns that are indicator columns.
        :param y_min: Sequence of y_min for each grain.
        :param y_max: Sequence of y_max for each grain.
        """
        # Adding a dataset property to match the contract of the dataset class used in
        # non-distributed TCN. This needs to be refactored in future to have a streamlined
        # code path.
        self.dataset = TimeseriesDatasetProperties(
            numericalized_grain_cols=numericalized_grain_column_indices,
            grain_map=grain_map,
            get_feature_indices_for_normalization=self._get_feature_indices_for_normalization,
            offsets=normalization_config.offsets,
            scales=normalization_config.scales,
            offsets_y=normalization_config.offset_y,
            scales_y=normalization_config.scale_y,
            use_label_log_transform=use_target_log_transform,
        )
        self.embedding_col_infos = embeddings
        self._embedded_column_indices = embedded_column_indices
        self._indicator_column_indices = indicator_column_indices
        self.y_min = y_min
        self.y_max = y_max

    def set_lookback(self, lookback) -> None:
        """
        Set the lookback period.

        :param lookback: The lookback period to be used in training.
        """
        self.lookback = lookback

    def _get_feature_indices_for_normalization(self) -> Sequence[int]:
        """Get the index of columns that have to be normalized."""
        exclude_indices = set(
            self._embedded_column_indices + self.dataset.numericalized_grain_cols + self._indicator_column_indices
        )
        indices = set(range(self.dataset.offsets.shape[1] + len(exclude_indices)))
        if exclude_indices:
            indices = indices.difference(exclude_indices)
        return sorted(list(indices))


def get_dataset_config(
    numericalized_grain_column_names: Sequence[str],
    apply_log_transform_for_target,
    column_names: Sequence[str],
    train_grain_summary: Sequence[GrainSummary],
    ts_transformer: TimeSeriesTransformer,
    data_profile: AggregatedTimeSeriesDataProfile,
    expr_store: ExperimentStore,
):
    """
    Get the config for the dataset.

    :param numericalized_grain_column_names: Names of grain columns that have been numericalized.
    :param apply_log_tranform_for_target: enable log transform for the target column.
    :param column_names: Sequence of column names that have to be used for training.
    :param train_grain_summary: Sequence of grain summaries for the training dataset.
    :param ts_transformer: The timeseries transformer.
    :param data_profile: The data profile for the train and val datasets.
    :param expr_store: The experiment store.

    :return: The dataset config.
    """
    numericalized_grain_columns = [column_names.index(gcol) for gcol in numericalized_grain_column_names]
    indicator_columns = _get_indicator_column_indices(column_names, expr_store)
    embeddings, embedded_columns = \
        _get_embeddings(column_names, indicator_columns, ts_transformer,
                        embedding_option=EmbeddingOption.ONLY_TSID_COLUMNS)

    grain_map = _get_grain_map(ts_transformer, train_grain_summary)
    normalization_config = _get_scales_and_offsets(
        train_grain_summary=train_grain_summary,
        data_profile=data_profile,
        column_names=column_names,
        indicator_column_indices=indicator_columns,
        numericalized_grain_columns=numericalized_grain_columns,
        embedded_column_indices=embedded_columns,
        apply_log_transform_for_target=apply_log_transform_for_target
    )
    y_min, y_max = _get_y_range(train_grain_summary, data_profile)

    return TimeseriesDatasetConfig(
        apply_log_transform_for_target,
        numericalized_grain_columns,
        grain_map,
        normalization_config,
        embeddings,
        embedded_columns,
        indicator_columns,
        y_min,
        y_max
    )


def _get_scales_and_offsets(
    train_grain_summary: Sequence[GrainSummary],
    data_profile: AggregatedTimeSeriesDataProfile,
    column_names: Sequence[str],
    indicator_column_indices: Sequence[int],
    numericalized_grain_columns: Sequence[int],
    embedded_column_indices: Sequence[int],
    apply_log_transform_for_target: bool
) -> NormalizationConfig:
    """
    Get the scales and offsets for a grain.

    :param train_grain_summary: The train grain summary.
    :param data_profile: The data profile for the train and val datasets.
    :param column_names: The column names for training.
    :param indicator_column_indices: The indicator columns indices.
    :param numericalized_grain_columns: The numericalized grain column indices.
    :param embedded_column_indices: The embedded column indices.
    :param apply_log_transform_for_target: Bool indicating if log transform has to be applied.

    :return: The scales and offsets for the grain.
    """
    offsets_list, scales_list = [], []
    offsets_list_y, scales_list_y = [], []

    for grain_summary in train_grain_summary:
        normalization_config_list = _get_stats_from_profile(
            grain_summary.grain,
            data_profile,
            column_names,
            indicator_column_indices,
            numericalized_grain_columns,
            embedded_column_indices,
            apply_log_transform_for_target
        )
        offsets_list.append(normalization_config_list.offsets)
        offsets_list_y.append(normalization_config_list.offset_y)
        scales_list.append(normalization_config_list.scales)
        scales_list_y.append(normalization_config_list.scale_y)

    return NormalizationConfig(
        scales=torch.tensor(scales_list),
        scale_y=torch.tensor(scales_list_y).reshape((-1, 1)),
        offsets=torch.tensor(offsets_list),
        offset_y=torch.tensor(offsets_list_y).reshape((-1, 1))
    )


def _get_y_range(
    train_grain_summary: Sequence[GrainSummary],
    data_profile: AggregatedTimeSeriesDataProfile,
) -> Tuple[Sequence[float], Sequence[float]]:
    """
    Get the min and max target values for each grain in the training dataset.

    :train_grain_summary: The train grain summary.
    :data_profile: The data profile for the train and validation datasets.

    :return: The min and max target values for each grain in the training dataset.
    """
    y_min_list = [
        data_profile.get_train_y_min(grain_summary.grain) for grain_summary in train_grain_summary
    ]
    y_max_list = [
        data_profile.get_train_y_max(grain_summary.grain) for grain_summary in train_grain_summary
    ]
    return y_min_list, y_max_list


def _get_stats_from_profile(
    grain: Mapping[str, Any],
    data_profile: AggregatedTimeSeriesDataProfile,
    column_names: Sequence[str],
    indicator_column_indices: Sequence[int],
    numericalized_grain_col_indices: Sequence[int],
    embedded_columns_indices: Sequence[int],
    use_target_log_transform: bool
) -> NormalizationConfig:
    """
    Get the statistics from the profile.

    :param grain: The grain represented as dictionary where key is column name and value is column value.
    :param data_profile: The data profile for the training and validation datasets.
    :param column_names: Sequence of column names that have to be used for training.
    :param indicator_column_indices: Indices of the indicator columns.
    :param numericalized_grain_col_indices: Index of numericalized grain columns.
    :param embedded_columns_indices: Index of columns that have to be embedded.
    :param use_target_log_transform: Boolean indicating if the target column has to be log transformed.

    :return: The normalization config, holding offsets and scales of regressors and target.
    """
    # Remove the numericalized grain columns, columns we want to embed and indicator columns.
    columns_to_remove = set(numericalized_grain_col_indices + embedded_columns_indices + indicator_column_indices)
    columns_for_train = [
        col for col_idx, col in enumerate(column_names)
        if col_idx not in columns_to_remove and col != TimeSeriesInternal.DUMMY_TARGET_COLUMN
    ]
    offset = data_profile.get_train_mean(grain, columns_for_train)
    scale = data_profile.get_train_std(grain, columns_for_train)

    if use_target_log_transform:
        target_col_name = TimeSeriesInternal.DUMMY_LOG_TARGET_COLUMN
    else:
        target_col_name = TimeSeriesInternal.DUMMY_TARGET_COLUMN
    offset_y = data_profile.get_train_mean(grain, target_col_name)
    scale_y = data_profile.get_train_std(grain, target_col_name)
    return NormalizationConfig(
        offsets=np.array(offset),
        offset_y=offset_y,
        scales=np.array(scale),
        scale_y=scale_y
    )


def _get_grain_map(ts_transformer: TimeSeriesTransformer, train_grain_summary: Sequence[GrainSummary]):
    """Get the grain mappings that maps numerical grain values to unique integers."""
    grain_index_featurizer: GrainIndexFeaturizer = \
        get_pipeline_step(ts_transformer.pipeline, TimeSeriesInternal.MAKE_GRAIN_FEATURES)
    df = pd.DataFrame([grain_summary.grain for grain_summary in train_grain_summary]).reset_index()
    # Below, we use index column as time column just as placeholder to avoid throwing error in validations.
    # It is not used. We have dropped it just after it.
    grain_map_df = grain_index_featurizer.transform(
        TSDataSet(df, time_series_id_column_names=ts_transformer.grain_column_names, time_column_name="index")
    ).data.reset_index(drop=True)
    grain_map = {tuple(x): idx for idx, x in enumerate(grain_map_df.values)}
    return grain_map


def _get_embeddings(
    column_names: Sequence[str],
    indicator_column_indices: Sequence[int],
    transformer: TimeSeriesTransformer,
    embedding_option: EmbeddingOption = EmbeddingOption.ONLY_TSID_COLUMNS
) -> Tuple[Sequence[EmbeddingColumnInfo], Sequence[int]]:
    """
    Get the embeddings.

    :param column_names: Sequence of the column names to be used for training.
    :param indicator_column_indices: Indices of the indicator columns.
    :param transformer: The timeseries transformer.
    :param embedding_option: Embedding option to enable embedding for grain/categorical columns.

    :return: The Sequence of embedding column information and Sequence of embedded columns.
    """
    embeddings = []
    embedded_columns = []
    if embedding_option is EmbeddingOption.ALL_CATEGORICAL_COLUMNS:
        non_grain_categoricals: Optional[NumericalizeTransformer] = \
            get_pipeline_step(transformer.pipeline, TimeSeriesInternal.MAKE_CATEGORICALS_NUMERIC)
        if non_grain_categoricals is not None:
            embeddings.extend(_get_embeddings_from_dict(
                non_grain_categoricals._categories_by_col, column_names, indicator_column_indices
            ))

    if embedding_option in (EmbeddingOption.ALL_CATEGORICAL_COLUMNS, EmbeddingOption.ONLY_TSID_COLUMNS):
        grain_categoricals: Optional[GrainIndexFeaturizer] = \
            get_pipeline_step(transformer.pipeline, TimeSeriesInternal.MAKE_GRAIN_FEATURES)
        if grain_categoricals is not None:
            embeddings.extend(_get_embeddings_from_dict(
                {
                    grain_categoricals._preview_grain_feature_names_from_grains([tsid_col])[0]:
                    categories for tsid_col, categories in grain_categoricals.categories_by_grain_cols.items()
                },
                column_names, indicator_column_indices))

    embedded_columns = [
        i for i, col in enumerate(column_names) for embed_col in embeddings if col == embed_col.name
    ]
    return embeddings, embedded_columns


def _get_embeddings_from_dict(
    category_col_dict: Mapping[str, Union[pd.Index, Sequence[Any]]],
    column_names: Sequence[str],
    indicator_column_indices: Sequence[int],
) -> Sequence[EmbeddingColumnInfo]:
    """
    Get the embeddings from a dictionary of column names and categories.

    :param category_col_dict: A dictionary mapping column names to the categories in it.
    :param column_names: Sequence of column names that have to be used for training.
    :param indicator_columns: The indices of indicator columns.

    :return: The sequence of embedding column information and sequence of embedded columns.
    """
    embeddings = []
    col_names_to_idx_map = {col_name: idx for idx, col_name in enumerate(column_names)}
    for col, categories in category_col_dict.items():
        if col not in col_names_to_idx_map:
            continue
        col_idx = col_names_to_idx_map[col]
        if col == TimeSeriesInternal.DUMMY_TARGET_COLUMN or col_idx in indicator_column_indices:
            continue
        if len(categories) > TCNForecastParameters.EMBEDDING_THRESHOLD:
            # Add one to the column index since the target will be prepended to the feature array
            embeddings.append(EmbeddingColumnInfo(name=col, index=(col_idx + 1), distinct_values=len(categories)))
    return embeddings


def _get_indicator_column_indices(column_names: Sequence[str], expr_store: ExperimentStore) -> Sequence[int]:
    """
    Get the sequence of column indices which are indicator columns.

    :param column_names: The sequence of column names that have to be used for training.
    :param expr_store: The experiment store.

    :return: The sequence of columns that are indicator columns containing only 0 or 1 values.
    """
    indicator_column_dict = expr_store.metadata.timeseries.get_indicator_columns_data()
    indicator_column_indices = []
    for col_idx, col in enumerate(column_names):
        if col != TimeSeriesInternal.DUMMY_TARGET_COLUMN and indicator_column_dict.get(col, False):
            indicator_column_indices.append(col_idx)
    return indicator_column_indices
