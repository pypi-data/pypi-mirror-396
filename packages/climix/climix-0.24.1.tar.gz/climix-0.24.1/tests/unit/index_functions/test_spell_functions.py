from typing import Any

from cf_units import Unit
import dask.array as da
from dask.distributed import Client
import numpy as np
import pytest
import iris.coords

from climix.index_functions import spell_functions as spl_func
from .test_index_functions import lazy_func_test


TEST_SEASON_START_CALL_PARAMETERS = [
    (
        {
            "data": np.arange(60).reshape(15, 2, 2),
            "units": "degree_Celsius",
        },  # data
        {
            "data": 5,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # threshold
        ">",  # condition
        {"data": 6, "units": "days"},  # duration
        {"data": 0, "units": "days"},  # delay
        np.array(
            [
                [
                    [
                        [15.0, np.nan],
                        [0.0, np.nan],
                        [3.0, np.nan],
                        [13.0, np.nan],
                        [0.0, np.nan],
                        [5.0, np.nan],
                    ],
                    [
                        [15.0, np.nan],
                        [0.0, np.nan],
                        [3.0, np.nan],
                        [13.0, np.nan],
                        [0.0, np.nan],
                        [5.0, np.nan],
                    ],
                ],
                [
                    [
                        [15.0, np.nan],
                        [0.0, np.nan],
                        [2.0, np.nan],
                        [14.0, np.nan],
                        [0.0, np.nan],
                        [5.0, np.nan],
                    ],
                    [
                        [15.0, np.nan],
                        [0.0, np.nan],
                        [2.0, np.nan],
                        [14.0, np.nan],
                        [0.0, np.nan],
                        [5.0, np.nan],
                    ],
                ],
            ]
        ),  # expected
    ),  # ordinary np, tests end spell
    (
        {
            "data": np.ma.masked_array(
                [
                    [[6, 7], [0, 0]],
                    [[6, 7], [-6, 3]],
                    [[4, 7], [-10, 6]],
                    [[7, 7], [5, 7]],
                    [[7, 7], [7, 8]],
                    [[7, 7], [7, 5]],
                ],
                mask=[
                    [[0, 0], [0, 0]],
                    [[0, 0], [0, 0]],
                    [[1, 0], [0, 0]],
                    [[0, 0], [0, 0]],
                    [[0, 0], [0, 0]],
                    [[0, 0], [0, 0]],
                ],
            ),
            "units": "degree_Celsius",
        },  # data
        {
            "data": 5,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # threshold
        ">",  # condition
        {"data": 3, "units": "days"},  # duration
        {"data": 0, "units": "days"},  # delay
        np.ma.masked_array(
            data=[
                [
                    [
                        [6.0, np.nan],
                        [2.0, np.nan],
                        [4.0, np.nan],
                        [3.0, np.nan],
                        [2.0, np.nan],
                        [2.0, np.nan],
                    ],
                    [
                        [6.0, np.nan],
                        [6.0, np.nan],
                        [1.0, np.nan],
                        [6.0, np.nan],
                        [2.0, np.nan],
                        [2.0, np.nan],
                    ],
                ],
                [
                    [
                        [6.0, np.nan],
                        [0.0, np.nan],
                        [np.nan, np.nan],
                        [2.0, np.nan],
                        [0.0, np.nan],
                        [2.0, np.nan],
                    ],
                    [
                        [6.0, np.nan],
                        [0.0, np.nan],
                        [3.0, np.nan],
                        [0.0, np.nan],
                        [0.0, np.nan],
                        [0.0, np.nan],
                    ],
                ],
            ],
            mask=[
                [
                    [[1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1]],
                    [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]],
                ],
                [
                    [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]],
                    [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]],
                ],
            ],
        ),
        # expected
    ),  # masked np, tests masked end-spell, full-spell, non-spell, internal-spell
    (
        {
            "data": da.array(
                [
                    [[6, 7], [8, 0]],
                    [[6, 7], [5, 7]],
                    [[10, 5], [5, 7]],
                    [[5, 7], [5, 7]],
                    [[7, 7], [7, 4]],
                    [[7, 5], [7, 7]],
                    [[7, 7], [7, 7]],
                    [[7, 7], [5, 7]],
                    [[7, 7], [7, 5]],
                ],
            ),
            "units": "degree_Celsius",
        },  # data
        {
            "data": 5,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # threshold
        ">",  # condition
        {"data": 3, "units": "days"},  # duration
        {"data": 0, "units": "days"},  # delay
        np.ma.masked_array(
            [
                [
                    [
                        [9.0, np.nan],
                        [3.0, np.nan],
                        [1.0, np.nan],
                        [5.0, np.nan],
                        [2.0, np.nan],
                        [2.0, np.nan],
                    ],
                    [
                        [9.0, np.nan],
                        [2.0, np.nan],
                        [7.0, np.nan],
                        [3.0, np.nan],
                        [2.0, np.nan],
                        [2.0, np.nan],
                    ],
                ],
                [
                    [
                        [9.0, np.nan],
                        [1.0, np.nan],
                        [5.0, np.nan],
                        [1.0, np.nan],
                        [1.0, np.nan],
                        [1.0, np.nan],
                    ],
                    [
                        [9.0, np.nan],
                        [0.0, np.nan],
                        [2.0, np.nan],
                        [0.0, np.nan],
                        [0.0, np.nan],
                        [0.0, np.nan],
                    ],
                ],
            ]
        ),  # expected
    ),  # ordinary da, tests double-spell, end-spell, internal-spell,
    # double-internal-spell
    (
        {
            "data": da.arange(30).reshape(30, 1, 1).rechunk(chunks=(10, -1, -1)),
            "units": "degree_Celsius",
        },  # data
        {
            "data": 50,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # threshold
        ">",  # condition
        {"data": 6, "units": "days"},  # duration
        {"data": 0, "units": "days"},  # delay
        np.ma.masked_array(
            [
                [
                    [
                        [30.0, np.nan],
                        [0.0, np.nan],
                        [np.nan, np.nan],
                        [0.0, np.nan],
                        [0.0, np.nan],
                        [0.0, np.nan],
                    ]
                ]
            ]
        ),  # expected
    ),  # tests no start and three chunks
    (
        {
            "data": da.arange(34).reshape(34, 1, 1).rechunk(chunks=(10, -1, -1)),
            "units": "degree_Celsius",
        },  # data
        {
            "data": 13,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # threshold
        ">",  # condition
        {"data": 6, "units": "days"},  # duration
        {"data": 0, "units": "days"},  # delay
        np.ma.masked_array(
            [
                [
                    [
                        [34.0, np.nan],
                        [0.0, np.nan],
                        [15.0, np.nan],
                        [20.0, np.nan],
                        [0.0, np.nan],
                        [5.0, np.nan],
                    ]
                ]
            ]
        ),  # expected
    ),  # tests start in second chunk and three chunks
    (
        {
            "data": da.arange(30).reshape(30, 1, 1).rechunk(chunks=(10, -1, -1)),
            "units": "degree_Celsius",
        },  # data
        {
            "data": 15,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # threshold
        ">",  # condition
        {"data": 6, "units": "days"},  # duration
        {"data": 0, "units": "days"},  # delay
        np.ma.masked_array(
            [
                [
                    [
                        [30.0, np.nan],
                        [0.0, np.nan],
                        [17.0, np.nan],
                        [14.0, np.nan],
                        [0.0, np.nan],
                        [5.0, np.nan],
                    ]
                ]
            ]
        ),  # expected
    ),  # tests start between chunks 2-3
    (
        {
            "data": da.arange(12000).reshape(3000, 2, 2).rechunk(chunks=(100, 1, 2)),
            "units": "degree_Celsius",
        },  # data
        {
            "data": -1,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # threshold
        ">",  # condition
        {"data": 6, "units": "days"},  # duration
        {"data": 0, "units": "days"},  # delay
        np.array(
            [
                [
                    [
                        [3000, np.nan],
                        [3000, np.nan],
                        [1.0, np.nan],
                        [3000, np.nan],
                        [5.0, np.nan],
                        [5.0, np.nan],
                    ],
                    [
                        [3000, np.nan],
                        [3000, np.nan],
                        [1.0, np.nan],
                        [3000, np.nan],
                        [5.0, np.nan],
                        [5.0, np.nan],
                    ],
                ],
                [
                    [
                        [3000, np.nan],
                        [3000, np.nan],
                        [1.0, np.nan],
                        [3000, np.nan],
                        [5.0, np.nan],
                        [5.0, np.nan],
                    ],
                    [
                        [3000, np.nan],
                        [3000, np.nan],
                        [1.0, np.nan],
                        [3000, np.nan],
                        [5.0, np.nan],
                        [5.0, np.nan],
                    ],
                ],
            ]
        ),  # expected
    ),  # tests spell that covers all data
    (
        {
            "data": da.arange(50).reshape(50, 1, 1).rechunk(chunks=(5, -1, -1)),
            "units": "degree_Celsius",
        },  # data
        {
            "data": 4,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # threshold
        ">",  # condition
        {"data": 20, "units": "days"},  # duration
        {"data": 0, "units": "days"},  # delay
        np.ma.masked_array(
            [
                [
                    [
                        [50.0, np.nan],
                        [0.0, np.nan],
                        [6.0, np.nan],
                        [45.0, np.nan],
                        [0.0, np.nan],
                        [19.0, np.nan],
                    ]
                ]
            ]
        ),  # expected
    ),  # tests end-spell and duration covers multiple cells
]

TEST_SEASON_START_POST_PROCESS_PARAMETERS = [
    (
        {
            "data": np.ma.masked_array(
                data=[
                    [
                        [
                            [
                                [15.0, np.nan],
                                [2.0, np.nan],
                                [np.nan, np.nan],
                                [2.0, np.nan],
                                [2.0, np.nan],
                                [3.0, np.nan],
                            ],
                            [
                                [15.0, np.nan],
                                [15.0, np.nan],
                                [1.0, np.nan],
                                [15.0, np.nan],
                                [5.0, np.nan],
                                [5.0, np.nan],
                            ],
                        ]
                    ],
                ],
            ),
            "units": "degree_Celsius",
        },  # data
        {
            "data": 5,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # threshold
        ">",  # condition
        {"data": 6, "units": "days"},  # duration
        {"data": 0, "units": "days"},  # start delay
        np.array([[[np.nan, 1]]]),
    ),  # postprocessing no-merging
    (
        {
            "data": np.ma.masked_array(
                data=[
                    [
                        [
                            [
                                [15.0, np.nan],
                                [2.0, np.nan],
                                [np.nan, np.nan],
                                [2.0, np.nan],
                                [2.0, np.nan],
                                [3.0, np.nan],
                            ],
                            [
                                [15.0, np.nan],
                                [0.0, np.nan],
                                [np.nan, np.nan],
                                [1.0, np.nan],
                                [0.0, np.nan],
                                [1.0, np.nan],
                            ],
                        ]
                    ],
                    [
                        [
                            [
                                [15.0, np.nan],
                                [3.0, np.nan],
                                [8.0, np.nan],
                                [7.0, np.nan],
                                [3.0, np.nan],
                                [3.0, np.nan],
                            ],
                            [
                                [15.0, np.nan],
                                [15.0, np.nan],
                                [1.0, np.nan],
                                [15.0, np.nan],
                                [5.0, np.nan],
                                [5.0, np.nan],
                            ],
                        ]
                    ],
                ],
            ),
            "units": "degree_Celsius",
        },  # data
        {
            "data": 5,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # threshold
        ">",  # condition
        {"data": 6, "units": "days"},  # duration
        {"data": 0, "units": "days"},  # start delay
        np.array([[[13, 15]], [[8, 1]]]),
    ),  # postprocessing merging, start between years, start at end of year,
    # start in year
]

parameter_names = (
    "f_cube_tas, f_first_threshold, condition, f_first_duration, "
    + "f_second_delay, expected"
)
fixtures = ["f_cube_tas", "f_first_threshold", "f_first_duration", "f_second_delay"]


@pytest.mark.parametrize(
    parameter_names, TEST_SEASON_START_CALL_PARAMETERS, indirect=fixtures
)
def test_season_start_lazy_func(
    f_cube_tas,
    f_first_threshold,
    condition,
    f_first_duration,
    f_second_delay,
    expected,
    f_dask_cluster,
):
    parameters = {
        "threshold": f_first_threshold,
        "condition": condition,
        "duration": f_first_duration,
        "delay": f_second_delay,
    }
    index_function = spl_func.SeasonStart(**parameters)
    with Client(f_dask_cluster) as client:
        lazy_func_test(index_function, f_cube_tas, expected, client)
        assert index_function.units == Unit("days")


@pytest.mark.parametrize(
    parameter_names, TEST_SEASON_START_POST_PROCESS_PARAMETERS, indirect=fixtures
)
def test_season_start_post_process(
    f_cube_tas, f_first_threshold, condition, f_first_duration, f_second_delay, expected
):
    parameters = {
        "threshold": f_first_threshold,
        "condition": condition,
        "duration": f_first_duration,
        "delay": f_second_delay,
    }
    index_function = spl_func.SeasonStart(**parameters)
    data = f_cube_tas.data
    aggregateby_cube = f_cube_tas
    cube, res = index_function.post_process(aggregateby_cube, data, None, None)
    assert np.array_equal(res, expected, equal_nan=True)
    expected_mask = np.ma.getmaskarray(expected)
    res_mask = np.ma.getmaskarray(res)
    assert (res_mask == expected_mask).all()


# output form:
# columns: start, end dependent
# rows: length, spell beginning, index, spell end, spell start data, spell end data
TEST_SEASON_END_CALL_PARAMETERS = [
    (
        {
            "data": np.arange(60).reshape(15, 2, 2),
            "units": "degree_Celsius",
        },  # data
        {
            "data": 5,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # start threshold
        ">",  # start condition
        {
            "data": 20,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # end threshold
        ">",  # end condition
        {"data": 3, "units": "days"},  # start duration
        {"data": 3, "units": "days"},  # end duration
        {"data": 0, "units": "days"},  # start delay
        {"data": 0, "units": "days"},  # end delay
        np.ma.masked_array(
            [
                [
                    [
                        [15.0, 15.0],
                        [0.0, 0.0],
                        [3.0, 7.0],
                        [13.0, 9.0],
                        [0.0, 0.0],
                        [2.0, 2.0],
                    ],
                    [
                        [15.0, 15.0],
                        [0.0, 0.0],
                        [3.0, 6.0],
                        [13.0, 10.0],
                        [0.0, 0.0],
                        [2.0, 2.0],
                    ],
                ],
                [
                    [
                        [15.0, 15.0],
                        [0.0, 0.0],
                        [2.0, 6.0],
                        [14.0, 10.0],
                        [0.0, 0.0],
                        [2.0, 2.0],
                    ],
                    [
                        [15.0, 15.0],
                        [0.0, 0.0],
                        [2.0, 6.0],
                        [14.0, 10.0],
                        [0.0, 0.0],
                        [2.0, 2.0],
                    ],
                ],
            ]
        ),  # expected
    ),  # ordinary np, tests spell at the end
    (
        {
            "data": np.ma.masked_array(
                [
                    [[6, 7], [4, 0]],
                    [[6, 7], [3, 3]],
                    [[6, 7], [2, 4]],
                    [[2, 7], [4, 7]],
                    [[3, 7], [3, 8]],
                    [[4, 7], [2, 6]],
                ],
                mask=[
                    [[0, 0], [0, 0]],
                    [[0, 0], [0, 0]],
                    [[1, 0], [0, 0]],
                    [[0, 0], [0, 0]],
                    [[0, 0], [0, 0]],
                    [[0, 0], [0, 0]],
                ],
            ),
            "units": "degree_Celsius",
        },  # data
        {
            "data": 5,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # start threshold
        ">",  # start condition
        {
            "data": 5,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # end threshold
        "<",  # end condition
        {"data": 3, "units": "days"},  # start duration
        {"data": 3, "units": "days"},  # end duration
        {"data": 0, "units": "days"},  # start delay
        {"data": 0, "units": "days"},  # end delay
        np.ma.masked_array(
            data=[
                [
                    [
                        [6.0, 6.0],
                        [2.0, 0.0],
                        [np.nan, np.nan],
                        [0.0, 3.0],
                        [2.0, 0.0],
                        [0.0, 2.0],
                    ],
                    [
                        [6.0, 6.0],
                        [6.0, 0.0],
                        [1.0, np.nan],
                        [6.0, 0.0],
                        [2.0, 0.0],
                        [2.0, 0.0],
                    ],
                ],
                [
                    [
                        [6.0, 6.0],
                        [0.0, 6.0],
                        [np.nan, np.nan],
                        [0.0, 6.0],
                        [0.0, 2.0],
                        [0.0, 2.0],
                    ],
                    [
                        [6.0, 6.0],
                        [0.0, 3.0],
                        [4.0, np.nan],
                        [3.0, 0.0],
                        [0.0, 2.0],
                        [2.0, 0.0],
                    ],
                ],
            ],
            mask=[
                [
                    [[1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1]],
                    [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]],
                ],
                [
                    [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]],
                    [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]],
                ],
            ],
        ),  # expected
    ),  # masked np, tests masked-start-spell, no-spell,
    # no-start, end-before-start-spell
    (
        {
            "data": da.array(
                [
                    [[6, 7], [4, 0]],
                    [[6, 7], [4, 3]],
                    [[10, 5], [4, 3]],
                    [[5, 5], [6, 3]],
                    [[4, 5], [6, 7]],
                    [[4, 5], [6, 7]],
                    [[4, 7], [2, 4]],
                    [[7, 7], [2, 4]],
                    [[7, 7], [2, 4]],
                ],
            ),
            "units": "degree_Celsius",
        },  # data
        {
            "data": 5,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # start threshold
        ">",  # start condition
        {
            "data": 5,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # end threshold
        "<",  # end condition
        {"data": 3, "units": "days"},  # start duration
        {"data": 3, "units": "days"},  # end duration
        {"data": 0, "units": "days"},  # start delay
        {"data": 0, "units": "days"},  # end delay
        np.ma.masked_array(
            [
                [
                    [
                        [9.0, 9.0],
                        [3.0, 0.0],
                        [1.0, 5.0],
                        [2.0, 0.0],
                        [2.0, 0.0],
                        [2.0, 0.0],
                    ],
                    [
                        [9.0, 9.0],
                        [2.0, 0.0],
                        [7.0, np.nan],
                        [3.0, 0.0],
                        [2.0, 0.0],
                        [2.0, 0.0],
                    ],
                ],
                [
                    [
                        [9.0, 9.0],
                        [0.0, 3.0],
                        [4.0, 7.0],
                        [0.0, 3.0],
                        [0.0, 2.0],
                        [0.0, 2.0],
                    ],
                    [
                        [9.0, 9.0],
                        [0.0, 4.0],
                        [np.nan, np.nan],
                        [0.0, 3.0],
                        [0.0, 2.0],
                        [0.0, 2.0],
                    ],
                ],
            ]
        ),  # expected
    ),  # ordinary da, tests internal-spell, no-spell, double-spell, no-start-spell
    (
        {
            "data": da.arange(30).reshape(30, 1, 1).rechunk(chunks=(10, -1, -1)),
            "units": "degree_Celsius",
        },  # data
        {
            "data": 10,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # start threshold
        ">",  # start condition
        {
            "data": 11,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # end threshold
        ">",  # end condition
        {"data": 6, "units": "days"},  # start duration
        {"data": 6, "units": "days"},  # end duration
        {"data": 0, "units": "days"},  # start delay
        {"data": 0, "units": "days"},  # end delay
        np.ma.masked_array(
            [
                [
                    [
                        [30.0, 30.0],
                        [0.0, 0.0],
                        [12.0, 13.0],
                        [19.0, 18.0],
                        [0.0, 0.0],
                        [5.0, 5.0],
                    ]
                ]
            ]
        ),  # expected
    ),  # tests start in 2 chunk and end in 2 chunk
    (
        {
            "data": da.arange(30).reshape(30, 1, 1).rechunk(chunks=(10, -1, -1)),
            "units": "degree_Celsius",
        },  # data
        {
            "data": 0,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # start threshold
        ">",  # start condition
        {
            "data": 0,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # end threshold
        ">",  # end condition
        {"data": 6, "units": "days"},  # start duration
        {"data": 6, "units": "days"},  # end duration
        {"data": 0, "units": "days"},  # start delay
        {"data": 0, "units": "days"},  # end delay
        np.ma.masked_array(
            [
                [
                    [
                        [30.0, 30.0],
                        [0.0, 0.0],
                        [2.0, 3.0],
                        [29.0, 29.0],
                        [0.0, 0.0],
                        [5.0, 5.0],
                    ]
                ]
            ],
        ),  # expected
    ),  # tests start and end at the same time in the 1 chunk
    (
        {
            "data": da.arange(30).reshape(30, 1, 1).rechunk(chunks=(10, -1, -1)),
            "units": "degree_Celsius",
        },  # data
        {
            "data": 2,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # start threshold
        ">",  # start condition
        {
            "data": 8,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # end threshold
        ">",  # end condition
        {"data": 6, "units": "days"},  # start duration
        {"data": 6, "units": "days"},  # end duration
        {"data": 0, "units": "days"},  # start delay
        {"data": 0, "units": "days"},  # end delay
        np.ma.masked_array(
            [
                [
                    [
                        [30.0, 30.0],
                        [0.0, 0.0],
                        [4.0, 10.0],
                        [27.0, 21.0],
                        [0.0, 0.0],
                        [5.0, 5.0],
                    ]
                ]
            ]
        ),  # expected
    ),  # tests start in 1 chunk and end between 1-2 chunks
    (
        {
            "data": da.arange(30).reshape(30, 1, 1).rechunk(chunks=(10, -1, -1)),
            "units": "degree_Celsius",
        },  # data
        {
            "data": 5,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # start threshold
        ">",  # start condition
        {
            "data": 15,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # end threshold
        ">",  # end condition
        {"data": 6, "units": "days"},  # start duration
        {"data": 6, "units": "days"},  # end duration
        {"data": 0, "units": "days"},  # start delay
        {"data": 0, "units": "days"},  # end delay
        np.array(
            [
                [
                    [
                        [30.0, 30.0],
                        [0.0, 0.0],
                        [7.0, 17.0],
                        [24.0, 14.0],
                        [0.0, 0.0],
                        [5.0, 5.0],
                    ]
                ]
            ]
        ),  # expected
    ),  # start between chunks 1-2 and end between chunks 2-3
    (
        {
            "data": da.arange(30).reshape(30, 1, 1).rechunk(chunks=(10, -1, -1)),
            "units": "degree_Celsius",
        },  # data
        {
            "data": 17,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # start threshold
        ">",  # start condition
        {
            "data": 17,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # end threshold
        ">",  # end condition
        {"data": 6, "units": "days"},  # start duration
        {"data": 6, "units": "days"},  # end duration
        {"data": 0, "units": "days"},  # start delay
        {"data": 0, "units": "days"},  # end delay
        np.array(
            [
                [
                    [
                        [30.0, 30.0],
                        [0.0, 0.0],
                        [19.0, 20.0],
                        [12.0, 12.0],
                        [0.0, 0.0],
                        [5.0, 5.0],
                    ]
                ]
            ]
        ),  # expected
    ),  # start and end at the same time between the same chunks
    (
        {
            "data": da.arange(40).reshape(40, 1, 1).rechunk(chunks=(10, -1, -1)),
            "units": "degree_Celsius",
        },  # data
        {
            "data": 17,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # start threshold
        ">",  # start condition
        {
            "data": 14,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # end threshold
        ">",  # end condition
        {"data": 6, "units": "days"},  # start duration
        {"data": 6, "units": "days"},  # end duration
        {"data": 0, "units": "days"},  # start delay
        {"data": 0, "units": "days"},  # end delay
        np.array(
            [
                [
                    [
                        [40.0, 40.0],
                        [0.0, 0.0],
                        [19.0, 20.0],
                        [22.0, 25.0],
                        [0.0, 0.0],
                        [5.0, 5.0],
                    ]
                ]
            ]
        ),  # expected
    ),  # end before start between the same chunks
    (
        {
            "data": da.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 3, 5, 6, 7, 8, 9, 10])
            .reshape(17, 1, 1)
            .rechunk(chunks=(5, -1, -1)),
            "units": "degree_Celsius",
        },  # data
        {
            "data": 4,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # start threshold
        ">",  # start condition
        {
            "data": 4,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # end threshold
        ">",  # end condition
        {"data": 6, "units": "days"},  # start duration
        {"data": 6, "units": "days"},  # end duration
        {"data": 0, "units": "days"},  # start delay
        {"data": 0, "units": "days"},  # end delay
        np.array(
            [
                [
                    [
                        [17.0, 17.0],
                        [0.0, 0.0],
                        [5.0, 12.0],
                        [6.0, 6.0],
                        [0.0, 0.0],
                        [5.0, 5.0],
                    ]
                ]
            ]
        ),  # expected
    ),  # tests end and start between chunks 1-2 at the same time,
    # final end at the end of the spell between chunks 3-4.
    (
        {
            "data": da.array(
                [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 3, 5, 6, 7, 4, 9, 10, 11, 12, 13, 14]
            )
            .reshape(21, 1, 1)
            .rechunk(chunks=(7, -1, -1)),
            "units": "degree_Celsius",
        },  # data
        {
            "data": 4,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # start threshold
        ">",  # start condition
        {
            "data": 4,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # end threshold
        ">",  # end condition
        {"data": 6, "units": "days"},  # start duration
        {"data": 6, "units": "days"},  # end duration
        {"data": 0, "units": "days"},  # start delay
        {"data": 0, "units": "days"},  # end delay
        np.array(
            [
                [
                    [
                        [21.0, 21.0],
                        [0.0, 0.0],
                        [5.0, 16.0],
                        [6.0, 6.0],
                        [0.0, 0.0],
                        [5.0, 5.0],
                    ]
                ]
            ]
        ),  # expected
    ),  # tests end and start between chunks 1-2 at the same time,
    # final end at the end of the spell in last chunk
    (
        {
            "data": da.array(
                [
                    -1,
                    0,
                    1,
                    2,
                    3,
                    4,
                    5,
                    6,
                    7,
                    6,
                    5,
                    4,
                    3,
                    2,
                    1,
                    0,
                    4,
                    9,
                    10,
                    11,
                    12,
                    13,
                    14,
                    13,
                    11,
                    9,
                    6,
                    4,
                    4,
                    4,
                    3,
                    2,
                    1,
                ]
            )
            .reshape(33, 1, 1)
            .rechunk(chunks=(10, -1, -1)),
            "units": "degree_Celsius",
        },  # data
        {
            "data": 5,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # start threshold
        ">",  # start condition
        {
            "data": 5,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # end threshold
        "<",  # end condition
        {"data": 6, "units": "days"},  # start duration
        {"data": 6, "units": "days"},  # end duration
        {"data": 0, "units": "days"},  # start delay
        {"data": 0, "units": "days"},  # end delay
        np.array(
            [
                [
                    [
                        [33.0, 33.0],
                        [0.0, 6.0],
                        [18.0, 28.0],
                        [0.0, 6.0],
                        [0.0, 5.0],
                        [0.0, 5.0],
                    ]
                ]
            ]
        ),  # expected
    ),  # end and start between chunks 2-3 at the same time,
    # final end at the end of the spell between chunks 3-4
    (
        {
            "data": da.arange(40).reshape(40, 1, 1).rechunk(chunks=(10, -1, -1)),
            "units": "degree_Celsius",
        },  # data
        {
            "data": 10,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # start threshold
        ">",  # start condition
        {
            "data": 32,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # end threshold
        ">",  # end condition
        {"data": 6, "units": "days"},  # start duration
        {"data": 6, "units": "days"},  # end duration
        {"data": 0, "units": "days"},  # start delay
        {"data": 0, "units": "days"},  # end delay
        np.array(
            [
                [
                    [
                        [40.0, 40.0],
                        [0.0, 0.0],
                        [12.0, 34.0],
                        [29.0, 7.0],
                        [0.0, 0.0],
                        [5.0, 5.0],
                    ]
                ]
            ]
        ),  # expected
    ),  # start in second chunk and end in last
    (
        {
            "data": da.arange(40).reshape(40, 1, 1).rechunk(chunks=(10, -1, -1)),
            "units": "degree_Celsius",
        },  # data
        {
            "data": 100,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # start threshold
        ">",  # start condition
        {
            "data": 12,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # end threshold
        ">",  # end condition
        {"data": 6, "units": "days"},  # start duration
        {"data": 6, "units": "days"},  # end duration
        {"data": 0, "units": "days"},  # start delay
        {"data": 0, "units": "days"},  # end delay
        np.array(
            [
                [
                    [
                        [40.0, 40.0],
                        [0.0, 0.0],
                        [np.nan, np.nan],
                        [0.0, 27.0],
                        [0.0, 0.0],
                        [0.0, 5.0],
                    ]
                ]
            ]
        ),  # expected
    ),  # tests no start
    (
        {
            "data": da.arange(40).reshape(40, 1, 1).rechunk(chunks=(10, -1, -1)),
            "units": "degree_Celsius",
        },  # data
        {
            "data": 10,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # start threshold
        ">",  # start condition
        {
            "data": 100,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # end threshold
        ">",  # end condition
        {"data": 6, "units": "days"},  # start duration
        {"data": 6, "units": "days"},  # end duration
        {"data": 0, "units": "days"},  # start delay
        {"data": 0, "units": "days"},  # end delay
        np.array(
            [
                [
                    [
                        [40.0, 40.0],
                        [0.0, 0.0],
                        [12.0, np.nan],
                        [29.0, 0.0],
                        [0.0, 0.0],
                        [5.0, 0.0],
                    ]
                ]
            ]
        ),  # expected
    ),  # tests no end
    (
        {
            "data": da.arange(0, 400, 1).reshape(100, 2, 2).rechunk(chunks=(10, 1, 1)),
            "units": "degree_Celsius",
        },  # data
        {
            "data": 30,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # start threshold
        ">",  # start condition
        {
            "data": 300,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # end threshold
        ">",  # end condition
        {"data": 2, "units": "days"},  # start duration
        {"data": 2, "units": "days"},  # end duration
        {"data": 0, "units": "days"},  # start delay
        {"data": 0, "units": "days"},  # end delay
        np.array(
            [
                [
                    [
                        [100.0, 100.0],
                        [0.0, 0.0],
                        [9.0, 77.0],
                        [92.0, 24.0],
                        [0.0, 0.0],
                        [1.0, 1.0],
                    ],
                    [
                        [100.0, 100.0],
                        [0.0, 0.0],
                        [9.0, 76.0],
                        [92.0, 25.0],
                        [0.0, 0.0],
                        [1.0, 1.0],
                    ],
                ],
                [
                    [
                        [100.0, 100.0],
                        [0.0, 0.0],
                        [9.0, 76.0],
                        [92.0, 25.0],
                        [0.0, 0.0],
                        [1.0, 1.0],
                    ],
                    [
                        [100.0, 100.0],
                        [0.0, 0.0],
                        [8.0, 76.0],
                        [93.0, 25.0],
                        [0.0, 0.0],
                        [1.0, 1.0],
                    ],
                ],
            ]
        ),  # expected
    ),  # tests multiple grid-cells and chunks
    (
        {
            "data": da.array(
                [
                    [[6, 1], [1, 1]],
                    [[7, 1], [1, 6]],
                    [[8, 6], [1, 7]],
                    [[1, 7], [6, 8]],
                    [[1, 8], [7, 5]],
                    [[1, 1], [8, 5]],
                    [[1, 1], [9, 5]],
                    [[1, 1], [1, 1]],
                    [[1, 1], [1, 1]],
                    [[1, 1], [1, 1]],
                ]
            ).rechunk(chunks=(3, 2, 2)),
            "units": "degree_Celsius",
        },  # data
        {
            "data": 5,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # start threshold
        ">",  # start condition
        {
            "data": 5,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # end threshold
        "<",  # end condition
        {"data": 3, "units": "days"},  # start duration
        {"data": 3, "units": "days"},  # end duration
        {"data": 0, "units": "days"},  # start delay
        {"data": 0, "units": "days"},  # end delay
        np.array(
            [
                [
                    [
                        [10.0, 10.0],
                        [3.0, 0.0],
                        [1.0, 4.0],
                        [0.0, 7.0],
                        [2.0, 0.0],
                        [0.0, 2.0],
                    ],
                    [
                        [10.0, 10.0],
                        [0.0, 2.0],
                        [3.0, 6.0],
                        [0.0, 5.0],
                        [0.0, 2.0],
                        [0.0, 2.0],
                    ],
                ],
                [
                    [
                        [10.0, 10.0],
                        [0.0, 3.0],
                        [4.0, 8.0],
                        [0.0, 3.0],
                        [0.0, 2.0],
                        [0.0, 2.0],
                    ],
                    [
                        [10.0, 10.0],
                        [0.0, 1.0],
                        [2.0, 8.0],
                        [0.0, 3.0],
                        [0.0, 1.0],
                        [0.0, 2.0],
                    ],
                ],
            ]
        ),  # expected
    ),  # tests multiple grid-cells and chunks
    (
        {
            "data": da.ma.masked_array(
                data=[
                    [[6, 1], [1, 5]],
                    [[7, 1], [1, 5]],
                    [[8, 1], [1, 5]],
                    [[5, 1], [1, 5]],
                    [[5, 1], [1, 5]],
                    [[5, 1], [1, 5]],
                    [[5, 1], [6, 5]],
                    [[5, 1], [6, 5]],
                    [[5, 1], [6, 5]],
                    [[5, 1], [1, 5]],
                ],
                mask=[
                    [[1, 0], [0, 0]],
                    [[0, 0], [0, 0]],
                    [[0, 0], [0, 0]],
                    [[0, 0], [0, 0]],
                    [[0, 0], [0, 0]],
                    [[0, 0], [0, 0]],
                    [[0, 0], [0, 1]],
                    [[0, 0], [0, 0]],
                    [[0, 0], [0, 0]],
                    [[0, 0], [0, 0]],
                ],
            ).rechunk(chunks=(3, 2, 2)),
            "units": "degree_Celsius",
        },  # data
        {
            "data": 5,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # start threshold
        ">",  # start condition
        {
            "data": 5,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # end threshold
        "<",  # end condition
        {"data": 3, "units": "days"},  # start duration
        {"data": 3, "units": "days"},  # end duration
        {"data": 0, "units": "days"},  # start delay
        {"data": 0, "units": "days"},  # end delay
        np.ma.masked_array(
            data=[
                [
                    [
                        [10.0, 10.0],
                        [0.0, 0.0],
                        [np.nan, np.nan],
                        [0.0, 0.0],
                        [0.0, 0.0],
                        [0.0, 0.0],
                    ],
                    [
                        [10.0, 10.0],
                        [0.0, 10.0],
                        [np.nan, np.nan],
                        [0.0, 10.0],
                        [0.0, 2.0],
                        [0.0, 2.0],
                    ],
                ],
                [
                    [
                        [10.0, 10.0],
                        [0.0, 6.0],
                        [7.0, np.nan],
                        [0.0, 1.0],
                        [0.0, 2.0],
                        [0.0, 1.0],
                    ],
                    [
                        [10.0, 10.0],
                        [0.0, 0.0],
                        [np.nan, np.nan],
                        [0.0, 0.0],
                        [0.0, 0.0],
                        [0.0, 0.0],
                    ],
                ],
            ],
            mask=[
                [
                    [[1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1]],
                    [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]],
                ],
                [
                    [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]],
                    [[1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1]],
                ],
            ],
        ),  # expected
    ),  # tests multiple grid-cells and chunks with masked array
    (
        {
            "data": da.arange(732).reshape(183, 2, 2).rechunk(chunks=(25, 1, 2)),
            "units": "degree_Celsius",
        },  # data
        {
            "data": 15,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # start threshold
        ">",  # start condition
        {
            "data": 20,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # end threshold
        ">",  # end condition
        {"data": 6, "units": "days"},  # start duration
        {"data": 6, "units": "days"},  # end duration
        {"data": 20, "units": "days"},  # start delay
        {"data": 75, "units": "days"},  # end delay
        np.array(
            [
                [
                    [
                        [183.0, 183.0],
                        [0.0, 0.0],
                        [21.0, 76.0],
                        [163.0, 108.0],
                        [0.0, 0.0],
                        [5.0, 5.0],
                    ],
                    [
                        [183.0, 183.0],
                        [0.0, 0.0],
                        [21.0, 76.0],
                        [163.0, 108.0],
                        [0.0, 0.0],
                        [5.0, 5.0],
                    ],
                ],
                [
                    [
                        [183.0, 183.0],
                        [0.0, 0.0],
                        [21.0, 76.0],
                        [163.0, 108.0],
                        [0.0, 0.0],
                        [5.0, 5.0],
                    ],
                    [
                        [183.0, 183.0],
                        [0.0, 0.0],
                        [21.0, 76.0],
                        [163.0, 108.0],
                        [0.0, 0.0],
                        [5.0, 5.0],
                    ],
                ],
            ]
        ),  # expected
    ),  # tests multiple grid-cells and chunks with different chunking on grid cells
    # and different delays for both start and end
    (
        {
            "data": da.arange(20).reshape(5, 2, 2).rechunk(chunks=(2, 1, 1)),
            "units": "degree_Celsius",
        },  # data
        {
            "data": 10,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # start threshold
        ">",  # start condition
        {
            "data": 20,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # end threshold
        ">",  # end condition
        {"data": 3, "units": "days"},  # start duration
        {"data": 3, "units": "days"},  # end duration
        {"data": 0, "units": "days"},  # start delay
        {"data": 0, "units": "days"},  # end delay
        np.array(
            [
                [
                    [
                        [5.0, 5.0],
                        [0.0, 0.0],
                        [np.nan, np.nan],
                        [2.0, 0.0],
                        [0.0, 0.0],
                        [2.0, 0.0],
                    ],
                    [
                        [5.0, 5.0],
                        [0.0, 0.0],
                        [np.nan, np.nan],
                        [2.0, 0.0],
                        [0.0, 0.0],
                        [2.0, 0.0],
                    ],
                ],
                [
                    [
                        [5.0, 5.0],
                        [0.0, 0.0],
                        [np.nan, np.nan],
                        [2.0, 0.0],
                        [0.0, 0.0],
                        [2.0, 0.0],
                    ],
                    [
                        [5.0, 5.0],
                        [0.0, 0.0],
                        [3.0, np.nan],
                        [3.0, 0.0],
                        [0.0, 0.0],
                        [2.0, 0.0],
                    ],
                ],
            ]
        ),  # expected
    ),  # tests multiple grid-cells and chunks, start exists but no end
    (
        {
            "data": da.ma.masked_array(
                data=[
                    [[4, 1], [9, 5]],
                    [[4, 1], [9, 5]],
                    [[4, 1], [9, 5]],
                    [[4, 1], [9, 5]],
                    [[9, 1], [9, 5]],
                    [[9, 1], [9, 5]],
                    [[9, 1], [9, 5]],
                    [[9, 1], [9, 5]],
                    [[9, 1], [9, 5]],
                    [[9, 1], [9, 5]],
                ],
                mask=[
                    [[0, 0], [0, 0]],
                    [[0, 0], [0, 0]],
                    [[0, 0], [0, 0]],
                    [[0, 0], [0, 0]],
                    [[0, 0], [1, 0]],
                    [[0, 0], [0, 1]],
                    [[0, 0], [0, 1]],
                    [[0, 0], [0, 0]],
                    [[0, 0], [0, 1]],
                    [[0, 0], [0, 0]],
                ],
            ).rechunk(chunks=(3, 2, 2)),
            "units": "degree_Celsius",
        },  # data
        {
            "data": 3,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # start threshold
        ">",  # start condition
        {
            "data": 2,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # end threshold
        ">",  # end condition
        {"data": 3, "units": "days"},  # start duration
        {"data": 3, "units": "days"},  # end duration
        {"data": 4, "units": "days"},  # start delay
        {"data": 3, "units": "days"},  # end delay
        np.ma.masked_array(
            data=[
                [
                    [
                        [10.0, 10.0],
                        [0.0, 0.0],
                        [5.0, 6.0],
                        [6.0, 7.0],
                        [2.0, 2.0],
                        [2.0, 2.0],
                    ],
                    [
                        [10.0, 10.0],
                        [0.0, 0.0],
                        [np.nan, np.nan],
                        [0.0, 0.0],
                        [0.0, 0.0],
                        [0.0, 0.0],
                    ],
                ],
                [
                    [
                        [10.0, 10.0],
                        [0.0, 0.0],
                        [6.0, 7.0],
                        [5.0, 5.0],
                        [2.0, 2.0],
                        [2.0, 2.0],
                    ],
                    [
                        [10.0, 10.0],
                        [0.0, 0.0],
                        [np.nan, np.nan],
                        [1.0, 1.0],
                        [2.0, 2.0],
                        [1.0, 1.0],
                    ],
                ],
            ],
            mask=[
                [
                    [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]],
                    [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]],
                ],
                [
                    [[1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1]],
                    [[1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1]],
                ],
            ],
        ),  # expected
    ),  # tests multiple grid-cells and chunks delays, masked
    (
        {
            "data": da.ma.masked_array(
                data=[
                    [[4, 1], [9, 4]],
                    [[4, 1], [9, 4]],
                    [[4, 1], [9, 4]],
                    [[4, 1], [9, 4]],
                    [[9, 1], [9, 9]],
                    [[9, 1], [1, 9]],
                    [[9, 9], [1, 9]],
                    [[4, 9], [1, 9]],
                    [[4, 9], [9, 9]],
                    [[4, 1], [9, 9]],
                    [[4, 1], [9, 9]],
                    [[4, 1], [9, 9]],
                ],
            ).rechunk(chunks=(6, 2, 2)),
            "units": "degree_Celsius",
        },  # data
        {
            "data": 5,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # start threshold
        ">",  # start condition
        {
            "data": 5,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # end threshold
        "<",  # end condition
        {"data": 3, "units": "days"},  # start duration
        {"data": 3, "units": "days"},  # end duration
        {"data": 2, "units": "days"},  # start delay
        {"data": 0, "units": "days"},  # end delay
        np.ma.masked_array(
            data=[
                [
                    [
                        [12.0, 12.0],
                        [0.0, 4.0],
                        [5.0, 8.0],
                        [0.0, 5.0],
                        [0.0, 2.0],
                        [0.0, 2.0],
                    ],
                    [
                        [12.0, 12.0],
                        [0.0, 6.0],
                        [7, 10],
                        [0.0, 3.0],
                        [0.0, 2.0],
                        [0.0, 2.0],
                    ],
                ],
                [
                    [
                        [12.0, 12.0],
                        [0.0, 0.0],
                        [3.0, 6],
                        [4.0, 0.0],
                        [2.0, 0.0],
                        [2.0, 0.0],
                    ],
                    [
                        [12.0, 12.0],
                        [0.0, 4.0],
                        [5, np.nan],
                        [8.0, 0.0],
                        [0.0, 2.0],
                        [2.0, 0.0],
                    ],
                ],
            ],
        ),  # expected
    ),  # tests multiple grid-cells and find_overlap
    (
        {
            "data": da.ma.masked_array(
                data=[
                    [[4, 6], [9, 9]],
                    [[4, 6], [9, 9]],
                    [[4, 6], [9, 9]],
                    [[4, 6], [9, 9]],
                    [[4, 6], [9, 9]],
                    [[4, 6], [1, 9]],
                    [[6, 6], [1, 9]],
                    [[6, 6], [9, 9]],
                    [[6, 4], [9, 9]],
                    [[6, 4], [9, 9]],
                    [[6, 4], [1, 1]],
                    [[6, 6], [1, 1]],
                    [[6, 6], [9, 1]],
                    [[6, 6], [9, 1]],
                    [[6, 6], [9, 1]],
                ],
            ).rechunk(chunks=(6, 2, 2)),
            "units": "degree_Celsius",
        },  # data
        {
            "data": 5,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # start threshold
        ">",  # start condition
        {
            "data": 5,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # end threshold
        ">",  # end condition
        {"data": 3, "units": "days"},  # start duration
        {"data": 3, "units": "days"},  # end duration
        {"data": 8, "units": "days"},  # start delay
        {"data": 0, "units": "days"},  # end delay
        np.ma.masked_array(
            data=[
                [
                    [
                        [15.0, 15.0],
                        [0.0, 0.0],
                        [9.0, 10.0],
                        [7.0, 9.0],
                        [0.0, 0.0],
                        [2.0, 2.0],
                    ],
                    [
                        [15.0, 15.0],
                        [0.0, 8.0],
                        [12, 13],
                        [4.0, 4.0],
                        [2.0, 2.0],
                        [2.0, 2.0],
                    ],
                ],
                [
                    [
                        [15.0, 15.0],
                        [0.0, 5.0],
                        [13.0, np.nan],
                        [3.0, 3.0],
                        [2.0, 2.0],
                        [2.0, 2.0],
                    ],
                    [
                        [15.0, 15.0],
                        [0.0, 10.0],
                        [np.nan, np.nan],
                        [0.0, 0.0],
                        [2.0, 2.0],
                        [0.0, 0.0],
                    ],
                ],
            ],
        ),  # expected
    ),  # tests multiple grid-cells and find_overlap
]
TEST_SEASON_END_POST_PROCESS_PARAMETERS = [
    (
        {
            "data": np.ma.masked_array(
                data=[
                    [
                        [
                            [16.0, 16.0],
                            [1.0, 1.0],
                            [3.0, 7.0],
                            [14.0, 10.0],
                            [1.0, 1.0],
                            [3.0, 3.0],
                        ],
                        [
                            [16.0, 16.0],
                            [1.0, 1.0],
                            [3.0, 6.0],
                            [14.0, 11.0],
                            [1.0, 1.0],
                            [3.0, 3.0],
                        ],
                    ],
                    [
                        [
                            [16.0, 16.0],
                            [1.0, 1.0],
                            [2.0, 6.0],
                            [15.0, 11.0],
                            [1.0, 1.0],
                            [3.0, 3.0],
                        ],
                        [
                            [16.0, 16.0],
                            [1.0, 1.0],
                            [2.0, 6.0],
                            [15.0, 11.0],
                            [1.0, 1.0],
                            [3.0, 3.0],
                        ],
                    ],
                ],
            ),
            "units": "degree_Celsius",
        },  # data
        {
            "data": 5,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # start threshold
        ">",  # start condition
        {
            "data": 10,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # end threshold
        ">",  # end condition
        {"data": 3, "units": "days"},  # start duration
        {"data": 3, "units": "days"},  # end duration
        {"data": 0, "units": "days"},  # start delay
        {"data": 0, "units": "days"},  # end delay
        np.array([[[7, 6], [6, 6]]]),  # expected
    ),  # postprocessing start before end, no merging
    (
        {
            "data": np.ma.masked_array(
                data=[
                    [
                        [
                            [
                                [16.0, 16.0],
                                [1.0, 1.0],
                                [np.nan, np.nan],
                                [2.0, 2.0],
                                [1.0, 1.0],
                                [2.0, 2.0],
                            ],
                            [
                                [16.0, 16.0],
                                [1.0, 1.0],
                                [np.nan, np.nan],
                                [2.0, 2.0],
                                [1.0, 1.0],
                                [1.0, 1.0],
                            ],
                        ]
                    ],
                    [
                        [
                            [
                                [16.0, 16.0],
                                [2.0, 2.0],
                                [4.0, np.nan],
                                [11.0, 1.0],
                                [2.0, 2.0],
                                [3.0, 1.0],
                            ],
                            [
                                [16.0, 16.0],
                                [2.0, 2.0],
                                [np.nan, np.nan],
                                [2.0, 2.0],
                                [2.0, 2.0],
                                [2.0, 2.0],
                            ],
                        ]
                    ],
                ],
            ),
            "units": "degree_Celsius",
        },  # data
        {
            "data": 5,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # start threshold
        ">",  # start condition
        {
            "data": 10,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # end threshold
        ">",  # end condition
        {"data": 3, "units": "days"},  # start duration
        {"data": 3, "units": "days"},  # end duration
        {"data": 0, "units": "days"},  # start delay
        {"data": 0, "units": "days"},  # end delay
        np.array([[[16, np.nan]], [[16, np.nan]]]),
    ),  # postprocessing merging, end at boundary, no start, end at the last day, no end
    (
        {
            "data": np.ma.masked_array(
                data=[
                    [
                        [
                            [
                                [365.0, 365.0],
                                [365.0, 0.0],
                                [1.0, np.nan],
                                [365.0, 0.0],
                                [5.0, 0.0],
                                [5.0, 0.0],
                            ],
                            [
                                [365.0, 365.0],
                                [0.0, 365.0],
                                [np.nan, np.nan],
                                [0.0, 365.0],
                                [0.0, 5.0],
                                [0.0, 5.0],
                            ],
                        ]
                    ],
                    [
                        [
                            [
                                [366.0, 366.0],
                                [366.0, 0.0],
                                [1.0, np.nan],
                                [366.0, 0.0],
                                [5.0, 0.0],
                                [5.0, 0.0],
                            ],
                            [
                                [366.0, 366.0],
                                [0.0, 366.0],
                                [np.nan, np.nan],
                                [0.0, 366.0],
                                [0.0, 5.0],
                                [0.0, 5.0],
                            ],
                        ]
                    ],
                ],
            ),
            "units": "degree_Celsius",
        },  # data
        {
            "data": 50,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # start threshold
        ">",  # start condition
        {
            "data": 50,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # end threshold
        "<",  # end condition
        {"data": 6, "units": "days"},  # start duration
        {"data": 6, "units": "days"},  # end duration
        {"data": 0, "units": "days"},  # start delay
        {"data": 0, "units": "days"},  # end delay
        np.array([[[365, np.nan]], [[366, np.nan]]]),
    ),  # postprocessing merging, start spell covers all year, end spell covers all year
    (
        {
            "data": np.ma.masked_array(
                data=[
                    [
                        [
                            [
                                [15.0, 15.0],
                                [2.0, 0.0],
                                [np.nan, np.nan],
                                [2.0, 2.0],
                                [2.0, 0.0],
                                [3.0, 2.0],
                            ],
                            [
                                [15.0, 15.0],
                                [15.0, 0.0],
                                [1.0, np.nan],
                                [15.0, 2.0],
                                [5.0, 0.0],
                                [5.0, 2.0],
                            ],
                        ]
                    ],
                    [
                        [
                            [
                                [15.0, 15.0],
                                [15.0, 3.0],
                                [1.0, 8.0],
                                [15.0, 7.0],
                                [5.0, 3.0],
                                [5.0, 5.0],
                            ],
                            [
                                [15.0, 15.0],
                                [15.0, 15.0],
                                [1.0, 1.0],
                                [15.0, 15.0],
                                [5.0, 5.0],
                                [5.0, 5.0],
                            ],
                        ]
                    ],
                ],
            ),
            "units": "degree_Celsius",
        },  # data
        {
            "data": 50,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # start threshold
        ">",  # start condition
        {
            "data": 50,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # end threshold
        "<",  # end condition
        {"data": 6, "units": "days"},  # start duration
        {"data": 6, "units": "days"},  # end duration
        {"data": 0, "units": "days"},  # start delay
        {"data": 0, "units": "days"},  # end delay
        np.array([[[15, 14]], [[8, 1]]]),
    ),  # postprocessing merging, start before end between years,
    # start exists end between years
]

parameter_names = (
    "f_cube_tas, f_first_threshold, first_condition, f_second_threshold, "
    + "second_condition, f_first_duration, f_second_duration, f_first_delay, "
    + "f_second_delay, expected"
)
fixtures = [
    "f_cube_tas",
    "f_first_threshold",
    "f_second_threshold",
    "f_first_duration",
    "f_second_duration",
    "f_first_delay",
    "f_second_delay",
]


@pytest.mark.parametrize(
    parameter_names, TEST_SEASON_END_CALL_PARAMETERS, indirect=fixtures
)
def test_season_end_lazy_func(
    f_cube_tas,
    f_first_threshold,
    first_condition,
    f_second_threshold,
    second_condition,
    f_first_duration,
    f_second_duration,
    f_first_delay,
    f_second_delay,
    expected,
    f_dask_cluster,
):
    parameters = {
        "start_threshold": f_first_threshold,
        "end_threshold": f_second_threshold,
        "start_condition": first_condition,
        "end_condition": second_condition,
        "start_duration": f_first_duration,
        "end_duration": f_second_duration,
        "start_delay": f_first_delay,
        "end_delay": f_second_delay,
    }
    index_function = spl_func.SeasonEnd(**parameters)
    with Client(f_dask_cluster) as client:
        lazy_func_test(index_function, f_cube_tas, expected, client)
    assert index_function.units == Unit("days")


@pytest.mark.parametrize(
    parameter_names, TEST_SEASON_END_POST_PROCESS_PARAMETERS, indirect=fixtures
)
def test_season_end_post_process(
    f_cube_tas,
    f_first_threshold,
    first_condition,
    f_second_threshold,
    second_condition,
    f_first_duration,
    f_second_duration,
    f_first_delay,
    f_second_delay,
    expected,
):
    parameters = {
        "start_threshold": f_first_threshold,
        "start_condition": first_condition,
        "end_threshold": f_second_threshold,
        "end_condition": second_condition,
        "start_duration": f_first_duration,
        "end_duration": f_second_duration,
        "start_delay": f_first_delay,
        "end_delay": f_second_delay,
    }
    index_function = spl_func.SeasonEnd(**parameters)
    data = f_cube_tas.data
    if data.ndim < 5:
        shape = data.shape
        data = data.reshape((1,) + shape)
    aggregateby_cube = f_cube_tas
    cube, res = index_function.post_process(aggregateby_cube, data, None, None)
    assert np.array_equal(res, expected, equal_nan=True)
    expected_mask = np.ma.getmaskarray(expected)
    res_mask = np.ma.getmaskarray(res)
    assert (res_mask == expected_mask).all()


TEST_SEASON_LENGTH_CALL_PARAMETERS = [
    (
        {
            "data": np.arange(60).reshape(15, 2, 2),
            "units": "degree_Celsius",
        },  # data
        {
            "data": 5,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # start threshold
        ">",  # start condition
        {
            "data": 20,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # end threshold
        ">",  # end condition
        {"data": 3, "units": "days"},  # start duration
        {"data": 3, "units": "days"},  # end duration
        {"data": 0, "units": "days"},  # start delay
        {"data": 0, "units": "days"},  # end delay
        np.array(
            [
                [
                    [
                        [15.0, 15.0],
                        [0.0, 0.0],
                        [3.0, 7.0],
                        [13.0, 9.0],
                        [0.0, 0.0],
                        [2.0, 2.0],
                    ],
                    [
                        [15.0, 15.0],
                        [0.0, 0.0],
                        [3.0, 6.0],
                        [13.0, 10.0],
                        [0.0, 0.0],
                        [2.0, 2.0],
                    ],
                ],
                [
                    [
                        [15.0, 15.0],
                        [0.0, 0.0],
                        [2.0, 6.0],
                        [14.0, 10.0],
                        [0.0, 0.0],
                        [2.0, 2.0],
                    ],
                    [
                        [15.0, 15.0],
                        [0.0, 0.0],
                        [2.0, 6.0],
                        [14.0, 10.0],
                        [0.0, 0.0],
                        [2.0, 2.0],
                    ],
                ],
            ],
        ),  # expected
    ),  # ordinary np (end spell)
    (
        {
            "data": np.ma.masked_array(
                [
                    [[6, 7], [4, 0]],
                    [[6, 7], [3, 3]],
                    [[6, 7], [2, 4]],
                    [[2, 7], [4, 7]],
                    [[3, 7], [3, 8]],
                    [[4, 7], [2, 6]],
                ],
                mask=[
                    [[0, 0], [0, 0]],
                    [[0, 0], [0, 0]],
                    [[1, 0], [0, 0]],
                    [[0, 0], [0, 0]],
                    [[0, 0], [0, 0]],
                    [[0, 0], [0, 0]],
                ],
            ),
            "units": "degree_Celsius",
        },  # data
        {
            "data": 5,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # start threshold
        ">",  # start condition
        {
            "data": 5,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # end threshold
        "<",  # end condition
        {"data": 3, "units": "days"},  # start duration
        {"data": 3, "units": "days"},  # end duration
        {"data": 0, "units": "days"},  # start delay
        {"data": 0, "units": "days"},  # end delay
        np.ma.masked_array(
            data=[
                [
                    [
                        [6.0, 6.0],
                        [2.0, 0.0],
                        [np.nan, np.nan],
                        [0.0, 3.0],
                        [2.0, 0.0],
                        [0.0, 2.0],
                    ],
                    [
                        [6.0, 6.0],
                        [6.0, 0.0],
                        [1.0, np.nan],
                        [6.0, 0.0],
                        [2.0, 0.0],
                        [2.0, 0.0],
                    ],
                ],
                [
                    [
                        [6.0, 6.0],
                        [0.0, 6.0],
                        [np.nan, np.nan],
                        [0.0, 6.0],
                        [0.0, 2.0],
                        [0.0, 2.0],
                    ],
                    [
                        [6.0, 6.0],
                        [0.0, 3.0],
                        [4.0, np.nan],
                        [3.0, 0.0],
                        [0.0, 2.0],
                        [2.0, 0.0],
                    ],
                ],
            ],
            mask=[
                [
                    [[1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1]],
                    [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]],
                ],
                [
                    [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]],
                    [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]],
                ],
            ],
        ),  # expected
    ),  # masked np (masked end-spell, full-spell, non-spell, internal-spell)
    (
        {
            "data": da.array(
                [
                    [[6, 7], [4, 0]],
                    [[6, 7], [4, 7]],
                    [[10, 5], [4, 7]],
                    [[5, 7], [6, 7]],
                    [[4, 7], [6, 7]],
                    [[4, 5], [6, 7]],
                    [[4, 7], [2, 4]],
                    [[7, 7], [2, 4]],
                    [[7, 7], [2, 4]],
                ],
            ),
            "units": "degree_Celsius",
        },  # data
        {
            "data": 5,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # start threshold
        ">",  # start condition
        {
            "data": 5,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # end threshold
        "<",  # end condition
        {"data": 3, "units": "days"},  # start duration
        {"data": 3, "units": "days"},  # end duration
        {"data": 0, "units": "days"},  # start delay
        {"data": 0, "units": "days"},  # end delay
        np.array(
            [
                [
                    [
                        [9.0, 9.0],
                        [3.0, 0.0],
                        [1.0, 5.0],
                        [2.0, 0.0],
                        [2.0, 0.0],
                        [2.0, 0.0],
                    ],
                    [
                        [9.0, 9.0],
                        [2.0, 0.0],
                        [7.0, np.nan],
                        [3.0, 0.0],
                        [2.0, 0.0],
                        [2.0, 0.0],
                    ],
                ],
                [
                    [
                        [9.0, 9.0],
                        [0.0, 3.0],
                        [4.0, 7.0],
                        [0.0, 3.0],
                        [0.0, 2.0],
                        [0.0, 2.0],
                    ],
                    [
                        [9.0, 9.0],
                        [0.0, 1.0],
                        [2.0, 7.0],
                        [0.0, 3.0],
                        [0.0, 1.0],
                        [0.0, 2.0],
                    ],
                ],
            ]
        ),  # expected
    ),  # ordinary da (double-spell, end-spell, internal-spell, long-internal-spell)
    (
        {
            "data": da.array(
                [
                    [[6, 7], [4, 0]],
                    [[6, 7], [4, 7]],
                    [[10, 4], [4, 7]],
                    [[5, 4], [6, 7]],
                    [[4, 7], [6, 7]],
                    [[4, 5], [6, 4]],
                    [[7, 7], [6, 7]],
                    [[7, 7], [2, 4]],
                    [[7, 7], [2, 4]],
                ],
            ),
            "units": "degree_Celsius",
        },  # data
        {
            "data": 5,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # start threshold
        ">",  # start condition
        {
            "data": 5,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # end threshold
        "<",  # end condition
        {"data": 3, "units": "days"},  # start duration
        {"data": 2, "units": "days"},  # end duration
        {"data": 0, "units": "days"},  # start delay
        {"data": 0, "units": "days"},  # end delay
        np.array(
            [
                [
                    [
                        [9.0, 9.0],
                        [3.0, 0.0],
                        [1.0, 5.0],
                        [3.0, 0.0],
                        [2.0, 0.0],
                        [2.0, 0.0],
                    ],
                    [
                        [9.0, 9.0],
                        [2.0, 0.0],
                        [7.0, np.nan],
                        [3.0, 0.0],
                        [2.0, 0.0],
                        [2.0, 0.0],
                    ],
                ],
                [
                    [
                        [9.0, 9.0],
                        [0.0, 3.0],
                        [4.0, 8.0],
                        [0.0, 2.0],
                        [0.0, 1.0],
                        [0.0, 1.0],
                    ],
                    [
                        [9.0, 9.0],
                        [0.0, 1.0],
                        [2.0, 8.0],
                        [0.0, 2.0],
                        [0.0, 1.0],
                        [0.0, 1.0],
                    ],
                ],
            ]
        ),  # expected
    ),  # tests different start and end spell durations
]
TEST_SEASON_LENGTH_POST_PROCESS_PARAMETERS: Any = [
    (
        {
            "data": np.ma.masked_array(
                data=[
                    [
                        [
                            [6.0, 6.0],
                            [2.0, 0.0],
                            [np.nan, np.nan],
                            [0.0, 3.0],
                            [2.0, 0.0],
                            [0.0, 2.0],
                        ],
                        [
                            [6.0, 6.0],
                            [6.0, 0.0],
                            [1.0, np.nan],
                            [6.0, 0.0],
                            [2.0, 0.0],
                            [2.0, 0.0],
                        ],
                    ],
                    [
                        [
                            [6.0, 6.0],
                            [0.0, 6.0],
                            [np.nan, np.nan],
                            [0.0, 6.0],
                            [0.0, 2.0],
                            [0.0, 2.0],
                        ],
                        [
                            [6.0, 6.0],
                            [0.0, 0.0],
                            [4.0, np.nan],
                            [3.0, 0.0],
                            [0.0, 2.0],
                            [2.0, 0.0],
                        ],
                    ],
                ],
                mask=[
                    [
                        [[1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1]],
                        [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]],
                    ],
                    [
                        [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]],
                        [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]],
                    ],
                ],
            ),
            "units": "degree_Celsius",
        },  # data
        {
            "data": 5,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # start threshold
        ">",  # start condition
        {
            "data": 5,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # end threshold
        "<",  # end condition
        {"data": 3, "units": "days"},  # start duration
        {"data": 3, "units": "days"},  # end duration
        {"data": 0, "units": "days"},  # start delay
        {"data": 0, "units": "days"},  # end delay
        np.ma.masked_array(
            data=[[[np.nan, 6], [0, 3]]], mask=[[[1, 0], [0, 0]]], dtype=np.float32
        ),
    ),  # postprocessing masked no-merge (masked spell, start spell, no start spell)
]

parameter_names = (
    "f_cube_tas, f_first_threshold, first_condition, f_second_threshold, "
    + "second_condition, f_first_duration, f_second_duration, f_first_delay, "
    + "f_second_delay, expected"
)
fixtures = [
    "f_cube_tas",
    "f_first_threshold",
    "f_second_threshold",
    "f_first_duration",
    "f_second_duration",
    "f_first_delay",
    "f_second_delay",
]


@pytest.mark.parametrize(
    parameter_names, TEST_SEASON_LENGTH_CALL_PARAMETERS, indirect=fixtures
)
def test_season_length_lazy_func(
    f_cube_tas,
    f_first_threshold,
    first_condition,
    f_second_threshold,
    second_condition,
    f_first_duration,
    f_second_duration,
    f_first_delay,
    f_second_delay,
    expected,
    f_dask_cluster,
):
    parameters = {
        "start_threshold": f_first_threshold,
        "start_condition": first_condition,
        "end_threshold": f_second_threshold,
        "end_condition": second_condition,
        "start_duration": f_first_duration,
        "end_duration": f_second_duration,
        "start_delay": f_first_delay,
        "end_delay": f_second_delay,
    }
    index_function = spl_func.SeasonLength(**parameters)
    with Client(f_dask_cluster) as client:
        lazy_func_test(index_function, f_cube_tas, expected, client)
    assert index_function.units == Unit("days")


@pytest.mark.parametrize(
    parameter_names, TEST_SEASON_LENGTH_POST_PROCESS_PARAMETERS, indirect=fixtures
)
def test_season_length_post_process(
    f_cube_tas,
    f_first_threshold,
    first_condition,
    f_second_threshold,
    second_condition,
    f_first_duration,
    f_second_duration,
    f_first_delay,
    f_second_delay,
    expected,
):
    parameters = {
        "start_threshold": f_first_threshold,
        "start_condition": first_condition,
        "end_threshold": f_second_threshold,
        "end_condition": second_condition,
        "start_duration": f_first_duration,
        "end_duration": f_second_duration,
        "start_delay": f_first_delay,
        "end_delay": f_second_delay,
    }
    index_function = spl_func.SeasonLength(**parameters)
    data = f_cube_tas.data
    if data.ndim < 5:
        shape = data.shape
        data = data.reshape((1,) + shape)
    aggregateby_cube = f_cube_tas
    cube, res = index_function.post_process(aggregateby_cube, data, None, None)
    assert np.array_equal(res, expected, equal_nan=True)
    expected_mask = np.ma.getmaskarray(expected)
    res_mask = da.ma.getmaskarray(res)
    assert (res_mask == expected_mask).all()


TEST_SPELL_LENGTH_CALL_PARAMETERS = [
    (
        {
            "data": np.array(
                [
                    [
                        [
                            [0.0, 1.0],
                            [0.0, 1.0],
                        ],
                    ],
                    [
                        [
                            [0.0, 0.0],
                            [1.0, 1.0],
                        ],
                    ],
                    [
                        [
                            [0.0, 1.0],
                            [0.0, 1.0],
                        ],
                    ],
                ],
            ),
            "standard_name": "lwe_thickness_of_precipitation_amount",
            "units": "mm",
        },  # data
        {
            "data": 1,
            "standard_name": "lwe_thickness_of_precipitation_amount",
            "units": "mm",
        },  # threshold
        "<",  # condition
        "max",  # reducer
        np.array(
            [
                [
                    [[3, 3, 0, 3, 1, np.nan, 1], [3, 0, 1, 0, np.nan, 2, np.nan]],
                    [[3, 1, 0, 1, 1, np.nan, 3], [3, 0, 0, 0, np.nan, np.nan, np.nan]],
                ]
            ]
        ),
    ),  # numpy array, one chunk (covered, internal spell, start and end spells, non)
    (
        {
            "data": da.array(
                [
                    [
                        [
                            [0.0, 0.0],
                            [1.0, 1.0],
                        ],
                    ],
                    [
                        [
                            [0.0, 0.0],
                            [1.0, 1.0],
                        ],
                    ],
                    [
                        [
                            [0.0, 0.0],
                            [1.0, 1.0],
                        ],
                    ],
                    [
                        [
                            [0.0, 1.0],
                            [0.0, 1.0],
                        ],
                    ],
                    [
                        [
                            [0.0, 1.0],
                            [0.0, 1.0],
                        ],
                    ],
                    [
                        [
                            [0.0, 1.0],
                            [0.0, 1.0],
                        ],
                    ],
                ],
            ).rechunk(3, -1, -1),
            "standard_name": "lwe_thickness_of_precipitation_amount",
            "units": "mm",
        },  # data
        {
            "data": 1,
            "standard_name": "lwe_thickness_of_precipitation_amount",
            "units": "mm",
        },  # threshold
        "<",  # condition
        "max",  # reducer
        np.array(
            [
                [
                    [[6, 6, 0, 6, 1, np.nan, 1], [6, 3, 0, 0, 1, np.nan, np.nan]],
                    [
                        [6, 0, 0, 3, np.nan, np.nan, 4],
                        [6, 0, 0, 0, np.nan, np.nan, np.nan],
                    ],
                ]
            ]
        ),
    ),  # dask array, two chunks (covered, start spell, end spell, no spell)
    (
        {
            "data": da.array(
                [
                    # chunk 1
                    [
                        [
                            [1.0, 1.0],
                            [1.0, 1.0],
                        ],
                    ],
                    [
                        [
                            [1.0, 1.0],
                            [1.0, 1.0],
                        ],
                    ],
                    [
                        [
                            [1.0, 1.0],
                            [1.0, 1.0],
                        ],
                    ],
                    [
                        [
                            [1.0, 1.0],
                            [1.0, 1.0],
                        ],
                    ],
                    [
                        [
                            [0.0, 0.0],
                            [0.0, 0.0],
                        ],
                    ],
                    # chunk 2
                    [
                        [
                            [0.0, 0.0],
                            [0.0, 0.0],
                        ],
                    ],
                    [
                        [
                            [1.0, 1.0],
                            [1.0, 1.0],
                        ],
                    ],
                    [
                        [
                            [0.0, 0.0],
                            [0.0, 0.0],
                        ],
                    ],
                    [
                        [
                            [0.0, 0.0],
                            [0.0, 0.0],
                        ],
                    ],
                    [
                        [
                            [1.0, 1.0],
                            [1.0, 1.0],
                        ],
                    ],
                ],
            ).rechunk(5, -1, -1),
            "standard_name": "lwe_thickness_of_precipitation_amount",
            "units": "mm",
        },  # data
        {
            "data": 1,
            "standard_name": "lwe_thickness_of_precipitation_amount",
            "units": "mm",
        },  # threshold
        "<",  # condition
        "max",  # reducer
        np.array(
            [
                [
                    [
                        [10, 0, 2, 0, np.nan, 5, np.nan],
                        [10, 0, 2, 0, np.nan, 5, np.nan],
                    ],
                    [
                        [10, 0, 2, 0, np.nan, 5, np.nan],
                        [10, 0, 2, 0, np.nan, 5, np.nan],
                    ],
                ]
            ]
        ),
    ),  # dask array, two chunks (covered, start spell, end spell, no spell)
    (
        {
            "data": da.array(
                [
                    # chunk 1
                    [
                        [
                            [0.0, 0.0],
                            [1.0, 1.0],
                        ],
                    ],
                    [
                        [
                            [0.0, 0.0],
                            [1.0, 0.0],
                        ],
                    ],
                    [
                        [
                            [0.0, 0.0],
                            [1.0, 1.0],
                        ],
                    ],
                    # chunk 2
                    [
                        [
                            [0.0, 1.0],
                            [0.0, 0.0],
                        ],
                    ],
                    [
                        [
                            [0.0, 0.0],
                            [0.0, 1.0],
                        ],
                    ],
                    [
                        [
                            [1.0, 0.0],
                            [0.0, 0.0],
                        ],
                    ],
                    # chunk 3
                    [
                        [
                            [1.0, 1.0],
                            [0.0, 0.0],
                        ],
                    ],
                    [
                        [
                            [1.0, 0.0],
                            [0.0, 1.0],
                        ],
                    ],
                    [
                        [
                            [0.0, 0.0],
                            [1.0, 0.0],
                        ],
                    ],
                    # chunk 4
                    [
                        [
                            [0.0, 0.0],
                            [1.0, 0.0],
                        ],
                    ],
                    [
                        [
                            [0.0, 0.0],
                            [1.0, 1.0],
                        ],
                    ],
                    [
                        [
                            [1.0, 0.0],
                            [1.0, 0.0],
                        ],
                    ],
                ],
            ).rechunk(3, -1, -1),
            "standard_name": "lwe_thickness_of_precipitation_amount",
            "units": "mm",
        },  # data
        {
            "data": 1,
            "standard_name": "lwe_thickness_of_precipitation_amount",
            "units": "mm",
        },  # threshold
        "<",  # condition
        "max",  # reducer
        np.array(
            [
                [
                    [[12, 5, 3, 0, 1, 9, np.nan], [12, 3, 2, 5, 1, 5, 8]],
                    [[12, 0, 5, 0, np.nan, 4, np.nan], [12, 0, 2, 1, np.nan, 6, 12]],
                ]
            ]
        ),
    ),  # dask array, 4 chunks different spells
    (
        {
            "data": da.array(
                [
                    # chunk 1
                    [
                        [
                            [0.0, 0.0],
                            [1.0, 0.0],
                        ],
                    ],
                    [
                        [
                            [1.0, 0.0],
                            [1.0, 0.0],
                        ],
                    ],
                    [
                        [
                            [1.0, 1.0],
                            [1.0, 0.0],
                        ],
                    ],
                    # chunk 2
                    [
                        [
                            [0.0, 1.0],
                            [1.0, 0.0],
                        ],
                    ],
                    [
                        [
                            [1.0, 0.0],
                            [1.0, 0.0],
                        ],
                    ],
                    [
                        [
                            [1.0, 1.0],
                            [1.0, 0.0],
                        ],
                    ],
                    # chunk 3
                    [
                        [
                            [0.0, 1.0],
                            [1.0, 0.0],
                        ],
                    ],
                    [
                        [
                            [0.0, 0.0],
                            [1.0, 0.0],
                        ],
                    ],
                    [
                        [
                            [1.0, 0.0],
                            [1.0, 0.0],
                        ],
                    ],
                    # chunk 4
                    [
                        [
                            [1.0, 0.0],
                            [1.0, 0.0],
                        ],
                    ],
                    [
                        [
                            [0.0, 0.0],
                            [1.0, 0.0],
                        ],
                    ],
                    [
                        [
                            [1.0, 0.0],
                            [1.0, 0.0],
                        ],
                    ],
                ],
            ).rechunk(3, -1, -1),
            "standard_name": "lwe_thickness_of_precipitation_amount",
            "units": "mm",
        },  # data
        {
            "data": 1,
            "standard_name": "lwe_thickness_of_precipitation_amount",
            "units": "mm",
        },  # threshold
        "<",  # condition
        "max",  # reducer
        np.array(
            [
                [
                    [[12, 1, 2, 0, 1, 7, np.nan], [12, 2, 1, 5, 1, 5, 8]],
                    [
                        [12, 0, 0, 0, np.nan, np.nan, np.nan],
                        [12, 12, 0, 12, 1, np.nan, 1],
                    ],
                ]
            ]
        ),
    ),  # dask array, 4 chunks different spells
    (
        {
            "data": np.ma.masked_array(
                data=[
                    [
                        [
                            [0.0, 1.0],
                            [0.0, 1.0],
                        ],
                    ],
                    [
                        [
                            [0.0, 0.0],
                            [1.0, 1.0],
                        ],
                    ],
                    [
                        [
                            [0.0, 1.0],
                            [0.0, 1.0],
                        ],
                    ],
                ],
                mask=[
                    [
                        [
                            [1, 0],
                            [0, 0],
                        ],
                    ],
                    [
                        [
                            [0, 1],
                            [0, 0],
                        ],
                    ],
                    [
                        [
                            [0, 0],
                            [0, 0],
                        ],
                    ],
                ],
            ),
            "standard_name": "lwe_thickness_of_precipitation_amount",
            "units": "mm",
        },  # data
        {
            "data": 1,
            "standard_name": "lwe_thickness_of_precipitation_amount",
            "units": "mm",
        },  # threshold
        "<",  # condition
        "max",  # reducer
        np.ma.masked_array(
            data=[
                [
                    [
                        [3, 0, 0, 2, np.nan, np.nan, 2],
                        [3, 0, 0, 0, np.nan, np.nan, np.nan],
                    ],
                    [[3, 1, 0, 1, 1, np.nan, 3], [3, 0, 0, 0, np.nan, np.nan, np.nan]],
                ]
            ],
            mask=[
                [
                    [[1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1]],
                    [[0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0]],
                ]
            ],
            dtype=np.float32,
        ),
    ),  # masked array, one chunk
    (
        {
            "data": da.ma.masked_array(
                data=[
                    # chunk 1
                    [
                        [
                            [0.0, 1.0],
                            [0.0, 1.0],
                        ],
                    ],
                    [
                        [
                            [0.0, 0.0],
                            [1.0, 1.0],
                        ],
                    ],
                    [
                        [
                            [0.0, 0.0],
                            [0.0, 1.0],
                        ],
                    ],
                    # chunk 2
                    [
                        [
                            [0.0, 0.0],
                            [0.0, 1.0],
                        ],
                    ],
                    [
                        [
                            [0.0, 1.0],
                            [1.0, 1.0],
                        ],
                    ],
                    [
                        [
                            [0.0, 1.0],
                            [0.0, 1.0],
                        ],
                    ],
                ],
                mask=[
                    # chunk 1
                    [
                        [
                            [0, 0],
                            [0, 0],
                        ],
                    ],
                    [
                        [
                            [0, 0],
                            [0, 0],
                        ],
                    ],
                    [
                        [
                            [0, 0],
                            [0, 0],
                        ],
                    ],
                    # chunk 2
                    [
                        [
                            [0, 1],
                            [0, 0],
                        ],
                    ],
                    [
                        [
                            [1, 0],
                            [0, 0],
                        ],
                    ],
                    [
                        [
                            [0, 0],
                            [0, 0],
                        ],
                    ],
                ],
            ).rechunk(2, -1, -1),
            "standard_name": "lwe_thickness_of_precipitation_amount",
            "units": "mm",
        },  # data
        {
            "data": 1,
            "standard_name": "lwe_thickness_of_precipitation_amount",
            "units": "mm",
        },  # threshold
        "<",  # condition
        "max",  # reducer
        np.ma.masked_array(
            data=[
                [
                    [
                        [6, 4, 0, 1, 1, np.nan, 6],
                        [6, 0, 2, 0, np.nan, 2, np.nan],
                    ],
                    [[6, 1, 2, 1, 1, 3, 6], [6, 0, 0, 0, np.nan, np.nan, np.nan]],
                ]
            ],
            mask=[
                [
                    [[1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1]],
                    [[0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0]],
                ]
            ],
            dtype=np.float32,
        ),
    ),  # masked array, two chunks
]

parameter_names = "f_cube_pr, f_first_threshold, condition, reducer, expected"
fixtures = [
    "f_cube_pr",
    "f_first_threshold",
]


@pytest.mark.parametrize(
    parameter_names, TEST_SPELL_LENGTH_CALL_PARAMETERS, indirect=fixtures
)
def test_spell_length_lazy_func(
    f_cube_pr,
    f_first_threshold,
    condition,
    reducer,
    expected,
    f_dask_cluster,
):
    parameters = {
        "threshold": f_first_threshold,
        "condition": condition,
        "statistic": reducer,
    }
    index_function = spl_func.SpellLength(**parameters)
    with Client(f_dask_cluster) as client:
        lazy_func_test(index_function, f_cube_pr, expected, client)
    assert index_function.units == Unit("days")


TEST_SPELL_LENGTH_POST_PROCESS_PARAMETERS = [
    (
        {
            "data": da.array(
                [
                    [
                        [6, 4, 0, 1, 1, np.nan, 6],
                        [6, 0, 2, 0, np.nan, 2, np.nan],
                    ],
                    [[6, 1, 2, 1, 1, 3, 6], [6, 0, 0, 0, np.nan, np.nan, np.nan]],
                ],
            ),
            "standard_name": "lwe_thickness_of_precipitation_amount",
            "units": "mm",
        },  # data
        {
            "data": 1,
            "standard_name": "lwe_thickness_of_precipitation_amount",
            "units": "mm",
        },  # threshold
        "<",  # condition
        "max",  # reducer
        np.array([[[4, 2], [2, 0]]]),  # expected
        {
            "first_threshold": iris.coords.AuxCoord(
                np.ma.masked_array(
                    data=[1],
                    mask=False,
                    dtype=np.float32,
                ),
                var_name="first_threshold",
                long_name="first_threshold",
                units=Unit("mm"),
            ),
            "spell_beginning": iris.coords.AuxCoord(
                np.array([[1, 2], [3, np.nan]]),
                var_name="spell_beginning",
                long_name="Day-of-year when longest spell begins",
                units=Unit("day"),
            ),
        },  # start
    ),  # postprocessing, one chunk
    (
        {
            "data": da.array(
                [
                    [
                        [
                            [6, 6, 0, 6, 1, np.nan, 1],
                            [6, 0, 0, 0, np.nan, np.nan, np.nan],
                        ],
                        [[6, 1, 1, 1, 1, 3, 6], [6, 0, 4, 0, np.nan, 2, np.nan]],
                    ],
                    [
                        [
                            [6, 5, 0, 0, 1, np.nan, np.nan],
                            [6, 1, 1, 2, 1, 3, 5],
                        ],
                        [[6, 0, 0, 5, np.nan, np.nan, 2], [6, 0, 2, 1, np.nan, 2, 6]],
                    ],
                    [
                        [
                            [6, 1, 3, 0, 1, 3, np.nan],
                            [6, 2, 1, 1, 1, 3, 6],
                        ],
                        [[6, 1, 2, 1, 1, 3, 6], [6, 4, 0, 1, 1, np.nan, 6]],
                    ],
                ]
            ).rechunk(1, -1, 2),
            "standard_name": "lwe_thickness_of_precipitation_amount",
            "units": "mm",
        },  # data
        {
            "data": 1,
            "standard_name": "lwe_thickness_of_precipitation_amount",
            "units": "mm",
        },  # threshold
        "<",  # condition
        "max",  # reducer
        np.array([[[[6, 0], [1, 4]], [[5, 2], [5, 2]], [[3, 2], [2, 4]]]]),  # expected
        {
            "first_threshold": iris.coords.AuxCoord(
                np.ma.masked_array(
                    data=[1],
                    mask=False,
                    dtype=np.float32,
                ),
                var_name="first_threshold",
                long_name="first_threshold",
                units=Unit("mm"),
            ),
            "spell_beginning": iris.coords.AuxCoord(
                np.array([[[1, np.nan], [1, 2]], [[1, 5], [2, 2]], [[3, 1], [3, 1]]]),
                var_name="spell_beginning",
                long_name="Day-of-year when longest spell begins",
                units=Unit("day"),
            ),
        },  # start
    ),  # postprocessing, three chunks
    (
        {
            "data": da.ma.masked_array(
                data=[
                    [
                        [6, 4, 0, 1, 1, np.nan, 6],
                        [6, 0, 2, 0, np.nan, 2, np.nan],
                    ],
                    [[6, 1, 2, 1, 1, 3, 6], [6, 0, 0, 0, np.nan, np.nan, np.nan]],
                ],
                mask=[
                    [
                        [1, 1, 1, 1, 1, 1, 1],
                        [0, 0, 0, 0, 0, 0, 0],
                    ],
                    [
                        [0, 0, 0, 0, 0, 0, 0],
                        [0, 0, 0, 0, 0, 0, 0],
                    ],
                ],
            ),
            "standard_name": "lwe_thickness_of_precipitation_amount",
            "units": "mm",
        },  # data
        {
            "data": 1,
            "standard_name": "lwe_thickness_of_precipitation_amount",
            "units": "mm",
        },  # threshold
        "<",  # condition
        "max",  # reducer
        np.ma.masked_array(
            data=[[[1e20, 2], [2, 0]]], mask=[[[1, 0], [0, 0]]], dtype=np.float32
        ),  # expected
        {
            "first_threshold": iris.coords.AuxCoord(
                np.ma.masked_array(
                    data=[1],
                    mask=False,
                    dtype=np.float32,
                ),
                var_name="first_threshold",
                long_name="first_threshold",
                units=Unit("mm"),
            ),
            "spell_beginning": iris.coords.AuxCoord(
                np.ma.masked_array(
                    data=[[1, 2], [3, np.nan]],
                    mask=[[[1, 0], [0, 0]]],
                    dtype=np.float32,
                ),
                var_name="spell_beginning",
                long_name="Day-of-year when longest spell begins",
                units=Unit("day"),
            ),
        },  # start
    ),  # postprocessing masked
]

parameter_names = (
    "f_cube_pr, f_first_threshold, condition, reducer, expected, expected_aux_coord"
)


@pytest.mark.parametrize(
    parameter_names, TEST_SPELL_LENGTH_POST_PROCESS_PARAMETERS, indirect=fixtures
)
def test_spell_length_post_process(
    f_cube_pr,
    f_first_threshold,
    condition,
    reducer,
    expected,
    expected_aux_coord,
    f_dask_cluster,
):
    parameters = {
        "threshold": f_first_threshold,
        "condition": condition,
        "statistic": reducer,
    }
    index_function = spl_func.SpellLength(**parameters)
    data = f_cube_pr.core_data()
    if data.ndim < 5:
        shape = data.shape
        data = data.reshape((1,) + shape)
    aggregateby_cube = f_cube_pr
    cube, res = index_function.post_process(aggregateby_cube, data, None, None)
    assert np.array_equal(res, expected, equal_nan=True)
    expected_mask = np.ma.getmaskarray(expected)
    res_mask = da.ma.getmaskarray(res)
    assert (res_mask == expected_mask).all()
    extra_coords = index_function.extra_coords
    for aux_coord in extra_coords:
        expected_coord = expected_aux_coord[aux_coord.var_name]
        assert aux_coord.var_name == expected_coord.var_name
        assert aux_coord.long_name == expected_coord.long_name
        assert aux_coord.units == expected_coord.units
        assert np.array_equal(aux_coord.points, expected_coord.points, equal_nan=True)
        expected_mask_start = np.ma.getmaskarray(expected_coord.points)
        start_mask = np.ma.getmaskarray(aux_coord.points)
        assert (start_mask == expected_mask_start).all()


TEST_START_OF_SPRING_CALL_PARAMETERS = {
    "spell-cover-year": (
        {
            "data": np.ones(1464).reshape(366, 2, 2),
            "units": "degree_Celsius",
        },  # data
        {
            "data": 0,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # threshold
        ">",  # condition
        {"data": 7, "units": "days"},  # duration
        {"data": 45, "units": "days"},  # delay
        np.array(
            [
                [
                    [
                        [366.0, np.nan],
                        [0, np.nan],
                        [46.0, np.nan],
                        [321.0, np.nan],
                        [6.0, np.nan],
                        [6.0, np.nan],
                    ],
                    [
                        [366.0, np.nan],
                        [0, np.nan],
                        [46.0, np.nan],
                        [321.0, np.nan],
                        [6.0, np.nan],
                        [6.0, np.nan],
                    ],
                ],
                [
                    [
                        [366.0, np.nan],
                        [0, np.nan],
                        [46.0, np.nan],
                        [321.0, np.nan],
                        [6.0, np.nan],
                        [6.0, np.nan],
                    ],
                    [
                        [366.0, np.nan],
                        [0, np.nan],
                        [46.0, np.nan],
                        [321.0, np.nan],
                        [6.0, np.nan],
                        [6.0, np.nan],
                    ],
                ],
            ]
        ),  # expected
    ),
    "no-spell": (
        {
            "data": np.zeros(1464).reshape(366, 2, 2),
            "units": "degree_Celsius",
        },  # data
        {
            "data": 0,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # threshold
        ">",  # condition
        {"data": 7, "units": "days"},  # duration
        {"data": 45, "units": "days"},  # delay
        np.array(
            [
                [
                    [
                        [366.0, np.nan],
                        [0, np.nan],
                        [np.nan, np.nan],
                        [0, np.nan],
                        [0.0, np.nan],
                        [0.0, np.nan],
                    ],
                    [
                        [366.0, np.nan],
                        [0, np.nan],
                        [np.nan, np.nan],
                        [0, np.nan],
                        [0.0, np.nan],
                        [0.0, np.nan],
                    ],
                ],
                [
                    [
                        [366.0, np.nan],
                        [0, np.nan],
                        [np.nan, np.nan],
                        [0, np.nan],
                        [0.0, np.nan],
                        [0.0, np.nan],
                    ],
                    [
                        [366.0, np.nan],
                        [0, np.nan],
                        [np.nan, np.nan],
                        [0, np.nan],
                        [0.0, np.nan],
                        [0.0, np.nan],
                    ],
                ],
            ]
        ),  # expected
    ),
    "last-day-leap-year": (
        {
            "data": (np.ones(366) + np.arange(start=-212, stop=154)).reshape(366, 1, 1),
            "units": "degree_Celsius",
        },  # data
        {
            "data": 0,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # threshold
        ">",  # condition
        {"data": 7, "units": "days"},  # duration
        {"data": 45, "units": "days"},  # delay
        np.array(
            [
                [
                    [
                        [366.0, np.nan],
                        [0, np.nan],
                        [213, np.nan],
                        [154, np.nan],
                        [0.0, np.nan],
                        [6.0, np.nan],
                    ],
                ],
            ]
        ),  # expected
    ),
    "last-day-no-leap-year": (
        {
            "data": (np.ones(365) + np.arange(start=-212, stop=153)).reshape(365, 1, 1),
            "units": "degree_Celsius",
        },  # data
        {
            "data": 0,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # threshold
        ">",  # condition
        {"data": 7, "units": "days"},  # duration
        {"data": 45, "units": "days"},  # delay
        np.array(
            [
                [
                    [
                        [365.0, np.nan],
                        [0, np.nan],
                        [213, np.nan],
                        [153, np.nan],
                        [0.0, np.nan],
                        [6.0, np.nan],
                    ],
                ],
            ]
        ),  # expected
    ),
}

TEST_START_OF_SPRING_POST_PROCESS_PARAMETERS = {
    "spell-cover-year": (
        {
            "data": np.ma.masked_array(
                data=[
                    [
                        [
                            [
                                [366.0, np.nan],
                                [0, np.nan],
                                [46.0, np.nan],
                                [321.0, np.nan],
                                [6.0, np.nan],
                                [6.0, np.nan],
                            ],
                            [
                                [366.0, np.nan],
                                [0, np.nan],
                                [46.0, np.nan],
                                [321.0, np.nan],
                                [6.0, np.nan],
                                [6.0, np.nan],
                            ],
                        ]
                    ],
                ],
            ),
            "units": "degree_Celsius",
        },  # data
        {
            "data": 0,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # threshold
        ">",  # condition
        {"data": 7, "units": "days"},  # duration
        {"data": 45, "units": "days"},  # start delay
        [1],  # leap years
        np.array([[[46.0, 46.0]]]),
    ),
    "no-spell": (
        {
            "data": np.ma.masked_array(
                data=[
                    [
                        [
                            [
                                [366.0, np.nan],
                                [0, np.nan],
                                [np.nan, np.nan],
                                [0, np.nan],
                                [0.0, np.nan],
                                [0.0, np.nan],
                            ],
                            [
                                [366.0, np.nan],
                                [0, np.nan],
                                [np.nan, np.nan],
                                [0, np.nan],
                                [0.0, np.nan],
                                [0.0, np.nan],
                            ],
                        ]
                    ],
                ],
            ),
            "units": "degree_Celsius",
        },  # data
        {
            "data": 0,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # threshold
        ">",  # condition
        {"data": 7, "units": "days"},  # duration
        {"data": 45, "units": "days"},  # start delay
        [1],  # leap years
        np.array([[[np.nan, np.nan]]]),
    ),
    "last-day-leap-year": (
        {
            "data": np.ma.masked_array(
                data=[
                    [
                        [
                            [
                                [366.0, np.nan],
                                [0, np.nan],
                                [213, np.nan],
                                [154, np.nan],
                                [0.0, np.nan],
                                [6.0, np.nan],
                            ],
                        ]
                    ],
                ],
            ),
            "units": "degree_Celsius",
        },  # data
        {
            "data": 0,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # threshold
        ">",  # condition
        {"data": 7, "units": "days"},  # duration
        {"data": 45, "units": "days"},  # start delay
        [1],  # leap years
        np.array([[[213.0]]]),
    ),
    "last-day-no-leap-year": (
        {
            "data": np.ma.masked_array(
                data=[
                    [
                        [
                            [
                                [365.0, np.nan],
                                [0, np.nan],
                                [213, np.nan],
                                [153, np.nan],
                                [0.0, np.nan],
                                [6.0, np.nan],
                            ],
                        ]
                    ],
                ],
            ),
            "units": "degree_Celsius",
        },  # data
        {
            "data": 0,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # threshold
        ">",  # condition
        {"data": 7, "units": "days"},  # duration
        {"data": 45, "units": "days"},  # start delay
        [0],  # leap years
        np.array([[[np.nan]]]),
    ),
}

parameter_names = (
    "f_cube_tas, f_first_threshold, condition, f_first_duration, "
    + "f_second_delay, expected"
)
fixtures = ["f_cube_tas", "f_first_threshold", "f_first_duration", "f_second_delay"]


@pytest.mark.parametrize(
    parameter_names,
    TEST_START_OF_SPRING_CALL_PARAMETERS.values(),
    ids=TEST_START_OF_SPRING_CALL_PARAMETERS.keys(),
    indirect=fixtures,
)
def test_start_of_spring_lazy_func(
    f_cube_tas,
    f_first_threshold,
    condition,
    f_first_duration,
    f_second_delay,
    expected,
    f_dask_cluster,
):
    parameters = {
        "threshold": f_first_threshold,
        "condition": condition,
        "duration": f_first_duration,
        "delay": f_second_delay,
    }
    index_function = spl_func.StartOfSpring(**parameters)
    with Client(f_dask_cluster) as client:
        lazy_func_test(index_function, f_cube_tas, expected, client)
        assert index_function.units == Unit("days")


parameter_names = (
    "f_cube_tas, f_first_threshold, condition, f_first_duration, "
    + "f_second_delay, leap_years, expected"
)


@pytest.mark.parametrize(
    parameter_names,
    TEST_START_OF_SPRING_POST_PROCESS_PARAMETERS.values(),
    ids=TEST_START_OF_SPRING_POST_PROCESS_PARAMETERS.keys(),
    indirect=fixtures,
)
def test_start_of_spring_post_process(
    f_cube_tas,
    f_first_threshold,
    condition,
    f_first_duration,
    f_second_delay,
    leap_years,
    expected,
):
    parameters = {
        "threshold": f_first_threshold,
        "condition": condition,
        "duration": f_first_duration,
        "delay": f_second_delay,
    }
    index_function = spl_func.StartOfSpring(**parameters)
    data = f_cube_tas.data
    aggregateby_cube = f_cube_tas
    index_function.leap_years = leap_years
    cube, res = index_function.post_process(aggregateby_cube, data, None, None)
    assert np.array_equal(res, expected, equal_nan=True)
    expected_mask = np.ma.getmaskarray(expected)
    res_mask = np.ma.getmaskarray(res)
    assert (res_mask == expected_mask).all()


TEST_START_OF_SUMMER_CALL_PARAMETERS = {
    "spell-cover-year": (
        {
            "data": np.ones(1464).reshape(366, 2, 2) * 10,
            "units": "degree_Celsius",
        },  # data
        {
            "data": 0,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # spring threshold
        ">",  # spring condition
        {"data": 7, "units": "days"},  # spring duration
        {"data": 45, "units": "days"},  # spring delay
        {
            "data": 10,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # summer threshold
        ">=",  # summer condition
        {"data": 5, "units": "days"},  # summer duration
        {"data": 45, "units": "days"},  # summer delay
        {
            "data": 10,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # autumn threshold
        "<",  # autumn condition
        {"data": 5, "units": "days"},  # autumn duration
        {"data": 212, "units": "days"},  # autumn delay
        np.array(
            [
                [
                    [
                        [[366.0, 366.0, 366.0], [366, np.nan, np.nan]],
                        [[0, 0, 0], [0, np.nan, np.nan]],
                        [[46, 46, np.nan], [47, np.nan, np.nan]],
                        [[321, 321, 0], [321, np.nan, np.nan]],
                        [[6, 6, 0], [4, np.nan, np.nan]],
                        [[6, 6, 0], [4, np.nan, np.nan]],
                    ],
                    [
                        [[366.0, 366.0, 366.0], [366, np.nan, np.nan]],
                        [[0, 0, 0], [0, np.nan, np.nan]],
                        [[46, 46, np.nan], [47, np.nan, np.nan]],
                        [[321, 321, 0], [321, np.nan, np.nan]],
                        [[6, 6, 0], [4, np.nan, np.nan]],
                        [[6, 6, 0], [4, np.nan, np.nan]],
                    ],
                ],
                [
                    [
                        [[366.0, 366.0, 366.0], [366, np.nan, np.nan]],
                        [[0, 0, 0], [0, np.nan, np.nan]],
                        [[46, 46, np.nan], [47, np.nan, np.nan]],
                        [[321, 321, 0], [321, np.nan, np.nan]],
                        [[6, 6, 0], [4, np.nan, np.nan]],
                        [[6, 6, 0], [4, np.nan, np.nan]],
                    ],
                    [
                        [[366.0, 366.0, 366.0], [366, np.nan, np.nan]],
                        [[0, 0, 0], [0, np.nan, np.nan]],
                        [[46, 46, np.nan], [47, np.nan, np.nan]],
                        [[321, 321, 0], [321, np.nan, np.nan]],
                        [[6, 6, 0], [4, np.nan, np.nan]],
                        [[6, 6, 0], [4, np.nan, np.nan]],
                    ],
                ],
            ]
        ),  # expected
    ),
    "no-spell": (
        {
            "data": np.zeros(366).reshape(366, 1, 1),
            "units": "degree_Celsius",
        },  # data
        {
            "data": 0,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # spring threshold
        ">",  # spring condition
        {"data": 7, "units": "days"},  # spring duration
        {"data": 45, "units": "days"},  # spring delay
        {
            "data": 10,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # summer threshold
        ">=",  # summer condition
        {"data": 5, "units": "days"},  # summer duration
        {"data": 45, "units": "days"},  # summer delay
        {
            "data": 10,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # autumn threshold
        "<",  # autumn condition
        {"data": 5, "units": "days"},  # autumn duration
        {"data": 212, "units": "days"},  # autumn delay
        np.array(
            [
                [
                    [
                        [[366.0, 366.0, 366.0], [366, np.nan, np.nan]],
                        [[0, 0, 0], [0, np.nan, np.nan]],
                        [[np.nan, np.nan, 214], [np.nan, np.nan, np.nan]],
                        [[0, 0, 153], [0, np.nan, np.nan]],
                        [[0, 0, 4], [0, np.nan, np.nan]],
                        [[0, 0, 4], [0, np.nan, np.nan]],
                    ],
                ],
            ]
        ),  # expected
    ),
    "last-day-leap-year": (
        {
            "data": (np.ones(366) + np.arange(start=-212, stop=154)).reshape(366, 1, 1)
            * 10,
            "units": "degree_Celsius",
        },  # data
        {
            "data": 0,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # spring threshold
        ">",  # spring condition
        {"data": 7, "units": "days"},  # spring duration
        {"data": 45, "units": "days"},  # spring delay
        {
            "data": 10,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # summer threshold
        ">=",  # summer condition
        {"data": 5, "units": "days"},  # summer duration
        {"data": 45, "units": "days"},  # summer delay
        {
            "data": 10,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # autumn threshold
        "<",  # autumn condition
        {"data": 5, "units": "days"},  # autumn duration
        {"data": 212, "units": "days"},  # autumn delay
        np.array(
            [
                [
                    [
                        [[366.0, 366.0, 366.0], [366, np.nan, np.nan]],
                        [[0, 0, 0], [0, np.nan, np.nan]],
                        [[213, 213, np.nan], [214, np.nan, np.nan]],
                        [[154, 154, 0], [154, np.nan, np.nan]],
                        [[0, 0, 4], [0, np.nan, np.nan]],
                        [[6, 6, 0], [4, np.nan, np.nan]],
                    ],
                ],
            ]
        ),  # expected
    ),
    "spring-is-late": (
        {
            "data": (np.ones(365) + np.arange(start=-212, stop=153)).reshape(365, 1, 1)
            * 10,
            "units": "degree_Celsius",
        },  # data
        {
            "data": 0,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # spring threshold
        ">",  # spring condition
        {"data": 7, "units": "days"},  # spring duration
        {"data": 45, "units": "days"},  # spring delay
        {
            "data": 10,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # summer threshold
        ">=",  # summer condition
        {"data": 5, "units": "days"},  # summer duration
        {"data": 45, "units": "days"},  # summer delay
        {
            "data": 10,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # autumn threshold
        "<",  # autumn condition
        {"data": 5, "units": "days"},  # autumn duration
        {"data": 212, "units": "days"},  # autumn delay
        np.array(
            [
                [
                    [
                        [[365.0, 365.0, 365.0], [365, np.nan, np.nan]],
                        [[0, 0, 0], [0, np.nan, np.nan]],
                        [[213, 213, np.nan], [214, np.nan, np.nan]],
                        [[153, 153, 0], [153, np.nan, np.nan]],
                        [[0, 0, 4], [0, np.nan, np.nan]],
                        [[6, 6, 0], [4, np.nan, np.nan]],
                    ],
                ],
            ]
        ),  # expected
    ),
}

TEST_START_OF_SUMMER_POST_PROCESS_PARAMETERS = {
    "spell-cover-year": (
        {
            "data": np.ma.masked_array(
                data=[
                    [
                        [
                            [
                                [[366, 366.0, 366.0], [366.0, np.nan, np.nan]],
                                [[0, 0, 0], [0, np.nan, np.nan]],
                                [[46, 46, np.nan], [47, np.nan, np.nan]],
                                [[321, 321, 0], [321, np.nan, np.nan]],
                                [[6, 6, 0], [4, np.nan, np.nan]],
                                [[6, 6, 0], [4, np.nan, np.nan]],
                            ],
                        ]
                    ],
                ],
            ),
            "units": "degree_Celsius",
        },  # data
        {
            "data": 0,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # spring threshold
        ">",  # spring condition
        {"data": 7, "units": "days"},  # spring duration
        {"data": 45, "units": "days"},  # spring delay
        {
            "data": 10,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # summer threshold
        ">=",  # summer condition
        {"data": 5, "units": "days"},  # summer duration
        {"data": 45, "units": "days"},  # summer delay
        {
            "data": 10,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # autumn threshold
        "<",  # autumn condition
        {"data": 5, "units": "days"},  # autumn duration
        {"data": 212, "units": "days"},  # autumn delay
        [1],  # leap years
        np.array([[[47.0]]]),
    ),
    "no-spell": (
        {
            "data": np.ma.masked_array(
                data=[
                    [
                        [
                            [
                                [[366.0, 366.0, 366.0], [366, np.nan, np.nan]],
                                [[0, 0, 0], [0, np.nan, np.nan]],
                                [[np.nan, np.nan, 214], [np.nan, np.nan, np.nan]],
                                [[0, 0, 153], [0, np.nan, np.nan]],
                                [[0, 0, 4], [0, np.nan, np.nan]],
                                [[0, 0, 4], [0, np.nan, np.nan]],
                            ],
                            [
                                [[366.0, 366.0, 366.0], [366, np.nan, np.nan]],
                                [[0, 0, 0], [0, np.nan, np.nan]],
                                [[np.nan, np.nan, 214], [np.nan, np.nan, np.nan]],
                                [[0, 0, 153], [0, np.nan, np.nan]],
                                [[0, 0, 4], [0, np.nan, np.nan]],
                                [[0, 0, 4], [0, np.nan, np.nan]],
                            ],
                        ]
                    ],
                ],
            ),
            "units": "degree_Celsius",
        },  # data
        {
            "data": 0,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # spring threshold
        ">",  # spring condition
        {"data": 7, "units": "days"},  # spring duration
        {"data": 45, "units": "days"},  # spring delay
        {
            "data": 10,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # summer threshold
        ">=",  # summer condition
        {"data": 5, "units": "days"},  # summer duration
        {"data": 45, "units": "days"},  # summer delay
        {
            "data": 10,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # autumn threshold
        "<",  # autumn condition
        {"data": 5, "units": "days"},  # autumn duration
        {"data": 212, "units": "days"},  # autumn delay
        [1],  # leap years
        np.array([[[np.nan, np.nan]]]),
    ),
    "last-day-leap-year": (
        {
            "data": np.ma.masked_array(
                data=[
                    [
                        [
                            [
                                [[366.0, 366.0, 366.0], [366, np.nan, np.nan]],
                                [[0, 0, 0], [0, np.nan, np.nan]],
                                [[213, 213, np.nan], [214, np.nan, np.nan]],
                                [[154, 154, 0], [154, np.nan, np.nan]],
                                [[0, 0, 4], [0, np.nan, np.nan]],
                                [[6, 6, 0], [4, np.nan, np.nan]],
                            ],
                        ],
                    ],
                ],
            ),
            "units": "degree_Celsius",
        },  # data
        {
            "data": 0,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # spring threshold
        ">",  # spring condition
        {"data": 7, "units": "days"},  # spring duration
        {"data": 45, "units": "days"},  # spring delay
        {
            "data": 10,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # summer threshold
        ">=",  # summer condition
        {"data": 5, "units": "days"},  # summer duration
        {"data": 45, "units": "days"},  # summer delay
        {
            "data": 10,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # autumn threshold
        "<",  # autumn condition
        {"data": 5, "units": "days"},  # autumn duration
        {"data": 212, "units": "days"},  # autumn delay
        [1],  # leap years
        np.array([[[214.0]]]),
    ),
    "last-day-no-leap-year": (
        {
            "data": np.ma.masked_array(
                data=[
                    [
                        [
                            [
                                [[365.0, 365.0, 365.0], [365, np.nan, np.nan]],
                                [[0, 0, 0], [0, np.nan, np.nan]],
                                [[213, 213, np.nan], [214, np.nan, np.nan]],
                                [[153, 153, 0], [153, np.nan, np.nan]],
                                [[0, 0, 4], [0, np.nan, np.nan]],
                                [[6, 6, 0], [4, np.nan, np.nan]],
                            ],
                        ]
                    ],
                ],
            ),
            "units": "degree_Celsius",
        },  # data
        {
            "data": 0,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # spring threshold
        ">",  # spring condition
        {"data": 7, "units": "days"},  # spring duration
        {"data": 45, "units": "days"},  # spring delay
        {
            "data": 10,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # summer threshold
        ">=",  # summer condition
        {"data": 5, "units": "days"},  # summer duration
        {"data": 45, "units": "days"},  # summer delay
        {
            "data": 10,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # autumn threshold
        "<",  # autumn condition
        {"data": 5, "units": "days"},  # autumn duration
        {"data": 212, "units": "days"},  # autumn delay
        [0],  # leap years
        np.array([[[np.nan]]]),
    ),
}


parameter_names = (
    "f_cube_tas, f_first_threshold, first_condition, f_first_duration, f_first_delay, "
    + "f_second_threshold, second_condition, f_second_duration, f_second_delay, "
    + "f_third_threshold, third_condition, f_third_duration, f_third_delay, "
    + "expected"
)
fixtures = [
    "f_cube_tas",
    "f_first_threshold",
    "f_first_duration",
    "f_first_delay",
    "f_second_threshold",
    "f_second_duration",
    "f_second_delay",
    "f_third_threshold",
    "f_third_duration",
    "f_third_delay",
]


@pytest.mark.parametrize(
    parameter_names,
    TEST_START_OF_SUMMER_CALL_PARAMETERS.values(),
    ids=TEST_START_OF_SUMMER_CALL_PARAMETERS.keys(),
    indirect=fixtures,
)
def test_start_of_summer_lazy_func(
    f_cube_tas,
    f_first_threshold,
    first_condition,
    f_first_duration,
    f_first_delay,
    f_second_threshold,
    second_condition,
    f_second_duration,
    f_second_delay,
    f_third_threshold,
    third_condition,
    f_third_duration,
    f_third_delay,
    expected,
    f_dask_cluster,
):
    parameters = {
        "spring_start_threshold": f_first_threshold,
        "spring_start_condition": first_condition,
        "spring_start_duration": f_first_duration,
        "spring_start_delay": f_first_delay,
        "spring_end_threshold": f_second_threshold,
        "spring_end_condition": second_condition,
        "spring_end_duration": f_second_duration,
        "spring_end_delay": f_second_delay,
        "autumn_start_threshold": f_third_threshold,
        "autumn_start_condition": third_condition,
        "autumn_start_duration": f_third_duration,
        "autumn_start_delay": f_third_delay,
    }
    index_function = spl_func.StartOfSummer(**parameters)
    with Client(f_dask_cluster) as client:
        lazy_func_test(index_function, f_cube_tas, expected, client)
        assert index_function.units == Unit("days")


parameter_names = (
    "f_cube_tas, f_first_threshold, first_condition, f_first_duration, f_first_delay, "
    + "f_second_threshold, second_condition, f_second_duration, f_second_delay, "
    + "f_third_threshold, third_condition, f_third_duration, f_third_delay, "
    + "leap_years, expected"
)


@pytest.mark.parametrize(
    parameter_names,
    TEST_START_OF_SUMMER_POST_PROCESS_PARAMETERS.values(),
    ids=TEST_START_OF_SUMMER_POST_PROCESS_PARAMETERS.keys(),
    indirect=fixtures,
)
def test_start_of_summer_post_process(
    f_cube_tas,
    f_first_threshold,
    first_condition,
    f_first_duration,
    f_first_delay,
    f_second_threshold,
    second_condition,
    f_second_duration,
    f_second_delay,
    f_third_threshold,
    third_condition,
    f_third_duration,
    f_third_delay,
    leap_years,
    expected,
    f_dask_cluster,
):
    parameters = {
        "spring_start_threshold": f_first_threshold,
        "spring_start_condition": first_condition,
        "spring_start_duration": f_first_duration,
        "spring_start_delay": f_first_delay,
        "spring_end_threshold": f_second_threshold,
        "spring_end_condition": second_condition,
        "spring_end_duration": f_second_duration,
        "spring_end_delay": f_second_delay,
        "autumn_start_threshold": f_third_threshold,
        "autumn_start_condition": third_condition,
        "autumn_start_duration": f_third_duration,
        "autumn_start_delay": f_third_delay,
    }
    index_function = spl_func.StartOfSummer(**parameters)
    data = f_cube_tas.data
    aggregateby_cube = f_cube_tas
    index_function.leap_years = leap_years
    index_function.summer.leap_years = leap_years
    index_function.spring.leap_years = leap_years
    cube, res = index_function.post_process(aggregateby_cube, data, None, None)
    assert np.array_equal(res, expected, equal_nan=True)
    expected_mask = np.ma.getmaskarray(expected)
    res_mask = np.ma.getmaskarray(res)
    assert (res_mask == expected_mask).all()


TEST_START_OF_WINTER_CALL_PARAMETERS = {
    "spell-cover-year": (
        {
            "data": np.zeros(273).reshape(273, 1, 1),
            "units": "degree_Celsius",
        },  # data
        {
            "data": 0,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # spring threshold
        ">",  # spring condition
        {"data": 7, "units": "days"},  # spring duration
        {"data": 198, "units": "days"},  # spring delay
        {
            "data": 0,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # winter threshold
        "<=",  # winter condition
        {"data": 5, "units": "days"},  # winter duration
        {"data": 0, "units": "days"},  # winter delay
        np.array(
            [
                [
                    [
                        [[273.0, 273.0], [np.nan, np.nan]],
                        [[0, 273], [np.nan, np.nan]],
                        [[np.nan, 1], [np.nan, np.nan]],
                        [[0, 273], [np.nan, np.nan]],
                        [[0, 4], [np.nan, np.nan]],
                        [[0, 4], [np.nan, np.nan]],
                    ],
                ],
            ]
        ),  # expected
    ),
    "no-spell": (
        {
            "data": np.ones(273).reshape(273, 1, 1),
            "units": "degree_Celsius",
        },  # data
        {
            "data": 0,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # spring threshold
        ">",  # spring condition
        {"data": 7, "units": "days"},  # spring duration
        {"data": 198, "units": "days"},  # spring delay
        {
            "data": 0,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # winter threshold
        "<=",  # winter condition
        {"data": 5, "units": "days"},  # winter duration
        {"data": 0, "units": "days"},  # winter delay
        np.array(
            [
                [
                    [
                        [[273.0, 273.0], [np.nan, np.nan]],
                        [[0, 0], [np.nan, np.nan]],
                        [[199, np.nan], [np.nan, np.nan]],
                        [[75, 0], [np.nan, np.nan]],
                        [[6, 0], [np.nan, np.nan]],
                        [[6, 0], [np.nan, np.nan]],
                    ],
                ],
            ]
        ),  # expected
    ),
    "last-day-leap-year": (
        {
            "data": (
                0.25 * np.sin(np.linspace(start=0, stop=1.4 * np.pi, num=275))
                + 0.25 * np.sin(np.linspace(start=0, stop=89 * np.pi, num=275))
            ).reshape(275, 1, 1),
            "units": "degree_Celsius",
        },  # data
        {
            "data": 0,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # spring threshold
        ">",  # spring condition
        {"data": 7, "units": "days"},  # spring duration
        {"data": 198, "units": "days"},  # spring delay
        {
            "data": 0,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # winter threshold
        "<=",  # winter condition
        {"data": 5, "units": "days"},  # winter duration
        {"data": 0, "units": "days"},  # winter delay
        np.array(
            [
                [
                    [
                        [[275.0, 275.0], [np.nan, np.nan]],
                        [[0, 1], [np.nan, np.nan]],
                        [[np.nan, 244], [np.nan, np.nan]],
                        [[0, 8], [np.nan, np.nan]],
                        [[0, 1], [np.nan, np.nan]],
                        [[0, 4], [np.nan, np.nan]],
                    ],
                ],
            ]
        ),  # expected
    ),
    "last-day-no-leap-year": (
        {
            "data": (
                0.25 * np.sin(np.linspace(start=0, stop=1.3 * np.pi, num=273))
                + 0.25 * np.sin(np.linspace(start=0, stop=82 * np.pi, num=273))
            ).reshape(273, 1, 1),
            "units": "degree_Celsius",
        },  # data
        {
            "data": 0,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # spring threshold
        ">",  # spring condition
        {"data": 7, "units": "days"},  # spring duration
        {"data": 198, "units": "days"},  # spring delay
        {
            "data": 0,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # winter threshold
        "<=",  # winter condition
        {"data": 5, "units": "days"},  # winter duration
        {"data": 0, "units": "days"},  # winter delay
        np.array(
            [
                [
                    [
                        [[273.0, 273.0], [np.nan, np.nan]],
                        [[0, 1], [np.nan, np.nan]],
                        [[np.nan, 243], [np.nan, np.nan]],
                        [[0, 5], [np.nan, np.nan]],
                        [[0, 1], [np.nan, np.nan]],
                        [[0, 4], [np.nan, np.nan]],
                    ],
                ],
            ]
        ),  # expected
    ),
    "winter-is-late": (
        {
            "data": (
                0.25 * np.sin(np.linspace(start=0, stop=1.3 * np.pi, num=273))
                + 0.25 * np.sin(np.linspace(start=0, stop=75 * np.pi, num=273))
            ).reshape(273, 1, 1),
            "units": "degree_Celsius",
        },  # data
        {
            "data": 0,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # spring threshold
        ">",  # spring condition
        {"data": 7, "units": "days"},  # spring duration
        {"data": 198, "units": "days"},  # spring delay
        {
            "data": 0,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # winter threshold
        "<=",  # winter condition
        {"data": 5, "units": "days"},  # winter duration
        {"data": 0, "units": "days"},  # winter delay
        np.array(
            [
                [
                    [
                        [[273.0, 273.0], [np.nan, np.nan]],
                        [[0, 1], [np.nan, np.nan]],
                        [[np.nan, 244], [np.nan, np.nan]],
                        [[0, 2], [np.nan, np.nan]],
                        [[0, 1], [np.nan, np.nan]],
                        [[0, 2], [np.nan, np.nan]],
                    ],
                ],
            ]
        ),  # expected
    ),
}

TEST_START_OF_WINTER_POST_PROCESS_PARAMETERS = {
    "spell-cover-year": (
        {
            "data": np.ma.masked_array(
                data=[
                    [
                        [
                            [
                                [[273.0, 273.0], [np.nan, np.nan]],
                                [[0, 273], [np.nan, np.nan]],
                                [[np.nan, 1], [np.nan, np.nan]],
                                [[0, 273], [np.nan, np.nan]],
                                [[0, 4], [np.nan, np.nan]],
                                [[0, 4], [np.nan, np.nan]],
                            ],
                        ]
                    ],
                ],
            ),
            "units": "degree_Celsius",
        },  # data
        {
            "data": 0,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # spring threshold
        ">",  # spring condition
        {"data": 7, "units": "days"},  # spring duration
        {"data": 198, "units": "days"},  # spring delay
        {
            "data": 0,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # winter threshold
        "<=",  # winter condition
        {"data": 5, "units": "days"},  # winter duration
        {"data": 0, "units": "days"},  # winter delay
        [0],  # leap years
        np.array([[[-152]]]),
    ),
    "no-spell": (
        {
            "data": np.ma.masked_array(
                data=[
                    [
                        [
                            [
                                [[273.0, 273.0], [np.nan, np.nan]],
                                [[0, 0], [np.nan, np.nan]],
                                [[199, np.nan], [np.nan, np.nan]],
                                [[75, 0], [np.nan, np.nan]],
                                [[6, 0], [np.nan, np.nan]],
                                [[6, 0], [np.nan, np.nan]],
                            ],
                        ]
                    ],
                ],
            ),
            "units": "degree_Celsius",
        },  # data
        {
            "data": 0,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # spring threshold
        ">",  # spring condition
        {"data": 7, "units": "days"},  # spring duration
        {"data": 198, "units": "days"},  # spring delay
        {
            "data": 0,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # winter threshold
        "<=",  # winter condition
        {"data": 5, "units": "days"},  # winter duration
        {"data": 0, "units": "days"},  # winter delay
        [0],  # leap years
        np.array([[[np.nan]]]),
    ),
    "last-day-leap-year": (
        {
            "data": np.ma.masked_array(
                data=[
                    [
                        [
                            [
                                [[275.0, 275.0], [np.nan, np.nan]],
                                [[0, 1], [np.nan, np.nan]],
                                [[np.nan, 244], [np.nan, np.nan]],
                                [[0, 8], [np.nan, np.nan]],
                                [[0, 1], [np.nan, np.nan]],
                                [[0, 4], [np.nan, np.nan]],
                            ],
                        ],
                    ],
                ],
            ),
            "units": "degree_Celsius",
        },  # data
        {
            "data": 0,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # spring threshold
        ">",  # spring condition
        {"data": 7, "units": "days"},  # spring duration
        {"data": 198, "units": "days"},  # spring delay
        {
            "data": 0,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # winter threshold
        "<=",  # winter condition
        {"data": 5, "units": "days"},  # winter duration
        {"data": 0, "units": "days"},  # winter delay
        [1],  # leap years
        np.array([[[91]]]),
    ),
    "last-day-no-leap-year": (
        {
            "data": np.ma.masked_array(
                data=[
                    [
                        [
                            [
                                [[273.0, 273.0], [np.nan, np.nan]],
                                [[0, 1], [np.nan, np.nan]],
                                [[np.nan, 243], [np.nan, np.nan]],
                                [[0, 5], [np.nan, np.nan]],
                                [[0, 1], [np.nan, np.nan]],
                                [[0, 4], [np.nan, np.nan]],
                            ],
                        ]
                    ],
                ],
            ),
            "units": "degree_Celsius",
        },  # data
        {
            "data": 0,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # spring threshold
        ">",  # spring condition
        {"data": 7, "units": "days"},  # spring duration
        {"data": 198, "units": "days"},  # spring delay
        {
            "data": 0,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # winter threshold
        "<=",  # winter condition
        {"data": 5, "units": "days"},  # winter duration
        {"data": 0, "units": "days"},  # winter delay
        [0],  # leap years
        np.array([[[90]]]),
    ),
    "winter-is-late": (
        {
            "data": np.ma.masked_array(
                data=[
                    [
                        [
                            [
                                [[273.0, 273.0], [np.nan, np.nan]],
                                [[0, 1], [np.nan, np.nan]],
                                [[np.nan, 244], [np.nan, np.nan]],
                                [[0, 2], [np.nan, np.nan]],
                                [[0, 1], [np.nan, np.nan]],
                                [[0, 2], [np.nan, np.nan]],
                            ],
                        ]
                    ],
                ],
            ),
            "units": "degree_Celsius",
        },  # data
        {
            "data": 0,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # spring threshold
        ">",  # spring condition
        {"data": 7, "units": "days"},  # spring duration
        {"data": 198, "units": "days"},  # spring delay
        {
            "data": 0,
            "units": "degree_Celsius",
            "standard_name": "air_temperature",
        },  # winter threshold
        "<=",  # winter condition
        {"data": 5, "units": "days"},  # winter duration
        {"data": 0, "units": "days"},  # winter delay
        [0],  # leap years
        np.array([[[np.nan]]]),
    ),
}


parameter_names = (
    " f_cube_tas, f_first_threshold, first_condition, f_first_duration, f_first_delay, "
    + "f_second_threshold, second_condition, f_second_duration, f_second_delay, "
    + "expected"
)
fixtures = [
    "f_cube_tas",
    "f_first_threshold",
    "f_first_duration",
    "f_first_delay",
    "f_second_threshold",
    "f_second_duration",
    "f_second_delay",
]


@pytest.mark.parametrize(
    parameter_names,
    TEST_START_OF_WINTER_CALL_PARAMETERS.values(),
    ids=TEST_START_OF_WINTER_CALL_PARAMETERS.keys(),
    indirect=fixtures,
)
def test_start_of_winter_lazy_func(
    f_cube_tas,
    f_first_threshold,
    first_condition,
    f_first_duration,
    f_first_delay,
    f_second_threshold,
    second_condition,
    f_second_duration,
    f_second_delay,
    expected,
    f_dask_cluster,
):
    parameters = {
        "spring_start_threshold": f_first_threshold,
        "spring_start_condition": first_condition,
        "spring_start_duration": f_first_duration,
        "spring_start_delay": f_first_delay,
        "winter_start_threshold": f_second_threshold,
        "winter_start_condition": second_condition,
        "winter_start_duration": f_second_duration,
        "winter_start_delay": f_second_delay,
    }
    index_function = spl_func.StartOfWinter(**parameters)
    with Client(f_dask_cluster) as client:
        lazy_func_test(index_function, f_cube_tas, expected, client)
        assert index_function.units == Unit("days")


parameter_names = (
    "f_cube_tas, f_first_threshold, first_condition, f_first_duration, f_first_delay, "
    + "f_second_threshold, second_condition, f_second_duration, f_second_delay, "
    + "leap_years, expected"
)


@pytest.mark.parametrize(
    parameter_names,
    TEST_START_OF_WINTER_POST_PROCESS_PARAMETERS.values(),
    ids=TEST_START_OF_WINTER_POST_PROCESS_PARAMETERS.keys(),
    indirect=fixtures,
)
def test_start_of_winter_post_process(
    f_cube_tas,
    f_first_threshold,
    first_condition,
    f_first_duration,
    f_first_delay,
    f_second_threshold,
    second_condition,
    f_second_duration,
    f_second_delay,
    leap_years,
    expected,
    f_dask_cluster,
):
    parameters = {
        "spring_start_threshold": f_first_threshold,
        "spring_start_condition": first_condition,
        "spring_start_duration": f_first_duration,
        "spring_start_delay": f_first_delay,
        "winter_start_threshold": f_second_threshold,
        "winter_start_condition": second_condition,
        "winter_start_duration": f_second_duration,
        "winter_start_delay": f_second_delay,
    }
    index_function = spl_func.StartOfWinter(**parameters)
    data = f_cube_tas.data
    aggregateby_cube = f_cube_tas
    index_function.leap_years = leap_years
    index_function.spring.leap_years = leap_years
    cube, res = index_function.post_process(aggregateby_cube, data, None, None)
    assert np.array_equal(res, expected, equal_nan=True)
    expected_mask = np.ma.getmaskarray(expected)
    res_mask = np.ma.getmaskarray(res)
    assert (res_mask == expected_mask).all()
