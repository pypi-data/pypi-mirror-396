import tempfile

import numpy as np
import pytest
from torch.utils.data import DataLoader

from forecast.data import FUTURE_IND_KEY, FUTURE_DEP_KEY, PAST_IND_KEY, PAST_DEP_KEY
from forecast.data.dataset import OnlineTimeSeriesDataset
from forecast.data.sources import ElectricityDataSource, GithubDataSource


@pytest.mark.parametrize("n_window", [60, 90, 120])
@pytest.mark.parametrize("n_horizon", [14, 30, 60])
@pytest.mark.parametrize("step", [1, 2, 4])
@pytest.mark.parametrize("target_ind", [0, 2, 4])
@pytest.mark.parametrize("mmap", [False, True])
@pytest.mark.parametrize("ts_id_idx", [None, 5])
def test_single_series(n_window, n_horizon, step, target_ind, mmap, ts_id_idx):
    n_steps = 1000
    n_features = 5
    data = np.random.rand(n_steps, n_features).astype(np.float32)

    if ts_id_idx:
        data = np.concatenate([data, np.zeros([n_steps, 1])], axis=1)

    tmpdir = tempfile.TemporaryDirectory()
    if mmap:
        fname = tmpdir.name + "/file.npy"
        np.save(fname, data)
        data = np.load(fname, mmap_mode="r")

    feat_cols = [i for i in range(data.shape[1]) if i != target_ind]
    ds = OnlineTimeSeriesDataset(
        data,
        n_window,
        n_horizon,
        [target_ind],
        step=step,
        ts_id_idx=ts_id_idx,
    )

    assert len(ds) == (n_steps - n_window - n_horizon + step) // step

    first_sample = ds[0]
    assert first_sample[PAST_IND_KEY].shape == data[:n_window, feat_cols].T.shape
    assert first_sample[PAST_DEP_KEY].shape == data[:n_window, [target_ind]].T.shape
    assert first_sample[FUTURE_IND_KEY].shape == data[n_window : n_window + n_horizon, feat_cols].T.shape
    assert first_sample[FUTURE_DEP_KEY].shape == data[n_window : n_window + n_horizon, [target_ind]].T.shape

    assert np.array_equal(first_sample[PAST_IND_KEY], data[:n_window, feat_cols].T)
    assert np.array_equal(first_sample[PAST_DEP_KEY], data[:n_window, [target_ind]].T)
    assert np.array_equal(first_sample[FUTURE_IND_KEY], data[n_window : n_window + n_horizon, feat_cols].T)
    assert np.array_equal(first_sample[FUTURE_DEP_KEY], data[n_window : n_window + n_horizon, [target_ind]].T)

    last_ind = len(ds) - 1
    w_start = last_ind * step
    h_start = last_ind * step + n_window
    last_sample = ds[last_ind]
    assert np.array_equal(last_sample[PAST_IND_KEY], data[w_start : w_start + n_window, feat_cols].T)
    assert np.array_equal(last_sample[PAST_DEP_KEY], data[w_start : w_start + n_window, [target_ind]].T)
    assert np.array_equal(last_sample[FUTURE_IND_KEY], data[h_start : h_start + n_horizon, feat_cols].T)
    assert np.array_equal(last_sample[FUTURE_DEP_KEY], data[h_start : h_start + n_horizon, [target_ind]].T)


@pytest.mark.parametrize("n_window", [60, 90, 120])
@pytest.mark.parametrize("n_horizon", [14, 30, 60])
@pytest.mark.parametrize("step", [1, 2, 4])
@pytest.mark.parametrize("target_ind", [0, 2, 4])
@pytest.mark.parametrize("mmap", [False, True])
def test_multiseries(n_window, n_horizon, step, target_ind, mmap):
    n_steps = 1000
    n_features = 5
    ts_id_idx = target_ind + 1
    data_raw = np.random.rand(n_steps, n_features).astype(np.float32)
    ts_ids = np.concatenate(
        [
            np.zeros(100),
            np.ones(200),
            np.ones(300) * 2,
            np.ones(400) * 3,
        ]
    )

    # fill in the new dataset
    data = np.zeros([n_steps, n_features + 1])
    data[:, ts_id_idx] = ts_ids
    data[:, [i for i in range(n_features + 1) if i != ts_id_idx]] = data_raw
    del data_raw

    tmpdir = tempfile.TemporaryDirectory()
    if mmap:
        fname = tmpdir.name + "/file.npy"
        np.save(fname, data)
        data = np.load(fname, mmap_mode="r")

    ds = OnlineTimeSeriesDataset(
        data,
        n_window,
        n_horizon,
        [target_ind],
        step=step,
        ts_id_idx=ts_id_idx,
    )

    for _ in range(20):
        idx = np.random.randint(len(ds))
        sample = ds[idx]
        assert sample[PAST_IND_KEY].shape == (n_features, n_window)
        assert sample[PAST_DEP_KEY].shape == (1, n_window)
        assert sample[FUTURE_IND_KEY].shape == (n_features, n_horizon)
        assert sample[FUTURE_DEP_KEY].shape == (1, n_horizon)

        sample_past_ts_col = sample[PAST_IND_KEY][target_ind, :]  # target_ind is stripped so the ts_id is shifted
        sample_fut_ts_col = sample[FUTURE_IND_KEY][target_ind, :]  # since ts_id = target_ind + 1
        assert (
            sample_past_ts_col.min() == sample_past_ts_col.max() == sample_fut_ts_col.min() == sample_fut_ts_col.max()
        )


@pytest.mark.parametrize("n_window", [60, 90, 120])
@pytest.mark.parametrize("n_horizon", [14, 30, 60])
# @pytest.mark.parametrize("step", [1, 2, 4])
@pytest.mark.parametrize("mmap", [False, True])
@pytest.mark.parametrize("source", [GithubDataSource, ElectricityDataSource])
def test_dataset_compatibility(n_window, n_horizon, mmap, source):
    datasource = source(n_horizon)
    train, _ = datasource.get_dataset(n_window)

    train_data = train._data.transpose(2, 1, 0).squeeze()

    if source is ElectricityDataSource:
        # flatten (grain_id, feature_id, time) making grain_id a feature
        train_data = np.concatenate([train_data[:, :, i] for i in range(train_data.shape[2])])
        ts_id_idx = 1
        target_ind = 0
    elif source is GithubDataSource:
        ts_id_idx = None
        target_ind = 0

    tmpdir = tempfile.TemporaryDirectory()
    if mmap:
        fname = tmpdir.name + "/file.npy"
        np.save(fname, train_data)
        train_data = np.load(fname, mmap_mode="r")

    train2 = OnlineTimeSeriesDataset(train_data, n_window, n_horizon, [target_ind], ts_id_idx=ts_id_idx)
    assert len(train) == len(train2)

    for _ in range(20):
        idx = np.random.randint(len(train2))
        assert np.array_equal(train[idx][PAST_IND_KEY], train2[idx][PAST_IND_KEY])
        assert np.array_equal(train[idx][PAST_DEP_KEY], train2[idx][PAST_DEP_KEY])
        assert np.array_equal(train[idx][FUTURE_IND_KEY], train2[idx][FUTURE_IND_KEY])
        assert np.array_equal(train[idx][FUTURE_DEP_KEY], train2[idx][FUTURE_DEP_KEY])


@pytest.mark.parametrize("source", [GithubDataSource, ElectricityDataSource])
@pytest.mark.parametrize("mmap", [False, True])
def test_dataloader(source, mmap):
    datasource = source(30)
    train, _ = datasource.get_dataset(60)
    train_data = train._data.transpose(2, 1, 0).squeeze()

    if source is ElectricityDataSource:
        # flatten (grain_id, feature_id, time) making grain_id a feature
        train_data = np.concatenate([train_data[:, :, i] for i in range(train_data.shape[2])])
        ts_id_idx = 1
        target_ind = 0
    elif source is GithubDataSource:
        ts_id_idx = None
        target_ind = 0

    tmpdir = tempfile.TemporaryDirectory()
    if mmap:
        fname = tmpdir.name + "/file.npy"
        np.save(fname, train_data)
        train_data = np.load(fname, mmap_mode="r")

    train2 = OnlineTimeSeriesDataset(train_data, 60, 30, [target_ind], ts_id_idx=ts_id_idx)
    dl = DataLoader(train2, batch_size=32, shuffle=True, num_workers=4)
    for _ in dl:
        pass
