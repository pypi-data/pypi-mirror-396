import io

import pandas as pd
import numpy as np
import pytest

from oddball import Dataset, clear_cache, list_available, load, split_by_label
from oddball.data.loader import DatasetManager
from oddball.data.registry import DATASET_FILES


@pytest.fixture(autouse=True)
def reset_cache():
    clear_cache(all_versions=True)
    yield
    clear_cache(all_versions=True)


@pytest.fixture
def sample_npz_bytes():
    def factory(n_rows: int = 50, n_features: int = 4) -> bytes:
        rng = np.random.default_rng(123)
        X = rng.normal(size=(n_rows, n_features)).astype(np.float32)
        y = np.zeros(n_rows, dtype=np.int64)
        y[: max(1, n_rows // 10)] = 1
        rng.shuffle(y)
        buf = io.BytesIO()
        np.savez(buf, X=X, y=y)
        return buf.getvalue()

    return factory


@pytest.fixture
def mock_download(monkeypatch, sample_npz_bytes):
    payload = sample_npz_bytes()

    def fake_download(self, filename: str) -> bytes:  # noqa: ARG001
        return payload

    monkeypatch.setattr(DatasetManager, "_download", fake_download)
    return payload


def test_load_returns_raw_arrays(mock_download):  # noqa: ARG001
    X, y = load(Dataset.COVER)
    assert isinstance(X, np.ndarray)
    assert isinstance(y, np.ndarray)
    assert X.shape[0] == y.shape[0]
    assert set(np.unique(y)) <= {0, 1}


def test_list_available_matches_registry():
    assert sorted(list_available()) == sorted(DATASET_FILES.keys())


@pytest.mark.parametrize("name", list_available())
def test_all_datasets_can_load_via_global_loader(mock_download, name):  # noqa: ARG001
    X, y = load(name)
    assert X.shape[0] == y.shape[0] > 0


@pytest.mark.parametrize(
    "alias",
    [
        "page_blocks",
        "page-blocks",
        "internet_ads",
        "spam_base",
        "breast wisconsin",
        "satimage_2",
    ],
)
def test_aliases_resolve_to_supported_dataset(mock_download, alias):  # noqa: ARG001
    X, y = load(alias)
    assert X.shape[0] == y.shape[0] > 0


def test_split_by_label_returns_views(mock_download):  # noqa: ARG001
    normal, anomaly = split_by_label(Dataset.COVER)
    assert isinstance(normal, np.ndarray)
    assert isinstance(anomaly, np.ndarray)
    assert normal.shape[1] == anomaly.shape[1]


def test_load_with_setup_returns_split(monkeypatch, sample_npz_bytes):
    payload = sample_npz_bytes(n_rows=200, n_features=5)

    def fake_download(self, filename: str) -> bytes:  # noqa: ARG001
        return payload

    monkeypatch.setattr(DatasetManager, "_download", fake_download)

    x_train, x_test, y_test = load(Dataset.COVER, setup=True, seed=123)

    assert isinstance(x_train, pd.DataFrame)
    assert isinstance(x_test, pd.DataFrame)
    assert isinstance(y_test, pd.Series)
    assert "Class" not in x_train.columns
    assert "Class" not in x_test.columns
    assert x_train.shape[1] == x_test.shape[1]
    assert set(y_test.unique()) <= {0, 1}

    npz = np.load(io.BytesIO(payload))
    df = pd.DataFrame(npz["X"])
    df["Class"] = npz["y"]

    normal_count = int((df["Class"] == 0).sum())
    anomaly_count = int((df["Class"] == 1).sum())
    expected_train = normal_count // 2
    expected_test = min(1000, expected_train // 3)
    expected_outlier = min(expected_test // 10, anomaly_count)
    expected_normal = min(
        expected_test - expected_outlier, normal_count - expected_train
    )

    assert len(x_train) == expected_train
    assert len(y_test) == expected_normal + expected_outlier
    assert df.loc[x_train.index, "Class"].eq(0).all()
    if expected_outlier:
        assert (y_test == 1).sum() == expected_outlier


@pytest.fixture
def mock_urlopen(monkeypatch, sample_npz_bytes):
    """Mock urlopen to return sample NPZ data without network calls."""
    from unittest.mock import MagicMock

    payload = sample_npz_bytes()

    def fake_urlopen(request):  # noqa: ARG001
        mock_response = MagicMock()
        mock_response.read.return_value = payload
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = lambda s, *args: None
        return mock_response

    monkeypatch.setattr("oddball.data.loader.urlopen", fake_urlopen)
    return payload


def test_clear_cache_clears_memory_cache(mock_urlopen, tmp_path, monkeypatch):  # noqa: ARG001
    """Verify clear_cache() empties the in-memory cache."""
    import os
    from oddball.data.loader import _manager

    os.environ["ODDBALL_CACHE_DIR"] = str(tmp_path)

    load(Dataset.COVER)
    assert len(_manager._memory_cache) > 0

    clear_cache()
    assert len(_manager._memory_cache) == 0


def test_clear_cache_clears_disk_cache(mock_urlopen, tmp_path, monkeypatch):  # noqa: ARG001
    """Verify clear_cache() removes files from disk cache."""
    import os
    from oddball.data.loader import _manager

    os.environ["ODDBALL_CACHE_DIR"] = str(tmp_path)

    load(Dataset.COVER)
    cache_file = tmp_path / _manager.version / DATASET_FILES["cover"]
    assert cache_file.exists()

    clear_cache()
    assert not cache_file.exists()


def test_clear_cache_single_dataset(mock_urlopen, tmp_path, monkeypatch):  # noqa: ARG001
    """Verify clear_cache(dataset=...) only clears that dataset."""
    import os
    from oddball.data.loader import _manager

    os.environ["ODDBALL_CACHE_DIR"] = str(tmp_path)

    load(Dataset.COVER)
    load(Dataset.GLASS)
    cover_file = tmp_path / _manager.version / DATASET_FILES["cover"]
    glass_file = tmp_path / _manager.version / DATASET_FILES["glass"]
    assert cover_file.exists()
    assert glass_file.exists()

    clear_cache(dataset="cover")
    assert not cover_file.exists()
    assert glass_file.exists()


def test_clear_cache_all_versions(mock_urlopen, tmp_path, monkeypatch):  # noqa: ARG001
    """Verify clear_cache(all_versions=True) removes all version directories."""
    import os
    from oddball.data.loader import _manager

    os.environ["ODDBALL_CACHE_DIR"] = str(tmp_path)

    load(Dataset.COVER)
    current_version_dir = tmp_path / _manager.version
    assert current_version_dir.exists()

    # Create a fake old version directory
    old_version_dir = tmp_path / "v0.9-old"
    old_version_dir.mkdir()
    (old_version_dir / "dummy.npz").touch()
    assert old_version_dir.exists()

    clear_cache(all_versions=True)
    assert not current_version_dir.exists()
    assert not old_version_dir.exists()


def test_download_retries_on_503(monkeypatch, tmp_path, sample_npz_bytes):
    """Verify download retries on 503 errors with exponential backoff."""
    import os
    from unittest.mock import MagicMock, call
    from urllib.error import HTTPError

    os.environ["ODDBALL_CACHE_DIR"] = str(tmp_path)

    payload = sample_npz_bytes()
    call_count = 0

    def fake_urlopen(request):  # noqa: ARG001
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise HTTPError(
                url="http://example.com",
                code=503,
                msg="Service Unavailable",
                hdrs={},
                fp=None,
            )
        mock_response = MagicMock()
        mock_response.read.return_value = payload
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = lambda s, *args: None
        return mock_response

    mock_sleep = MagicMock()
    monkeypatch.setattr("oddball.data.loader.urlopen", fake_urlopen)
    monkeypatch.setattr("oddball.data.loader.time.sleep", mock_sleep)

    with pytest.warns(UserWarning, match=r"Retry \d/\d for cover\.npz"):
        X, y = load(Dataset.COVER)

    assert X.shape[0] == y.shape[0]
    assert call_count == 3
    assert mock_sleep.call_args_list == [call(2.0), call(4.0)]
