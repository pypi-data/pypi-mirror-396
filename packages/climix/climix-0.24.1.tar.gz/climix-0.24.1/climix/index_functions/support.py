# -*- coding: utf-8 -*-
import operator

from cf_units import Unit
import cftime
import dask.array as da
import iris
import iris.coords
import numpy as np

import gordias.util.time_string
import gordias.util.units


SUPPORTED_OPERATORS = [
    "<",
    ">",
    "<=",
    ">=",
]
SUPPORTED_REDUCERS = [
    "min",
    "max",
    "sum",
    "mean",
]


def scalar_mean(*args):
    return float(np.mean(args))


SCALAR_OPERATORS = {
    "<": operator.lt,
    ">": operator.gt,
    "<=": operator.le,
    ">=": operator.ge,
}
SCALAR_REDUCERS = {
    "min": min,
    "max": max,
    "sum": sum,
    "mean": scalar_mean,
}


NUMPY_OPERATORS = {
    "<": np.less,
    ">": np.greater,
    "<=": np.less_equal,
    ">=": np.greater_equal,
}
NUMPY_REDUCERS = {
    "min": np.min,
    "max": np.max,
    "sum": np.sum,
    "mean": np.mean,
}


DASK_OPERATORS = {
    "<": da.less,
    ">": da.greater,
    "<=": da.less_equal,
    ">=": da.greater_equal,
}
DASK_REDUCERS = {
    "min": da.min,
    "max": da.max,
    "sum": da.sum,
    "mean": da.mean,
}


class TimesHelper:
    def __init__(self, time):
        self.times = time.core_points()
        self.units = str(time.units)

    def __getattr__(self, name):
        return getattr(self.times, name)

    def __len__(self):
        return len(self.times)

    def __getitem__(self, key):
        return self.times[key]


class ComputationalPeriod:
    """
    Builds a :namedtuple:`TimeRange` for the computational period.

    Given a time period following the ISO8601 format, returns the
    :namedtuple:`TimeRange` containing datetime objects for the start and end.
    """

    def __init__(self, computational_period):
        if computational_period is not None:
            self.timerange = gordias.util.time_string.parse_isodate_time_range(
                computational_period
            )
        else:
            self.timerange = None


def normalize_axis(axis, ndim):
    if isinstance(axis, list) and len(axis) == 1:
        axis = axis[0]
    if axis < 0:
        # just cope with negative axis numbers
        axis += ndim
    return axis


def _add_mask(data, parameter_data, length, time_constraint):
    """Add a mask to data array given a length and time constraint."""
    mask = np.zeros(parameter_data.shape + (length,))
    for ind in np.ndindex(parameter_data.shape):
        threshold = parameter_data[ind]
        if np.isnan(threshold):
            mask[ind] = 1
        elif threshold > 1 and time_constraint == "start":
            mask[ind][slice(int(threshold) - 1)] = 1
        elif threshold > 1 and time_constraint == "end":
            mask[ind][slice(int(threshold) - 1, None, None)] = 1
        elif threshold <= 1 and time_constraint == "end":
            mask[ind] = 1
    mask = np.moveaxis(mask, -1, 0)
    res = np.ma.masked_array(data=data, mask=mask)
    return res


def _compute_offset(sub_cube, year):
    """Return the time offset in days from the first day of the year and the first day
    in the cube."""
    time = sub_cube.coord("time")
    time_units = Unit(f"days since {year}-01-01 00:00:00", calendar=time.units.calendar)
    first_day_of_year = cftime.date2num(
        cftime.datetime(year, 1, 1, 0, calendar=time.units.calendar),
        units=time_units.cftime_unit,
        calendar=time.units.calendar,
    )
    time.convert_units(time_units)
    first_day = time.points[0]
    offset = np.abs(first_day_of_year - first_day)
    offset = np.floor(offset)
    return offset


def _mask_data(input_cube, parameter_cube, time_constraint):
    """Return data array with values from `input_cube` that have been masked and
    parameters used for masking each year."""
    stack = []
    pstack = []
    first_year = input_cube.coord("year").points[0]
    last_year = input_cube.coord("year").points[-1]
    for year in range(first_year, last_year + 1):
        sub_cube = input_cube.extract(iris.Constraint(year=year))
        constraint = parameter_cube.extract(iris.Constraint(year=year))
        if constraint is not None:
            offset = _compute_offset(sub_cube, year)
            parameter_data = da.clip(
                da.asarray(constraint.lazy_data()).rechunk(100, 100) - offset, 0, None
            )
        else:
            # If there are no constraint for this year create a zero array threshold
            parameter_data = da.zeros(sub_cube.shape[1:], dtype=np.float32).rechunk(
                100, 100
            )
        length = sub_cube.shape[0]
        data = sub_cube.lazy_data().rechunk(-1, 100, 100)
        masked_data = da.blockwise(
            _add_mask,
            (2, 0, 1),
            data,
            (2, 0, 1),
            parameter_data,
            (0, 1),
            length=length,
            time_constraint=time_constraint,
            dtype=np.float32,
            meta=np.array((), dtype=parameter_data.dtype),
            concatenate=True,
        )
        stack.append(masked_data)
        pstack.append(parameter_data)
    return da.vstack(stack), da.stack(pstack, axis=0)


def mask_data_from_parameters(input_cubes, parameters):
    """Masks data in `input_cubes` given a mapping of a constraint to a parameter cube.

    The `parameters` should contain a mapping from a time constraint to a parameter
    cube, where the data from the parameter cube will be used as a threshold. The shape
    of the data must match the grid of the input cubes data. The input cubes data is
    then masked along the time dimension, either before or after the threshold
    depending on the time constraint. The time constraint should be either `start` or
    `end` to indicate if the data is masked before or after the threshold. For example,
    the `parameters` dict can contain the time constraint `start` mapped to a parameter
    cube that contains yearly values for the start of the growing season. The data in
    the parameter cube is then used to create a mask which masks all days before the
    start of the growing season for each matching year. This will excludes these days
    from the index computation.

    Parameters
    ----------
    input_cubes : dict[str, iris.cube.Cube]
        Dictionary with mapping of input data and cubes from input data files.
    parameters : dict[str, iris.cube.Cube]
        Dictionary with mapping of time constraint and cubes from parameter files.
        The time constraint must be either `start` or `end`.

    Returns
    -------
    list[iris.coords.AuxCoord]
        A list with auxiliary coordinates describing the masking process.
    """
    for input_cube in input_cubes.values():
        aux_coords = []
        res = da.zeros(input_cube.shape, dtype=np.float32)
        for time_constraint, parameter_cube in parameters.items():
            assert time_constraint == "start" or time_constraint == "end", (
                f"Invalid time constraint <{time_constraint}> must be either `start` or"
                "`end`."
            )
            res, params = _mask_data(input_cube, parameter_cube, time_constraint)
            input_cube.data = res
            aux_coord = iris.coords.AuxCoord(
                params,
                var_name=f"mask-{time_constraint}",
                long_name="Day-of-year for which data have been masked.",
                units=Unit("day"),
            )
            aux_coords.append(aux_coord)
    return aux_coords


class IndexFunction:
    def __init__(self, standard_name=None, units=Unit("no_unit")):
        super().__init__()
        self.standard_name = standard_name
        self.units = units
        self.extra_coords = []

    def preprocess(self, cubes, client):
        pass

    def prepare(self, input_cubes, *args, **kwargs):
        pass

    def pre_aggregate_shape(self, *args, **kwargs):
        return ()


class ThresholdMixin:
    def __init__(self, threshold, condition, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.threshold = threshold
        self.condition = NUMPY_OPERATORS[condition]
        self.lazy_condition = DASK_OPERATORS[condition]
        self.extra_coords.append(threshold.copy())

    def prepare(self, input_cubes, parameters=None):
        ref_cube = next(iter(input_cubes.values()))
        threshold = self.threshold
        threshold.points = threshold.points.astype(ref_cube.dtype)
        if threshold.has_bounds():
            threshold.bounds = threshold.bounds.astype(ref_cube.dtype)
        gordias.util.units.change_units(
            threshold, ref_cube.units, ref_cube.standard_name
        )
        super().prepare(input_cubes)


class ReducerMixin:
    def __init__(self, reducer, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reducer = NUMPY_REDUCERS[reducer]
        self.lazy_reducer = DASK_REDUCERS[reducer]
        self.scalar_reducer = SCALAR_REDUCERS[reducer]


class RollingWindowMixin:
    def __init__(self, rolling_aggregator, window_size, reducer, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reducer = NUMPY_REDUCERS[reducer]
        self.lazy_reducer = DASK_REDUCERS[reducer]
        self.window_size = window_size
        self.rolling_aggregator = NUMPY_REDUCERS[rolling_aggregator]
        self.lazy_rolling_aggregator = DASK_REDUCERS[rolling_aggregator]
