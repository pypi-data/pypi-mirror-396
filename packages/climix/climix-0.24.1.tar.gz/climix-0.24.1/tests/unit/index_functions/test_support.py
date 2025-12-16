from contextlib import nullcontext as does_not_raise
import climix.index_functions.support
import numpy as np
import pytest
import iris.cube
import iris.coords
import iris.coord_categorisation
from typing import Any
import dask.array as da
from cf_units import Unit

TEST_ADD_MASK: dict[str, Any] = {
    "mask-start": (
        np.array(np.arange(8)).reshape(8, 1, 1),
        np.array([3]).reshape(1, 1),
        8,
        "start",
        does_not_raise(
            np.ma.masked_array(
                data=np.array(np.arange(8)).reshape(8, 1, 1),
                mask=np.array([[1, 1, 0, 0, 0, 0, 0, 0]]),
            )
        ),
    ),
    "mask-end": (
        np.array(np.arange(8)).reshape(8, 1, 1),
        np.array([3]).reshape(1, 1),
        8,
        "end",
        does_not_raise(
            np.ma.masked_array(
                data=np.array(np.arange(8)).reshape(8, 1, 1),
                mask=np.array([[0, 0, 1, 1, 1, 1, 1, 1]]),
            )
        ),
    ),
    "mask-end-threshold-1": (
        np.array(np.arange(8)).reshape(8, 1, 1),
        np.array([1]).reshape(1, 1),
        8,
        "end",
        does_not_raise(
            np.ma.masked_array(
                data=np.array(np.arange(8)).reshape(8, 1, 1),
                mask=np.array([[1, 1, 1, 1, 1, 1, 1, 1]]),
            )
        ),
    ),
    "mask-start-threshold-1": (
        np.array(np.arange(8)).reshape(8, 1, 1),
        np.array([1]).reshape(1, 1),
        8,
        "start",
        does_not_raise(
            np.ma.masked_array(
                data=np.array(np.arange(8)).reshape(8, 1, 1),
                mask=np.array([[0, 0, 0, 0, 0, 0, 0, 0]]),
            )
        ),
    ),
    "nan-values": (
        np.array(np.arange(8)).reshape(8, 1, 1),
        np.array([np.nan]).reshape(1, 1),
        8,
        "start",
        does_not_raise(
            np.ma.masked_array(
                data=np.array(np.arange(8)).reshape(8, 1, 1),
                mask=np.array([[1, 1, 1, 1, 1, 1, 1, 1]]),
            )
        ),
    ),
    "2x2": (
        np.array(np.arange(40)).reshape(10, 2, 2),
        np.array([[1, 3], [4, 10]]),
        10,
        "start",
        does_not_raise(
            np.ma.masked_array(
                data=np.array(np.arange(40)).reshape(10, 2, 2),
                mask=np.array(
                    [
                        [[0, 1], [1, 1]],
                        [[0, 1], [1, 1]],
                        [[0, 0], [1, 1]],
                        [[0, 0], [0, 1]],
                        [[0, 0], [0, 1]],
                        [[0, 0], [0, 1]],
                        [[0, 0], [0, 1]],
                        [[0, 0], [0, 1]],
                        [[0, 0], [0, 1]],
                        [[0, 0], [0, 0]],
                    ]
                ),
            )
        ),
    ),
}


parameter_names: tuple[str, ...] = (
    "data",
    "parameter_data",
    "length",
    "time_constraint",
    "expected_output",
)


@pytest.mark.parametrize(
    parameter_names,
    TEST_ADD_MASK.values(),
    ids=TEST_ADD_MASK.keys(),
)
def test_add_mask(data, parameter_data, length, time_constraint, expected_output):
    """Test funtion _add_mask()."""
    with expected_output:
        res = climix.index_functions.support._add_mask(
            data, parameter_data, length, time_constraint
        )
        assert np.array_equal(res, expected_output.enter_result, equal_nan=True)
        expected_mask = da.ma.getmaskarray(expected_output.enter_result)
        res_mask = da.ma.getmaskarray(res)
        assert (res_mask == expected_mask).all()
        assert res.dtype == data.dtype


TEST_MASK_DATA: dict[str, Any] = {
    "mask-start": (
        {
            "cubes": {
                "cube_1": {
                    "cube": iris.cube.Cube(
                        data=np.arange(40).reshape(10, 2, 2),
                        standard_name="air_temperature",
                        var_name="tas",
                        units="degree_Celsius",
                    ),
                    "dim_coord_time": iris.coords.DimCoord(
                        points=np.arange(0, 10, 1),
                        var_name="time",
                        standard_name="time",
                        units="days since 2022-01-01 00:00:00",
                    ),
                },
                "cube_2": {
                    "cube": iris.cube.Cube(
                        data=np.arange(start=1, stop=9).reshape(2, 2, 2),
                        standard_name=None,
                        var_name=None,
                        units="day",
                    ),
                    "dim_coord_time": iris.coords.DimCoord(
                        points=np.array([183, 365.5]),
                        var_name="time",
                        standard_name="time",
                        units="days since 2022-01-01 00:00:00",
                    ),
                },
            }
        },
        "start",
        does_not_raise(
            {
                "data": np.ma.masked_array(
                    data=np.arange(40).reshape(10, 2, 2),
                    mask=[
                        [[0, 1], [1, 1]],
                        [[0, 0], [1, 1]],
                        [[0, 0], [0, 1]],
                        [[0, 0], [0, 0]],
                        [[0, 0], [0, 0]],
                        [[0, 0], [0, 0]],
                        [[0, 0], [0, 0]],
                        [[0, 0], [0, 0]],
                        [[0, 0], [0, 0]],
                        [[0, 0], [0, 0]],
                    ],
                ),
                "parameters": np.arange(start=1, stop=5).reshape(1, 2, 2),
            }
        ),
    ),
    "mask-end": (
        {
            "cubes": {
                "cube_1": {
                    "cube": iris.cube.Cube(
                        data=da.asarray(np.arange(40).reshape(10, 2, 2)).rechunk(
                            1, 1, 1
                        ),
                        standard_name="air_temperature",
                        var_name="tas",
                        units="degree_Celsius",
                    ),
                    "dim_coord_time": iris.coords.DimCoord(
                        points=np.arange(0, 10, 1),
                        var_name="time",
                        standard_name="time",
                        units="days since 2022-01-01 00:00:00",
                    ),
                },
                "cube_2": {
                    "cube": iris.cube.Cube(
                        data=np.arange(start=1, stop=9).reshape(2, 2, 2),
                        standard_name=None,
                        var_name=None,
                        units="day",
                    ),
                    "dim_coord_time": iris.coords.DimCoord(
                        points=np.array([183, 365.5]),
                        var_name="time",
                        standard_name="time",
                        units="days since 2022-01-01 00:00:00",
                    ),
                },
            }
        },
        "end",
        does_not_raise(
            {
                "data": np.ma.masked_array(
                    data=np.arange(40).reshape(10, 2, 2),
                    mask=[
                        [[1, 0], [0, 0]],
                        [[1, 1], [0, 0]],
                        [[1, 1], [1, 0]],
                        [[1, 1], [1, 1]],
                        [[1, 1], [1, 1]],
                        [[1, 1], [1, 1]],
                        [[1, 1], [1, 1]],
                        [[1, 1], [1, 1]],
                        [[1, 1], [1, 1]],
                        [[1, 1], [1, 1]],
                    ],
                ),
                "parameters": np.arange(start=1, stop=5).reshape(1, 2, 2),
            }
        ),
    ),
    "nan-values": (
        {
            "cubes": {
                "cube_1": {
                    "cube": iris.cube.Cube(
                        data=np.array(
                            [
                                [[0, 1], [np.nan, 2]],
                                [[0, 1], [3, 2]],
                                [[0, 1], [3, np.nan]],
                                [[0, 1], [3, np.nan]],
                                [[0, 1], [3, 2]],
                            ],
                        ),
                        standard_name="air_temperature",
                        var_name="tas",
                        units="degree_Celsius",
                    ),
                    "dim_coord_time": iris.coords.DimCoord(
                        points=np.arange(0, 5, 1),
                        var_name="time",
                        standard_name="time",
                        units="days since 2022-01-01 00:00:00",
                    ),
                },
                "cube_2": {
                    "cube": iris.cube.Cube(
                        data=np.arange(start=2, stop=10).reshape(2, 2, 2),
                        standard_name=None,
                        var_name=None,
                        units="day",
                    ),
                    "dim_coord_time": iris.coords.DimCoord(
                        points=np.array([183, 365.5]),
                        var_name="time",
                        standard_name="time",
                        units="days since 2022-01-01 00:00:00",
                    ),
                },
            }
        },
        "end",
        does_not_raise(
            {
                "data": np.ma.masked_array(
                    data=[
                        [[0, 1], [np.nan, 2]],
                        [[0, 1], [3, 2]],
                        [[0, 1], [3, np.nan]],
                        [[0, 1], [3, np.nan]],
                        [[0, 1], [3, 2]],
                    ],
                    mask=[
                        [[0, 0], [0, 0]],
                        [[1, 0], [0, 0]],
                        [[1, 1], [0, 0]],
                        [[1, 1], [1, 0]],
                        [[1, 1], [1, 1]],
                    ],
                ),
                "parameters": np.arange(start=2, stop=6).reshape(1, 2, 2),
            }
        ),
    ),
    "masked-input": (
        {
            "cubes": {
                "cube_1": {
                    "cube": iris.cube.Cube(
                        data=np.ma.masked_array(
                            data=[
                                [[0, 1], [np.nan, 2]],
                                [[0, 1], [3, 2]],
                                [[0, 1], [3, np.nan]],
                                [[0, 1], [3, np.nan]],
                                [[0, 1], [3, 2]],
                            ],
                            mask=[
                                [[0, 1], [0, 1]],
                                [[0, 0], [0, 0]],
                                [[0, 0], [0, 0]],
                                [[0, 0], [0, 0]],
                                [[0, 0], [0, 1]],
                            ],
                        ),
                        standard_name="air_temperature",
                        var_name="tas",
                        units="degree_Celsius",
                    ),
                    "dim_coord_time": iris.coords.DimCoord(
                        points=np.arange(0, 5, 1),
                        var_name="time",
                        standard_name="time",
                        units="days since 2022-01-01 00:00:00",
                    ),
                },
                "cube_2": {
                    "cube": iris.cube.Cube(
                        data=np.arange(start=2, stop=10).reshape(2, 2, 2),
                        standard_name=None,
                        var_name=None,
                        units="day",
                    ),
                    "dim_coord_time": iris.coords.DimCoord(
                        points=np.array([183, 365.5]),
                        var_name="time",
                        standard_name="time",
                        units="days since 2022-01-01 00:00:00",
                    ),
                },
            }
        },
        "end",
        does_not_raise(
            {
                "data": np.ma.masked_array(
                    data=[
                        [[0, 1], [np.nan, 2]],
                        [[0, 1], [3, 2]],
                        [[0, 1], [3, np.nan]],
                        [[0, 1], [3, np.nan]],
                        [[0, 1], [3, 2]],
                    ],
                    mask=[
                        [[0, 1], [0, 1]],
                        [[1, 0], [0, 0]],
                        [[1, 1], [0, 0]],
                        [[1, 1], [1, 0]],
                        [[1, 1], [1, 1]],
                    ],
                ),
                "parameters": np.arange(start=2, stop=6).reshape(1, 2, 2),
            }
        ),
    ),
    "nan-values-in-parameters": (
        {
            "cubes": {
                "cube_1": {
                    "cube": iris.cube.Cube(
                        data=np.ma.masked_array(
                            data=[
                                [[0, 1], [np.nan, 2]],
                                [[0, 1], [3, 2]],
                                [[0, 1], [3, np.nan]],
                                [[0, 1], [3, np.nan]],
                                [[0, 1], [3, 2]],
                            ],
                            mask=[
                                [[0, 1], [0, 1]],
                                [[0, 0], [0, 0]],
                                [[0, 0], [0, 0]],
                                [[0, 0], [0, 0]],
                                [[0, 0], [0, 1]],
                            ],
                        ),
                        standard_name="air_temperature",
                        var_name="tas",
                        units="degree_Celsius",
                    ),
                    "dim_coord_time": iris.coords.DimCoord(
                        points=np.arange(0, 5, 1),
                        var_name="time",
                        standard_name="time",
                        units="days since 2022-01-01 00:00:00",
                    ),
                },
                "cube_2": {
                    "cube": iris.cube.Cube(
                        np.array(
                            [
                                [[np.nan, 1], [3, 2]],
                                [[0, np.nan], [3, 2]],
                            ]
                        ),
                        standard_name=None,
                        var_name=None,
                        units="day",
                    ),
                    "dim_coord_time": iris.coords.DimCoord(
                        points=np.array([183, 365.5]),
                        var_name="time",
                        standard_name="time",
                        units="days since 2022-01-01 00:00:00",
                    ),
                },
            }
        },
        "start",
        does_not_raise(
            {
                "data": np.ma.masked_array(
                    data=[
                        [[0, 1], [np.nan, 2]],
                        [[0, 1], [3, 2]],
                        [[0, 1], [3, np.nan]],
                        [[0, 1], [3, np.nan]],
                        [[0, 1], [3, 2]],
                    ],
                    mask=[
                        [[1, 1], [1, 1]],
                        [[1, 0], [1, 0]],
                        [[1, 0], [0, 0]],
                        [[1, 0], [0, 0]],
                        [[1, 0], [0, 1]],
                    ],
                ),
                "parameters": np.array(
                    [
                        [[np.nan, 1], [3, 2]],
                    ]
                ),
            }
        ),
    ),
    "high-threshold-values-start": (
        {
            "cubes": {
                "cube_1": {
                    "cube": iris.cube.Cube(
                        data=np.array(
                            [
                                [[0, 1], [np.nan, 2]],
                                [[0, 1], [3, 2]],
                                [[0, 1], [3, np.nan]],
                                [[0, 1], [3, np.nan]],
                                [[0, 1], [3, 2]],
                            ],
                        ),
                        standard_name="air_temperature",
                        var_name="tas",
                        units="degree_Celsius",
                    ),
                    "dim_coord_time": iris.coords.DimCoord(
                        points=np.arange(0, 5, 1),
                        var_name="time",
                        standard_name="time",
                        units="days since 2022-01-01 00:00:00",
                    ),
                },
                "cube_2": {
                    "cube": iris.cube.Cube(
                        np.array(
                            [
                                [[365, 1], [182, 3]],
                                [[365, 1], [182, 3]],
                            ]
                        ),
                        standard_name=None,
                        var_name=None,
                        units="day",
                    ),
                    "dim_coord_time": iris.coords.DimCoord(
                        points=np.array([183, 365.5]),
                        var_name="time",
                        standard_name="time",
                        units="days since 2022-01-01 00:00:00",
                    ),
                },
            }
        },
        "start",
        does_not_raise(
            {
                "data": np.ma.masked_array(
                    data=[
                        [[0, 1], [np.nan, 2]],
                        [[0, 1], [3, 2]],
                        [[0, 1], [3, np.nan]],
                        [[0, 1], [3, np.nan]],
                        [[0, 1], [3, 2]],
                    ],
                    mask=[
                        [[1, 0], [1, 1]],
                        [[1, 0], [1, 1]],
                        [[1, 0], [1, 0]],
                        [[1, 0], [1, 0]],
                        [[1, 0], [1, 0]],
                    ],
                ),
                "parameters": np.array(
                    [
                        [[365, 1], [182, 3]],
                    ]
                ),
            }
        ),
    ),
    "high-threshold-values-end": (
        {
            "cubes": {
                "cube_1": {
                    "cube": iris.cube.Cube(
                        data=np.array(
                            [
                                [[0, 1], [np.nan, 2]],
                                [[0, 1], [3, 2]],
                                [[0, 1], [3, np.nan]],
                                [[0, 1], [3, np.nan]],
                                [[0, 1], [3, 2]],
                            ],
                        ),
                        standard_name="air_temperature",
                        var_name="tas",
                        units="degree_Celsius",
                    ),
                    "dim_coord_time": iris.coords.DimCoord(
                        points=np.arange(0, 5, 1),
                        var_name="time",
                        standard_name="time",
                        units="days since 2022-01-01 00:00:00",
                    ),
                },
                "cube_2": {
                    "cube": iris.cube.Cube(
                        np.array(
                            [
                                [[365, 1], [182, 3]],
                                [[365, 1], [182, 3]],
                            ]
                        ),
                        standard_name=None,
                        var_name=None,
                        units="day",
                    ),
                    "dim_coord_time": iris.coords.DimCoord(
                        points=np.array([183, 365.5]),
                        var_name="time",
                        standard_name="time",
                        units="days since 2022-01-01 00:00:00",
                    ),
                },
            }
        },
        "end",
        does_not_raise(
            {
                "data": np.ma.masked_array(
                    data=[
                        [[0, 1], [np.nan, 2]],
                        [[0, 1], [3, 2]],
                        [[0, 1], [3, np.nan]],
                        [[0, 1], [3, np.nan]],
                        [[0, 1], [3, 2]],
                    ],
                    mask=[
                        [[0, 1], [0, 0]],
                        [[0, 1], [0, 0]],
                        [[0, 1], [0, 1]],
                        [[0, 1], [0, 1]],
                        [[0, 1], [0, 1]],
                    ],
                ),
                "parameters": np.array(
                    [
                        [[365, 1], [182, 3]],
                    ]
                ),
            }
        ),
    ),
    "mask_start-two-years": (
        {
            "cubes": {
                "cube_1": {
                    "cube": iris.cube.Cube(
                        data=np.arange(730).reshape(730, 1, 1),
                        standard_name="air_temperature",
                        var_name="tas",
                        units="degree_Celsius",
                    ),
                    "dim_coord_time": iris.coords.DimCoord(
                        points=np.arange(0, 730, 1),
                        var_name="time",
                        standard_name="time",
                        units="days since 2022-01-01 00:00:00",
                    ),
                },
                "cube_2": {
                    "cube": iris.cube.Cube(
                        data=np.arange(start=183, stop=185).reshape(2, 1, 1),
                        standard_name=None,
                        var_name=None,
                        units="day",
                    ),
                    "dim_coord_time": iris.coords.DimCoord(
                        points=np.array([183, 365.5]),
                        var_name="time",
                        standard_name="time",
                        units="days since 2022-01-01 00:00:00",
                    ),
                },
            }
        },
        "start",
        does_not_raise(
            {
                "data": np.ma.masked_array(
                    data=np.arange(730).reshape(730, 1, 1),
                    mask=np.concatenate(
                        (np.ones(182), np.zeros(183), np.ones(183), np.zeros(182)),
                        axis=0,
                    ),
                ),
                "parameters": np.arange(start=183, stop=185).reshape(2, 1, 1),
            }
        ),
    ),
    "mask-start-offset": (
        {
            "cubes": {
                "cube_1": {
                    "cube": iris.cube.Cube(
                        data=np.ones(362).reshape(362, 1, 1),
                        standard_name="air_temperature",
                        var_name="tas",
                        units="degree_Celsius",
                    ),
                    "dim_coord_time": iris.coords.DimCoord(
                        points=np.concatenate(
                            (np.arange(31, 212, 1), np.arange(396, 577, 1)),
                            axis=0,
                        ),
                        var_name="time",
                        standard_name="time",
                        units="days since 2022-01-01 00:00:00",
                    ),
                },
                "cube_2": {
                    "cube": iris.cube.Cube(
                        data=np.array([32, 182]).reshape(2, 1, 1),
                        standard_name=None,
                        var_name=None,
                        units="day",
                    ),
                    "dim_coord_time": iris.coords.DimCoord(
                        points=np.array([183, 365.5]),
                        var_name="time",
                        standard_name="time",
                        units="days since 2022-01-01 00:00:00",
                    ),
                },
            }
        },
        "start",
        does_not_raise(
            {
                "data": np.ma.masked_array(
                    data=np.ones(362).reshape(362, 1, 1),
                    mask=np.concatenate(
                        (np.zeros(181), np.ones(150), np.zeros(31)),
                        axis=0,
                    ).reshape(362, 1, 1),
                ),
                "parameters": np.array([1, 151]).reshape(2, 1, 1),
            }
        ),
    ),
    "mask-end-offset": (
        {
            "cubes": {
                "cube_1": {
                    "cube": iris.cube.Cube(
                        data=np.ones(362).reshape(362, 1, 1),
                        standard_name="air_temperature",
                        var_name="tas",
                        units="degree_Celsius",
                    ),
                    "dim_coord_time": iris.coords.DimCoord(
                        points=np.concatenate(
                            (np.arange(31, 212, 1), np.arange(396, 577, 1)),
                            axis=0,
                        ),
                        var_name="time",
                        standard_name="time",
                        units="days since 2022-01-01 00:00:00",
                    ),
                },
                "cube_2": {
                    "cube": iris.cube.Cube(
                        data=np.array([31, 182]).reshape(2, 1, 1),
                        standard_name=None,
                        var_name=None,
                        units="day",
                    ),
                    "dim_coord_time": iris.coords.DimCoord(
                        points=np.array([183, 365.5]),
                        var_name="time",
                        standard_name="time",
                        units="days since 2022-01-01 00:00:00",
                    ),
                },
            }
        },
        "end",
        does_not_raise(
            {
                "data": np.ma.masked_array(
                    data=np.ones(362).reshape(362, 1, 1),
                    mask=np.concatenate(
                        (np.ones(181), np.zeros(150), np.ones(31)),
                        axis=0,
                    ).reshape(362, 1, 1),
                ),
                "parameters": np.array([0, 151]).reshape(2, 1, 1),
            }
        ),
    ),
}


parameter_names = (
    "f_cubes",
    "time_constraint",
    "expected_output",
)
fixtures = ["f_cubes"]


@pytest.mark.parametrize(
    parameter_names,
    TEST_MASK_DATA.values(),
    ids=TEST_MASK_DATA.keys(),
    indirect=fixtures,
)
def test_mask_data(f_cubes, time_constraint, expected_output):
    """Test funtion _mask_data()."""
    with expected_output:
        cube_1 = f_cubes["cube_1"]
        cube_2 = f_cubes["cube_2"]
        iris.coord_categorisation.add_year(cube_1, "time")
        iris.coord_categorisation.add_year(cube_2, "time")
        res, parameters = climix.index_functions.support._mask_data(
            cube_1, cube_2, time_constraint
        )
        expected_result = expected_output.enter_result["data"]
        expected_parameters = expected_output.enter_result["parameters"]
        assert np.array_equal(res, expected_result, equal_nan=True)
        expected_mask = da.ma.getmaskarray(expected_result)
        res_mask = da.ma.getmaskarray(res)
        assert (res_mask == expected_mask).all()
        assert res.dtype == np.float32
        assert np.array_equal(parameters, expected_parameters, equal_nan=True)


TEST_MASK_DATA_FROM_PARAMETERS: dict[str, Any] = {
    "mask-start-and-end": (
        {
            "cubes": {
                "data": {
                    "cube": iris.cube.Cube(
                        data=da.asarray(np.arange(40).reshape(10, 2, 2)).rechunk(
                            1, 1, 1
                        ),
                        standard_name="air_temperature",
                        var_name="tas",
                        units="degree_Celsius",
                    ),
                    "dim_coord_time": iris.coords.DimCoord(
                        points=np.arange(0, 10, 1),
                        var_name="time",
                        standard_name="time",
                        units="days since 2022-01-01 00:00:00",
                    ),
                },
                "start": {
                    "cube": iris.cube.Cube(
                        data=np.arange(start=1, stop=9).reshape(2, 2, 2),
                        standard_name=None,
                        var_name=None,
                        units="day",
                    ),
                    "dim_coord_time": iris.coords.DimCoord(
                        points=np.array([183, 365.5]),
                        var_name="time",
                        standard_name="time",
                        units="days since 2022-01-01 00:00:00",
                    ),
                },
                "end": {
                    "cube": iris.cube.Cube(
                        data=np.arange(start=8, stop=16).reshape(2, 2, 2),
                        standard_name=None,
                        var_name=None,
                        units="day",
                    ),
                    "dim_coord_time": iris.coords.DimCoord(
                        points=np.array([183, 365.5]),
                        var_name="time",
                        standard_name="time",
                        units="days since 2022-01-01 00:00:00",
                    ),
                },
            }
        },
        does_not_raise(
            {
                "data": np.ma.masked_array(
                    data=np.arange(40).reshape(10, 2, 2),
                    mask=[
                        [[0, 1], [1, 1]],
                        [[0, 0], [1, 1]],
                        [[0, 0], [0, 1]],
                        [[0, 0], [0, 0]],
                        [[0, 0], [0, 0]],
                        [[0, 0], [0, 0]],
                        [[0, 0], [0, 0]],
                        [[1, 0], [0, 0]],
                        [[1, 1], [0, 0]],
                        [[1, 1], [1, 0]],
                    ],
                    dtype=np.int64,
                ),
                "aux_coord": [
                    iris.coords.AuxCoord(
                        np.arange(start=1, stop=5).reshape(1, 2, 2),
                        var_name="mask-start",
                        long_name="Day-of-year for which data have been masked.",
                        units=Unit("day"),
                    ),
                    iris.coords.AuxCoord(
                        np.arange(start=8, stop=12).reshape(1, 2, 2),
                        var_name="mask-end",
                        long_name="Day-of-year for which data have been masked.",
                        units=Unit("day"),
                    ),
                ],
            },
        ),
    ),
    "mask-start": (
        {
            "cubes": {
                "data": {
                    "cube": iris.cube.Cube(
                        data=da.asarray(
                            np.arange(40, dtype=np.int32).reshape(10, 2, 2)
                        ).rechunk(1, 1, 1),
                        standard_name="air_temperature",
                        var_name="tas",
                        units="degree_Celsius",
                    ),
                    "dim_coord_time": iris.coords.DimCoord(
                        points=np.arange(0, 10, 1),
                        var_name="time",
                        standard_name="time",
                        units="days since 2022-01-01 00:00:00",
                    ),
                },
                "start": {
                    "cube": iris.cube.Cube(
                        data=np.arange(start=1, stop=9).reshape(2, 2, 2),
                        standard_name=None,
                        var_name=None,
                        units="day",
                    ),
                    "dim_coord_time": iris.coords.DimCoord(
                        points=np.array([183, 365.5]),
                        var_name="time",
                        standard_name="time",
                        units="days since 2022-01-01 00:00:00",
                    ),
                },
            }
        },
        does_not_raise(
            {
                "data": np.ma.masked_array(
                    data=np.arange(40).reshape(10, 2, 2),
                    mask=[
                        [[0, 1], [1, 1]],
                        [[0, 0], [1, 1]],
                        [[0, 0], [0, 1]],
                        [[0, 0], [0, 0]],
                        [[0, 0], [0, 0]],
                        [[0, 0], [0, 0]],
                        [[0, 0], [0, 0]],
                        [[0, 0], [0, 0]],
                        [[0, 0], [0, 0]],
                        [[0, 0], [0, 0]],
                    ],
                    dtype=np.int32,
                ),
                "aux_coord": [
                    iris.coords.AuxCoord(
                        np.arange(start=1, stop=5).reshape(1, 2, 2),
                        var_name="mask-start",
                        long_name="Day-of-year for which data have been masked.",
                        units=Unit("day"),
                    )
                ],
            },
        ),
    ),
    "mask-end": (
        {
            "cubes": {
                "data": {
                    "cube": iris.cube.Cube(
                        data=da.asarray(
                            np.arange(40, dtype=np.float32).reshape(10, 2, 2)
                        ).rechunk(1, 1, 1),
                        standard_name="air_temperature",
                        var_name="tas",
                        units="degree_Celsius",
                    ),
                    "dim_coord_time": iris.coords.DimCoord(
                        points=np.arange(0, 10, 1),
                        var_name="time",
                        standard_name="time",
                        units="days since 2022-01-01 00:00:00",
                    ),
                },
                "end": {
                    "cube": iris.cube.Cube(
                        data=np.arange(start=8, stop=16).reshape(2, 2, 2),
                        standard_name=None,
                        var_name=None,
                        units="day",
                    ),
                    "dim_coord_time": iris.coords.DimCoord(
                        points=np.array([183, 365.5]),
                        var_name="time",
                        standard_name="time",
                        units="days since 2022-01-01 00:00:00",
                    ),
                },
            }
        },
        does_not_raise(
            {
                "data": (
                    np.ma.masked_array(
                        data=np.arange(40).reshape(10, 2, 2),
                        mask=[
                            [[0, 0], [0, 0]],
                            [[0, 0], [0, 0]],
                            [[0, 0], [0, 0]],
                            [[0, 0], [0, 0]],
                            [[0, 0], [0, 0]],
                            [[0, 0], [0, 0]],
                            [[0, 0], [0, 0]],
                            [[1, 0], [0, 0]],
                            [[1, 1], [0, 0]],
                            [[1, 1], [1, 0]],
                        ],
                        dtype=np.float32,
                    )
                ),
                "aux_coord": [
                    iris.coords.AuxCoord(
                        np.arange(start=8, stop=12).reshape(1, 2, 2),
                        var_name="mask-end",
                        long_name="Day-of-year for which data have been masked.",
                        units=Unit("day"),
                    )
                ],
            }
        ),
    ),
}


parameter_names = ("f_cubes", "expected_output")
fixtures = ["f_cubes"]


@pytest.mark.parametrize(
    parameter_names,
    TEST_MASK_DATA_FROM_PARAMETERS.values(),
    ids=TEST_MASK_DATA_FROM_PARAMETERS.keys(),
    indirect=fixtures,
)
def test_mask_data_from_parameters(f_cubes, expected_output):
    """Test funtion mask_data_from_parameters()."""
    with expected_output:
        params = {}
        for key, value in f_cubes.items():
            iris.coord_categorisation.add_year(value, "time")
            params.update({key: value})
        input_cube = params.pop("data")
        dtype = input_cube.data.dtype
        input_cubes = {"data": input_cube}
        aux_coord = climix.index_functions.support.mask_data_from_parameters(
            input_cubes, params
        )
        res = input_cubes["data"].data
        expected_res = expected_output.enter_result["data"]
        expected_aux_coord = expected_output.enter_result["aux_coord"]
        assert np.array_equal(res, expected_res, equal_nan=True)
        expected_mask = da.ma.getmaskarray(expected_res)
        res_mask = da.ma.getmaskarray(res)
        assert (res_mask == expected_mask).all()
        assert res.dtype == dtype == expected_res.dtype
        for coord, exp in zip(aux_coord, expected_aux_coord):
            assert coord.var_name == exp.var_name
            assert coord.long_name == exp.long_name
            assert np.array_equal(coord.points, exp.points, equal_nan=True)
            assert coord.units == exp.units


TEST_COMPUTE_OFFSET: dict[str, Any] = {
    "offset-0": (
        {
            "cubes": {
                "cube": {
                    "cube": iris.cube.Cube(
                        data=da.asarray(
                            np.arange(40, dtype=np.float32).reshape(10, 2, 2)
                        ).rechunk(1, 1, 1),
                        standard_name="air_temperature",
                        var_name="tas",
                        units="degree_Celsius",
                    ),
                    "dim_coord_time": iris.coords.DimCoord(
                        points=np.arange(0.5, 10.5, 1),
                        var_name="time",
                        standard_name="time",
                        units="days since 2022-01-01 00:00:00",
                    ),
                },
            },
        },
        2022,
        does_not_raise(0),
    ),
    "offset-31": (
        {
            "cubes": {
                "cube": {
                    "cube": iris.cube.Cube(
                        data=da.asarray(
                            np.arange(40, dtype=np.float32).reshape(10, 2, 2)
                        ).rechunk(1, 1, 1),
                        standard_name="air_temperature",
                        var_name="tas",
                        units="degree_Celsius",
                    ),
                    "dim_coord_time": iris.coords.DimCoord(
                        points=np.arange(31.5, 41.5, 1),
                        var_name="time",
                        standard_name="time",
                        units="days since 2022-01-01 00:00:00",
                    ),
                },
            },
        },
        2022,
        does_not_raise(31),
    ),
    "offset-100": (
        {
            "cubes": {
                "cube": {
                    "cube": iris.cube.Cube(
                        data=da.asarray(
                            np.arange(40, dtype=np.float32).reshape(10, 2, 2)
                        ).rechunk(1, 1, 1),
                        standard_name="air_temperature",
                        var_name="tas",
                        units="degree_Celsius",
                    ),
                    "dim_coord_time": iris.coords.DimCoord(
                        points=np.arange(100.5, 110.5, 1),
                        var_name="time",
                        standard_name="time",
                        units="days since 2022-01-01 00:00:00",
                    ),
                },
            },
        },
        2022,
        does_not_raise(100),
    ),
    "offset-seconds-31-days": (
        {
            "cubes": {
                "cube": {
                    "cube": iris.cube.Cube(
                        data=da.asarray(
                            np.arange(40, dtype=np.float32).reshape(10, 2, 2)
                        ).rechunk(1, 1, 1),
                        standard_name="air_temperature",
                        var_name="tas",
                        units="degree_Celsius",
                    ),
                    "dim_coord_time": iris.coords.DimCoord(
                        points=np.arange(2721600, 3585600, 86400),
                        var_name="time",
                        standard_name="time",
                        units="seconds since 2022-01-01 00:00:00",
                    ),
                },
            },
        },
        2022,
        does_not_raise(31),
    ),
}


parameter_names = ("f_cubes", "year", "expected_output")
fixtures = ["f_cubes"]


@pytest.mark.parametrize(
    parameter_names,
    TEST_COMPUTE_OFFSET.values(),
    ids=TEST_COMPUTE_OFFSET.keys(),
    indirect=fixtures,
)
def test_compute_offset(f_cubes, year, expected_output):
    """Test funtion _compute_offset()."""
    with expected_output:
        cube = f_cubes["cube"]
        offset = climix.index_functions.support._compute_offset(cube, year)
        assert offset == expected_output.enter_result
