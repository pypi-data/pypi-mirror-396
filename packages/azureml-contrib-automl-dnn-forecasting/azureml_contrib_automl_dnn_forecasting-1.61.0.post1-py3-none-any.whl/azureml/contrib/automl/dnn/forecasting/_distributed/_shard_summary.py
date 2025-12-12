# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Optional

from azureml.automl.core.shared.constants import MLTableDataLabel
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.contrib.automl.dnn.forecasting._distributed._grain_summary import GrainSummary


class GrainShardSummary:
    """The summary of one shard of one grain in the dataset to be downloaded."""

    def __init__(self,
                 grain_summary: GrainSummary,
                 dataset_type: MLTableDataLabel,
                 row_start_idx: int = 0,
                 row_end_idx: Optional[int] = None) -> None:
        """
        The summary of one shard of one grain in the dataset to be downloaded.
        Shard is one piece of timeseries dataset that has to be downloaded

        :param grain_summary: The summary of the grain this shard represents.
        :param dataset_type: The dataset type this shard belongs to.
        :param row_start_idx:
            The starting index of the row to be downloaded. If it is negative, padding will
            be applied. Example- If row_start_idx is -2, 2 rows will be padded.
        :param row_end_idx:
            The ending index of the row to be downloaded. If None, download till the end of
            the timeseries. This value is exclusive. That means, if row_start_idx is 5 and
            row_end_idx is 9, rows 5 to 8 will be downloaded
        """
        if row_end_idx is None:
            row_end_idx = grain_summary.num_rows
        # assert all sizes are greater than 0
        Contract.assert_true(
            row_end_idx >= row_start_idx,
            "A shard cannot have start index greater than end index.",
            reference_code=ReferenceCodes._TS_SHARDING_ROW_END_IDX_LT_ROW_START_IDX,
            log_safe=True
        )
        # assert the rows to download are valid.
        Contract.assert_true(
            row_end_idx <= grain_summary.num_rows,
            "A shard cannot have row end index greater than total number of rows in the grain",
            reference_code=ReferenceCodes._TS_SHARDING_ROW_END_IDX_GT_TOTAL_ROWS,
            log_safe=True
        )
        self.grain_summary = grain_summary
        self.rows_to_pad = max(0, -row_start_idx)
        self.rows_to_download_range = (max(0, row_start_idx), row_end_idx)
        self.dataset_type = dataset_type

    @property
    def num_rows(self) -> int:
        """
        The number of rows this shard represents.

        :return: The number of rows this shard represents.
        """
        return self.rows_to_download_range[1] - self.rows_to_download_range[0] + self.rows_to_pad
