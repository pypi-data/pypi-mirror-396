from cf_units import Unit
import dask.array as da
import numpy as np
import iris.coords

from .spell_kernels import make_first_spell_kernels, make_spell_length_kernels
from .support import (
    normalize_axis,
    IndexFunction,
    ThresholdMixin,
    ReducerMixin,
    DASK_OPERATORS,
)
from ..dask_take_along_axis import dask_take_along_axis

import gordias.dask_setup
import gordias.util.units

DASK_ARG_REDUCER = {
    "max": da.argmax,
    "min": da.argmin,
}


class FirstSpell(IndexFunction):
    def __init__(self, params):
        super().__init__(units=Unit("days"))
        self.params = params
        self.start_duration = self.params[0][2]
        if len(self.params) > 1:
            self.end_duration = self.params[1][2]
        else:
            self.end_duration = self.start_duration
        self.kernel = make_first_spell_kernels()

    def prepare(self, input_cubes, parameters=None):
        props = {
            (name, cube.dtype, cube.units, cube.standard_name)
            for name, cube in input_cubes.items()
        }
        for _, dtype, units, standard_name in props:
            for args in self.params:
                threshold = args[0]
                threshold.points = threshold.points.astype(dtype)
                if threshold.has_bounds():
                    threshold.bounds = threshold.bounds.astype(dtype)
                gordias.util.units.change_units(threshold, units, standard_name)
        if parameters is not None:
            raise NotImplementedError(
                "Parameter files cannot be used with this index function."
            )
        super().prepare(input_cubes)

    def pre_aggregate_shape(self, *args, **kwargs):
        return (4,)

    def call_func(self, data, axis, **kwargs):
        raise NotImplementedError

    def lazy_func(self, data, axis, cube, client, **kwargs):
        axis = normalize_axis(axis, data.ndim)
        mask = da.ma.getmaskarray(data).any(axis=axis)
        data = da.moveaxis(data, axis, -1)
        length = data.shape[-1]
        time = da.arange(length, dtype=np.float32)
        output_dim = data.ndim
        output_shape = 6  # length, head_chunk, res, tail_chunk, head_yr, tail_yr
        res_dim = output_dim + 1
        res_shape = 3  # start, end_independent, end_dependent
        data_idx = tuple(range(data.ndim))
        time_dim = data.ndim - 1
        time_idx = (time_dim,)
        output_idx = time_idx + data_idx[:-1] + (output_dim, res_dim)
        # divides data into chunks and looks for start and end spells for each chunk
        spell_res = da.blockwise(
            self.find_spell,
            output_idx,
            data,
            data_idx,
            time,
            time_idx,
            length=length,
            adjust_chunks={
                time_dim: lambda n: 1,
            },
            new_axes={
                output_dim: output_shape,
                res_dim: res_shape,
            },
            meta=np.array((), dtype=np.float32),
        )
        # reduces all chunks to one result by merging chunks in three steps
        res = client.persist(
            da.reduction(
                spell_res,
                self.chunk,
                self.aggregate,
                combine=self.combine,
                axis=0,
                keepdims=True,
                concatenate=True,
                split_every=4,
                dtype=np.float32,
                meta=np.array((), dtype=np.float32),
            )
        )
        gordias.dask_setup.progress(res)
        res = res[0]
        masked = da.ma.masked_array(
            da.ma.getdata(res),
            da.broadcast_to(mask[..., np.newaxis, np.newaxis], res.shape),
        )
        return masked[..., :2].astype(np.float32)

    def find_spell(self, chunk, time, length):
        """Calculate first spell information for a chunk of data.

        Parameters
        ----------
        chunk : da.array
            dask array containing one chunk of data
        time :  da.array
            dask array containing the time index for the chunked data
        length : int
            the length of the total data

        Returns
        -------
        da.array
            output dimensions : (1, n_long, n_lat, 6, 3)
            for each gridcell in the chunk returns 6x3 values:
            3 values:
            - start
            - end independent
            - end dependent
            6 values:
            - length of chunk
            - length of spell at beginning
            - position of first spell in the timeseries
            - length of spell at the end
            - length of spell at the beginning of the yr
            - length of the spell at the end of the yr
        """

        def _first_spell(chunk_data, chunk_time, args, leap_year=0):
            threshold, condition, duration, delay = args
            if delay > 59:
                delay += leap_year
            offset = np.where(delay <= chunk_time, True, False)
            thresholded_data = condition(chunk_data, threshold.points)
            thresholded_data = np.ma.filled(thresholded_data, fill_value=False)
            chunk_res = self.kernel.chunk(
                thresholded_data, offset, chunk_time, length, duration
            )
            return chunk_res

        stack = []
        leap_year = 0
        if length == 366:
            leap_year = 1
        # finds the independent start and end spells given conditions
        for args in self.params:
            chunk_res = _first_spell(chunk, time, args, leap_year)
            stack.append(chunk_res)
        # if there is no conditions given for the end
        if len(self.params) == 1:
            no_end = np.full(
                chunk.shape[:-1] + (6,), fill_value=np.nan, dtype=np.float32
            )
            stack.extend([no_end, no_end])
        else:
            end_dependent = stack[1].copy()
            start = stack[0][..., 2]
            cond = da.greater_equal(start, end_dependent[..., 2])
            for ind in np.ndindex(chunk.shape[:-1]):
                # if the start is before the end
                # compute a new dependent end with the start as offset
                if cond[ind]:
                    start_offset = int(time[0]) + start[ind] + 1
                    end_params = self.params[1][:-1] + (start_offset,)
                    chunk_res = _first_spell(chunk[ind], time, end_params)
                    end_dependent[ind] = chunk_res
            stack.append(end_dependent)
        res = da.stack(stack, axis=-1)
        return res.reshape((1,) + res.shape)

    def chunk(self, x_chunk, axis, keepdims, computing_meta=False):
        if computing_meta:
            return np.array((), dtype=np.float32)
        return x_chunk

    def combine(self, x_chunk, axis, keepdims):
        res = self.kernel.combine(
            np.array(x_chunk), self.start_duration, self.end_duration
        )
        return res.reshape((1,) + res.shape)

    def aggregate(self, x_chunk, axis, keepdims):
        res = self.kernel.combine(
            np.array(x_chunk), self.start_duration, self.end_duration
        )
        res = self.kernel.aggregate(res)
        return res.reshape((1,) + res.shape)

    def post_process(self, cube, chunk_data, coords, period, **kwargs):
        def _fuse(current_chunk, next_chunk):
            res = current_chunk.copy()
            for ind in np.ndindex(current_chunk.shape[:2]):
                ind_length = ind + (0, 0)
                ind_start_index = ind + (2, 0)
                ind_start_tail = ind + (5, 0)
                ind_end_index = ind + (2, 1)
                ind_end_tail = ind + (5, 1)
                ind_next_start_head = ind + (4, 0)
                ind_next_end_head = ind + (4, 1)
                # if no start have been found check if there is a start
                # at the end of the year
                if da.isnan(current_chunk[ind_start_index]):
                    start_spell = (
                        current_chunk[ind_start_tail] + next_chunk[ind_next_start_head]
                    )
                    # if there is a start
                    if start_spell >= self.start_duration:
                        res[ind_start_index] = (
                            current_chunk[ind_length]
                            - current_chunk[ind_start_tail]
                            + 1
                        )
                        end_tail = current_chunk[ind_end_tail]
                        # if the end tail is larger or equal to the start tail
                        # reduce the end tail
                        if current_chunk[ind_end_tail] >= current_chunk[ind_start_tail]:
                            end_tail = current_chunk[ind_start_tail] - 1
                        end_spell = end_tail + next_chunk[ind_next_end_head]
                        # if we have conditions for finding a end
                        if not da.isnan(end_spell):
                            # if there is a end after the start
                            if end_spell >= self.end_duration:
                                res[ind_end_index] = (
                                    current_chunk[ind_length] - end_tail + 1
                                )
                            # if the start is at the end of the year
                            # the end is not possible
                            elif res[ind_start_index] == current_chunk[ind_length]:
                                res[ind_end_index] = np.nan
                            # if there is no end found
                            # the end is set to be the end of the year
                            else:
                                res[ind_end_index] = current_chunk[ind_length]
                else:
                    # if there is a start but no end have been found
                    if da.isnan(current_chunk[ind_end_index]):
                        end_spell = (
                            current_chunk[ind_end_tail] + next_chunk[ind_next_end_head]
                        )
                        # if we have conditions for finding a end
                        if not da.isnan(end_spell):
                            # if there is a end
                            if end_spell >= self.end_duration:
                                res[ind_end_index] = (
                                    current_chunk[ind_length]
                                    - current_chunk[ind_end_tail]
                                    + 1
                                )
                            # if there is no end found
                            # the end is set to be the end of the year
                            else:
                                res[ind_end_index] = current_chunk[ind_length]
            return res

        mask = da.ma.getmaskarray(chunk_data)
        stack = []
        # start with the first year
        this = da.ma.getdata(chunk_data[(0,)]).rechunk(-1)
        tmp_res = da.empty(this.shape, dtype=np.float32)
        # add a year containing only zeros at the end for padding
        padding_chunk = da.zeros((1,) + this.shape, dtype=np.float32)
        padded_data = da.concatenate(
            [da.ma.getdata(chunk_data), padding_chunk], axis=0
        ).rechunk(-1)
        # for each year check if either the start or the end can be found in the overlap
        for next_chunk in padded_data[1:]:
            tmp_res = da.blockwise(
                _fuse,
                (0, 1, 2, 3),
                this,
                (0, 1, 2, 3),
                next_chunk,
                (0, 1, 2, 3),
                meta=np.array((), dtype=np.float32),
                align_arrays=False,
            )
            stack.append(tmp_res)
            this = next_chunk
        res_chunk = da.stack(stack, axis=0)
        masked_res = da.ma.masked_array(res_chunk, mask)
        return masked_res


class SeasonStart(FirstSpell):
    def __init__(self, **params):
        args = [
            (
                params["threshold"],
                DASK_OPERATORS[params["condition"]],
                params["duration"].points[0],
                params["delay"].points[0],
            )
        ]
        super().__init__(args)

    def lazy_func(self, data, axis, **kwargs):
        res = super().lazy_func(data, axis, **kwargs)
        return res

    def post_process(self, cube, data, coords, period, **kwargs):
        res = super().post_process(cube, data, coords, period, **kwargs)
        start = res[..., 0]
        return cube, start[..., 2].astype(np.float32)


class SeasonEnd(FirstSpell):
    def __init__(self, **params):
        args = [
            (
                params["start_threshold"],
                DASK_OPERATORS[params["start_condition"]],
                params["start_duration"].points[0],
                params["start_delay"].points[0],
            ),
            (
                params["end_threshold"],
                DASK_OPERATORS[params["end_condition"]],
                params["end_duration"].points[0],
                params["end_delay"].points[0],
            ),
        ]
        super().__init__(args)

    def lazy_func(self, data, axis, **kwargs):
        res = super().lazy_func(data, axis, **kwargs)
        return res

    def post_process(self, cube, data, coords, period, **kwargs):
        res = super().post_process(cube, data, coords, period, **kwargs)
        end = res[..., 1]
        return cube, end[..., 2].astype(np.float32)


class SeasonLength(FirstSpell):
    def __init__(self, **params):
        args = [
            (
                params["start_threshold"],
                DASK_OPERATORS[params["start_condition"]],
                params["start_duration"].points[0],
                params["start_delay"].points[0],
            ),
            (
                params["end_threshold"],
                DASK_OPERATORS[params["end_condition"]],
                params["end_duration"].points[0],
                params["end_delay"].points[0],
            ),
        ]
        super().__init__(args)

    def lazy_func(self, data, axis, **kwargs):
        res = super().lazy_func(data, axis, **kwargs)
        return res

    def post_process(self, cube, data, coords, period, **kwargs):
        res = super().post_process(cube, data, coords, period, **kwargs)
        start = res[..., 0]
        end = res[..., 1]
        length = end[..., 2] - start[..., 2] + 1
        length = da.ma.where(np.isnan(length), 0, length)
        return cube, length.astype(np.float32)


class StartOfSpring(SeasonStart):
    def __init__(self, **params):
        super().__init__(**params)
        self.leap_years = []

    def lazy_func(self, data, axis, **kwargs):
        res = super().lazy_func(data, axis, **kwargs)
        if data.shape[0] > 365:
            self.leap_years.append(1)
        else:
            self.leap_years.append(0)
        return res

    def post_process(self, cube, data, coords, period, **kwargs):
        _, res = super().post_process(cube, data, coords, period, **kwargs)
        start = res.copy()
        assert len(self.leap_years) > 0
        for year, leap in enumerate(self.leap_years):
            start[year] = da.where(res[year] > (212 + leap), np.nan, res[year])
        return cube, start.astype(np.float32)


class StartOfWinter(IndexFunction):
    def __init__(self, **params):
        super().__init__(units=Unit("days"))
        spring_args = {
            k.replace("spring_start_", ""): v
            for k, v in params.items()
            if "spring_start" in k
        }
        winter_args = {
            k.replace("winter_start_", ""): v
            for k, v in params.items()
            if "winter_start" in k
        }
        self.spring = StartOfSpring(**spring_args)
        self.winter = SeasonStart(**winter_args)
        self.leap_years = []

    def prepare(self, input_cubes, parameters=None):
        if parameters is not None:
            raise NotImplementedError(
                "Parameter files cannot be used with this index function."
            )
        self.spring.prepare(input_cubes, parameters)
        self.winter.prepare(input_cubes, parameters)
        super().prepare(input_cubes)
        ref_cube = next(iter(input_cubes.values()))
        self.standard_name = ref_cube.standard_name

    def pre_aggregate_shape(self, *args, **kwargs):
        return (4,)

    def call_func(self, data, axis, **kwargs):
        raise NotImplementedError

    def lazy_func(self, data, axis, **kwargs):
        spring_starts = self.spring.lazy_func(data, axis, **kwargs)
        winter_starts = self.winter.lazy_func(data, axis, **kwargs)
        res = da.stack([spring_starts, winter_starts], axis=-1)
        if data.shape[0] > 273:
            self.leap_years.append(1)
        else:
            self.leap_years.append(0)
        return res

    def post_process(self, cube, data, coords, period, **kwargs):
        _, spring_starts = self.spring.post_process(
            cube, data[..., 0], coords, period, **kwargs
        )
        _, winter_starts = self.winter.post_process(
            cube, data[..., 1], coords, period, **kwargs
        )
        start = winter_starts.copy()
        start = da.where(spring_starts > winter_starts, np.nan, start)
        assert len(self.leap_years) > 0
        for year, leap in enumerate(self.leap_years):
            start[year] = da.where(
                winter_starts[year] > (243 + leap), np.nan, winter_starts[year]
            )
        start -= 153
        return cube, start.astype(np.float32)


class StartOfSummer(IndexFunction):
    def __init__(self, **params):
        super().__init__(units=Unit("days"))
        spring_args = {
            k.replace("spring_start_", ""): v
            for k, v in params.items()
            if "spring_start" in k
        }
        summer_args = {
            k.replace("spring_", ""): v for k, v in params.items() if "spring" in k
        }
        autumn_args = {
            k.replace("autumn_start_", ""): v
            for k, v in params.items()
            if "autumn_start" in k
        }
        self.spring = StartOfSpring(**spring_args)
        self.summer = SeasonEnd(**summer_args)
        self.autumn = SeasonStart(**autumn_args)
        self.leap_years = []

    def prepare(self, input_cubes, parameters=None):
        if parameters is not None:
            raise NotImplementedError(
                "Parameter files cannot be used with this index function."
            )
        self.spring.prepare(input_cubes, parameters)
        self.summer.prepare(input_cubes, parameters)
        self.autumn.prepare(input_cubes, parameters)
        super().prepare(input_cubes)
        ref_cube = next(iter(input_cubes.values()))
        self.standard_name = ref_cube.standard_name

    def pre_aggregate_shape(self, *args, **kwargs):
        return (4,)

    def call_func(self, data, axis, **kwargs):
        raise NotImplementedError

    def lazy_func(self, data, axis, **kwargs):
        summer_starts = self.summer.lazy_func(data, axis, **kwargs)
        spring_starts = self.spring.lazy_func(data, axis, **kwargs)
        autumn_starts = self.autumn.lazy_func(data, axis, **kwargs)
        res = da.stack([summer_starts, spring_starts, autumn_starts], axis=-1)
        if data.shape[0] > 365:
            self.leap_years.append(1)
        else:
            self.leap_years.append(0)
        return res

    def post_process(self, cube, data, coords, period, **kwargs):
        _, summer_starts = self.summer.post_process(
            cube, data[..., 0], coords, period, **kwargs
        )
        _, spring_starts = self.spring.post_process(
            cube, data[..., 1], coords, period, **kwargs
        )
        _, autumn_starts = self.autumn.post_process(
            cube, data[..., 2], coords, period, **kwargs
        )
        start = summer_starts.copy()
        start = da.where(start >= autumn_starts, np.nan, summer_starts)
        start = da.where(np.isnan(spring_starts), np.nan, start)
        assert len(self.leap_years) > 0
        for year, leap in enumerate(self.leap_years):
            start[year] = da.where(start[year] > (304 + leap), np.nan, start[year])
        return cube, start.astype(np.float32)


class SpellLength(ThresholdMixin, ReducerMixin, IndexFunction):
    def __init__(self, threshold, condition, statistic, fuse_periods=False):
        super().__init__(threshold, condition, statistic, units=Unit("days"))
        self.spanning_spells = True
        self.kernels = make_spell_length_kernels(self.scalar_reducer)
        self.fuse_periods = fuse_periods
        self.lazy_arg_reducer = DASK_ARG_REDUCER[statistic]

    def prepare(self, input_cubes, parameters=None):
        if parameters is not None:
            raise NotImplementedError(
                "Parameter files cannot be used with this index function."
            )
        super().prepare(input_cubes)

    def pre_aggregate_shape(self, *args, **kwargs):
        return (4,)

    def call_func(self, data, axis, **kwargs):
        raise NotImplementedError

    def lazy_func(self, data, axis, **kwargs):
        axis = normalize_axis(axis, data.ndim)
        mask = da.ma.getmaskarray(data).any(axis=axis)
        data = da.moveaxis(data, axis, -1)
        res = da.reduction(
            data,
            self.chunk,
            self.aggregate,
            keepdims=True,
            output_size=7,
            axis=-1,
            dtype=np.float32,
            concatenate=False,
            meta=np.array((), dtype=np.float32),
        )
        res = da.ma.masked_array(
            da.ma.getdata(res), np.broadcast_to(mask[..., np.newaxis], res.shape)
        )
        return res.astype("float32")

    def chunk(self, raw_data, axis, keepdims, computing_meta=False):
        if computing_meta:
            return np.array((), dtype=int)

        data = self.condition(raw_data, self.threshold.points)
        data = np.ma.filled(data, fill_value=False)
        chunk_res = self.kernels.chunk(data)
        return chunk_res

    def aggregate(self, x_chunk, axis, keepdims):
        if not isinstance(x_chunk, list):
            return x_chunk
        res = self.kernels.aggregate(np.array(x_chunk))
        return res

    def post_process(self, cube, data, coords, period, **kwargs):
        def fuse(this, previous_tail):
            own_mask = da.ma.getmaskarray(this[..., 0])
            own_length = this[..., 0]
            own_head = this[..., 1]
            internal = this[..., 2]
            own_tail = this[..., 3]
            head = da.where(own_head, previous_tail + own_head, 0.0)
            tail = da.where(own_length == own_head, previous_tail + own_tail, own_tail)
            stack = da.stack([head, internal, tail], axis=-1)
            spell_length = da.ma.masked_array(
                self.lazy_reducer(stack, axis=-1), own_mask
            )
            return spell_length, tail

        if self.fuse_periods and len(data) > 1:
            stack = []
            this = data[0]
            slice_shape = this.shape[:-1]
            previous_tail = da.ma.masked_array(
                da.zeros(slice_shape, dtype=np.float32),
                da.ma.getmaskarray(data[0, ..., 3]),
            )

            for next_chunk in data[1:]:
                spell_length, previous_tail = fuse(this, previous_tail)
                stack.append(spell_length)
                this = next_chunk

            stack.append(fuse(next_chunk, previous_tail)[0])
            res_data = da.stack(stack, axis=0)
        else:
            res_data = self.lazy_reducer(data[..., 1:4], axis=-1)
            mask = da.ma.getmaskarray(res_data)
            res_ind = self.lazy_arg_reducer(data[..., 1:4], keepdims=True, axis=-1)
            spell_beginning = dask_take_along_axis(
                data[..., 4:], res_ind, axis=-1
            ).reshape(res_data.shape)
            masked_spell_beginning = da.ma.masked_array(spell_beginning, mask).squeeze()
            aux_coord = iris.coords.AuxCoord(
                masked_spell_beginning,
                var_name="spell_beginning",
                long_name="Day-of-year when longest spell begins",
                units=Unit("day"),
            )
            self.extra_coords.append(aux_coord)
        return cube, res_data
