import pytest
from dask.distributed import LocalCluster
from iris.cube import Cube
from iris.coords import AuxCoord
import numpy as np
from cf_units import Unit
from iris.coords import DimCoord


def create_and_add_dim_coord(cube, time):
    """Add time dimension coordinates to cube."""
    shape = cube.data.shape
    assert len(shape) == 3
    time_coord = DimCoord(
        time,
        var_name="time",
        standard_name="time",
        units="days since 1949-12-01 00:00:00",
    )
    cube.add_dim_coord(time_coord, 0)


def add_dim_coord(cube, coord):
    """Add time dimension coordinates to cube."""
    shape = cube.data.shape
    assert len(shape) == 3
    coord.guess_bounds()
    cube.add_dim_coord(coord, 0)


def add_aux_coord(cube, coord):
    """Add auxiliary coordinates to cube."""
    cube.add_aux_coord(coord)


@pytest.fixture
def f_cubes(request):
    """Fixture for creating a iris cubes."""
    test_cubes = request.param["cubes"]
    cubes = {}
    for name, value in test_cubes.items():
        cube = value["cube"]
        if "dim_coord_time" in value:
            add_dim_coord(cube, value["dim_coord_time"])
        if "aux_coord" in value:
            add_aux_coord(cube, value["aux_coord"])
        if cube.coord("time").bounds is None:
            cube.coord("time").guess_bounds()
        cubes.update({name: cube})
    return cubes


@pytest.fixture(scope="module")
def f_dask_cluster():
    cluster = LocalCluster(n_workers=2, threads_per_worker=2, dashboard_address=None)
    yield cluster
    cluster.close()


@pytest.fixture
def f_time_cube_tas(request):
    test_cube = Cube(
        data=request.param["data"].astype(np.float32),
        standard_name="air_temperature",
        var_name="tas",
        units=request.param["units"],
    )
    if "time" in request.param:
        create_and_add_dim_coord(test_cube, request.param["time"])
    return test_cube


@pytest.fixture
def f_cube_tas(request):
    test_cube = Cube(
        data=request.param["data"].astype(np.float32),
        standard_name="air_temperature",
        var_name="tas",
        units=request.param["units"],
    )
    return test_cube


@pytest.fixture
def f_cube_tasmax(request):
    test_cube = Cube(
        data=request.param["data"].astype(np.float32),
        standard_name="air_temperature",
        var_name="tasmax",
        units=request.param["units"],
    )
    return test_cube


@pytest.fixture
def f_cube_tasmin(request):
    test_cube = Cube(
        data=request.param["data"].astype(np.float32),
        standard_name="air_temperature",
        var_name="tasmin",
        units=request.param["units"],
    )
    return test_cube


@pytest.fixture
def f_cube_pr(request):
    test_cube = Cube(
        data=request.param["data"].astype(np.float32),
        standard_name=request.param["standard_name"],
        var_name="pr",
        units=request.param["units"],
    )
    return test_cube


@pytest.fixture
def f_first_threshold(request):
    long_name = "first_threshold"
    if "long_name" in request.param:
        long_name = request.param["long_name"]
    aux_coord = AuxCoord(
        np.array([request.param["data"]]),
        standard_name=request.param["standard_name"],
        units=Unit(request.param["units"]),
        var_name="first_threshold",
        long_name=long_name,
    )
    return aux_coord


@pytest.fixture
def f_second_threshold(request):
    long_name = "second_threshold"
    if "long_name" in request.param:
        long_name = request.param["long_name"]
    aux_coord = AuxCoord(
        np.array([request.param["data"]]),
        standard_name=request.param["standard_name"],
        units=Unit(request.param["units"]),
        var_name="second_threshold",
        long_name=long_name,
    )
    return aux_coord


@pytest.fixture
def f_third_threshold(request):
    long_name = "third_threshold"
    if "long_name" in request.param:
        long_name = request.param["long_name"]
    aux_coord = AuxCoord(
        np.array([request.param["data"]]),
        standard_name=request.param["standard_name"],
        units=Unit(request.param["units"]),
        var_name="third_threshold",
        long_name=long_name,
    )
    return aux_coord


@pytest.fixture
def f_percentile(request):
    aux_coord = AuxCoord(
        np.array([request.param["data"]]),
        units=Unit(request.param["units"]),
    )
    return aux_coord


@pytest.fixture
def f_window_size(request):
    aux_coord = AuxCoord(
        np.array([request.param["data"]]),
        units=Unit(request.param["units"]),
    )
    return aux_coord


@pytest.fixture
def f_first_duration(request):
    aux_coord = AuxCoord(
        np.array([request.param["data"]]),
        units=Unit(request.param["units"]),
    )
    return aux_coord


@pytest.fixture
def f_second_duration(request):
    aux_coord = AuxCoord(
        np.array([request.param["data"]]),
        units=Unit(request.param["units"]),
    )
    return aux_coord


@pytest.fixture
def f_third_duration(request):
    aux_coord = AuxCoord(
        np.array([request.param["data"]]),
        units=Unit(request.param["units"]),
    )
    return aux_coord


@pytest.fixture
def f_first_delay(request):
    aux_coord = AuxCoord(
        np.array([request.param["data"]]),
        units=Unit(request.param["units"]),
    )
    return aux_coord


@pytest.fixture
def f_second_delay(request):
    aux_coord = AuxCoord(
        np.array([request.param["data"]]),
        units=Unit(request.param["units"]),
    )
    return aux_coord


@pytest.fixture
def f_third_delay(request):
    aux_coord = AuxCoord(
        np.array([request.param["data"]]),
        units=Unit(request.param["units"]),
    )
    return aux_coord
