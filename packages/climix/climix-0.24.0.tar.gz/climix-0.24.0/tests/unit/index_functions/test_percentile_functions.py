import pytest
import dask.array as da
import numpy as np

from climix.index_functions import percentile_functions as pf


TEST_HYNDMAN_FAN_PARAMETERS = [
    (
        1,
        10,
        da.array(32 / 3, dtype=np.int64),
        da.array((32 / 3 - int(32 / 3)), dtype=np.float64),
    ),
    (
        1.0,
        10.0,
        da.array(32 / 3, dtype=np.int64),
        da.array((32 / 3 - int(32 / 3)), dtype=np.float64),
    ),
    (
        1.0,
        da.array([10, 20]),
        da.array([32 / 3, 62 / 3], dtype=np.int64),
        da.array([(32 / 3 - int(32 / 3)), (62 / 3 - int(62 / 3))], dtype=np.float64),
    ),
    (
        1,
        np.array([10.0, 20.0]),
        np.array([32 / 3, 62 / 3], dtype=np.int64),
        np.array([(32 / 3 - int(32 / 3)), (62 / 3 - int(62 / 3))], dtype=np.float64),
    ),
    (
        1.0,
        da.array([[10], [20]]),
        da.array([[32 / 3], [62 / 3]], dtype=np.int64),
        da.array(
            [[(32 / 3 - int(32 / 3))], [(62 / 3 - int(62 / 3))]], dtype=np.float64
        ),
    ),
    (
        1.0,
        da.array([[10, 20], [20, 10]]),
        da.array([[32 / 3, 62 / 3], [62 / 3, 32 / 3]], dtype=np.int64),
        da.array(
            [
                [(32 / 3 - int(32 / 3)), (62 / 3 - int(62 / 3))],
                [(62 / 3 - int(62 / 3)), (32 / 3 - int(32 / 3))],
            ],
            dtype=np.float64,
        ),
    ),
    (
        1.0,
        da.ma.masked_array([[10, 20], [20, 10]]),
        da.array([[32 / 3, 62 / 3], [62 / 3, 32 / 3]], dtype=np.int64),
        da.array(
            [
                [(32 / 3 - int(32 / 3)), (62 / 3 - int(62 / 3))],
                [(62 / 3 - int(62 / 3)), (32 / 3 - int(32 / 3))],
            ],
            dtype=np.float64,
        ),
    ),
    (
        1.0,
        da.ma.masked_array([[[10, 20], [20, 10]], [[10, 20], [20, 10]]]),
        da.array(
            [
                [[32 / 3, 62 / 3], [62 / 3, 32 / 3]],
                [[32 / 3, 62 / 3], [62 / 3, 32 / 3]],
            ],
            dtype=np.int64,
        ),
        da.array(
            [
                [
                    [(32 / 3 - int(32 / 3)), (62 / 3 - int(62 / 3))],
                    [(62 / 3 - int(62 / 3)), (32 / 3 - int(32 / 3))],
                ],
                [
                    [(32 / 3 - int(32 / 3)), (62 / 3 - int(62 / 3))],
                    [(62 / 3 - int(62 / 3)), (32 / 3 - int(32 / 3))],
                ],
            ],
            dtype=np.float64,
        ),
    ),
]

TEST_HYNDMAN_FAN_TO_TOPK = [
    (10, 5, 5, da.array(-6, dtype=np.int64), np.array(-11, dtype=np.int64)),
    (10, 5, 5, da.array(-6, dtype=np.int64), np.array(-11, dtype=np.int64)),
    (10.0, 5.0, 5.0, da.array(-6, dtype=np.int64), np.array(-11, dtype=np.int64)),
    (10.0, 6.0, 5.0, da.array(4, dtype=np.int64), np.array(9, dtype=np.int64)),
    (
        da.array(10),
        da.array(6.0),
        5.0,
        da.array(4, dtype=np.int64),
        np.array(9, dtype=np.int64),
    ),
    (
        da.array([10, 20]),
        da.array([6, 20]),
        5.0,
        da.array([4, 0], dtype=np.int64),
        np.array(9, dtype=np.int64),
    ),
    (
        da.array([[10.0, 20.0], [20.0, 10.0]]),
        da.array([[6.0, 20.0], [20.0, 6.0]]),
        5.0,
        da.array([[4, 0], [0, 4]], dtype=np.int64),
        np.array(9, dtype=np.int64),
    ),
    (
        da.array([[10.0, 10.0], [10.0, 10.0]]),
        da.array([[5.0, 5.0], [5.0, 5.0]]),
        5,
        da.array([[-6, -6], [-6, -6]], dtype=np.int64),
        np.array(-11, dtype=np.int64),
    ),
]


@pytest.mark.parametrize(
    "prob, n, j_expected, gamma_expected", TEST_HYNDMAN_FAN_PARAMETERS
)
def test_hydman_fan_params(prob, n, j_expected, gamma_expected):
    """Test ``hyndman fan params``."""
    j, gamma = pf.hyndman_fan_params(prob, n)
    assert j == pytest.approx(j_expected)
    assert gamma == pytest.approx(gamma_expected)
    assert j.dtype == j_expected.dtype
    assert gamma.dtype == gamma_expected.dtype


@pytest.mark.parametrize(
    "n, j, window_size, k_expected, k_ext_expected", TEST_HYNDMAN_FAN_TO_TOPK
)
def test_hyndman_fan_to_topk(n, j, window_size, k_expected, k_ext_expected):
    """Test ``hyndman fan to topk``."""
    k, k_ext = pf.hyndman_fan_to_topk(n, j, window_size)
    assert k == pytest.approx(k_expected)
    assert k_ext == pytest.approx(k_ext_expected)
    assert k.dtype == k_expected.dtype
    assert k_ext.dtype == k_ext_expected.dtype
