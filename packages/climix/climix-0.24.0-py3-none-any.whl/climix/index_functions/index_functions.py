# -*- coding: utf-8 -*-

from datetime import datetime

from cf_units import Unit
import dask.array as da
import numpy as np

from .support import (
    mask_data_from_parameters,
    normalize_axis,
    IndexFunction,
    ThresholdMixin,
    ReducerMixin,
    RollingWindowMixin,
    DASK_OPERATORS,
)
import gordias.util.units


class CountLevelCrossings(IndexFunction):
    def __init__(self, threshold):
        super().__init__(units=Unit("1"))
        self.threshold = threshold
        self.extra_coords.append(threshold.copy())

    def prepare(self, input_cubes, parameters=None):
        props = {
            (cube.dtype, cube.units, cube.standard_name)
            for cube in input_cubes.values()
        }
        assert len(props) == 1
        dtype, units, standard_name = props.pop()
        threshold = self.threshold
        threshold.points = threshold.points.astype(dtype)
        if threshold.has_bounds():
            threshold.bounds = threshold.bounds.astype(dtype)
        gordias.util.units.change_units(threshold, units, standard_name)
        if parameters is not None:
            aux_coords = mask_data_from_parameters(input_cubes, parameters)
            self.extra_coords.extend(aux_coords)
        super().prepare(input_cubes)

    def call_func(self, data, axis, **kwargs):
        cond = da.logical_and(
            data["low_data"] < self.threshold.points,
            self.threshold.points < data["high_data"],
        )
        res = np.count_nonzero(cond, axis=axis)
        return res.astype("float32")

    lazy_func = call_func


class CountOccurrences(ThresholdMixin, IndexFunction):
    def __init__(self, threshold, condition):
        super().__init__(threshold, condition, units=Unit("1"))

    def prepare(self, input_cubes, parameters=None):
        if parameters is not None:
            aux_coords = mask_data_from_parameters(input_cubes, parameters)
            self.extra_coords.extend(aux_coords)
        super().prepare(input_cubes)

    def call_func(self, data, axis, **kwargs):
        axis = normalize_axis(axis, data.ndim)
        cond = self.condition(data, self.threshold.points)
        res = np.count_nonzero(cond, axis=axis)
        return res.astype("float32")

    def lazy_func(self, data, axis, **kwargs):
        axis = normalize_axis(axis, data.ndim)
        cond = self.lazy_condition(data, self.threshold.points)
        res = da.count_nonzero(cond, axis=axis)
        return res.astype("float32")


class DiurnalTemperatureRange(ReducerMixin, IndexFunction):
    def __init__(self, statistic="mean"):
        super().__init__(statistic, units=Unit("degree_Celsius"))

    def prepare(self, input_cubes, parameters=None):
        props = {
            (cube.dtype, cube.units, cube.standard_name)
            for cube in input_cubes.values()
        }
        assert len(props) == 1
        dtype, units, standard_name = props.pop()
        assert units.is_convertible(Unit("degree_Celsius"))
        if parameters is not None:
            aux_coords = mask_data_from_parameters(input_cubes, parameters)
            self.extra_coords.extend(aux_coords)
        super().prepare(input_cubes)

    def call_func(self, data, axis, **kwargs):
        res = self.reducer(data["high_data"] - data["low_data"], axis=axis)
        return res.astype("float32")

    def lazy_func(self, data, axis, **kwargs):
        res = self.lazy_reducer(data["high_data"] - data["low_data"], axis=axis)
        return res.astype("float32")


class ExtremeTemperatureRange(IndexFunction):
    def __init__(self):
        super().__init__(units=Unit("degree_Celsius"))

    def prepare(self, input_cubes, parameters=None):
        props = {
            (cube.dtype, cube.units, cube.standard_name)
            for cube in input_cubes.values()
        }
        assert len(props) == 1
        dtype, units, standard_name = props.pop()
        assert units.is_convertible(Unit("degree_Celsius"))
        if parameters is not None:
            aux_coords = mask_data_from_parameters(input_cubes, parameters)
            self.extra_coords.extend(aux_coords)
        super().prepare(input_cubes)

    def call_func(self, data, axis, **kwargs):
        res = data["high_data"].max(axis=axis) - data["low_data"].min(axis=axis)
        return res.astype("float32")

    lazy_func = call_func


class FirstOccurrence(ThresholdMixin, IndexFunction):
    def __init__(self, threshold, condition):
        super().__init__(threshold, condition, units=Unit("days"))

    def prepare(self, input_cubes, parameters=None):
        if parameters is not None:
            raise NotImplementedError(
                "Parameter files cannot be used with this index function."
            )
        super().prepare(input_cubes)

    def call_func(self, data, axis, **kwargs):
        axis = normalize_axis(axis, data.ndim)
        mask = np.ma.getmaskarray(data).any(axis=axis)
        cond = self.condition(data, self.threshold.points)
        res = np.where(cond.any(axis=axis), cond.argmax(axis=axis), np.nan)
        res = np.ma.masked_array(np.ma.getdata(res), mask)
        res = np.ma.masked_invalid(res)
        return res.astype("float32")

    def lazy_func(self, data, axis, **kwargs):
        axis = normalize_axis(axis, data.ndim)
        mask = da.ma.getmaskarray(data).any(axis=axis)
        cond = self.lazy_condition(data, self.threshold.points)
        res = da.where(cond.any(axis=axis), cond.argmax(axis=axis), np.nan)
        res = da.ma.masked_array(da.ma.getdata(res), mask)
        res = da.ma.masked_invalid(res)
        return res.astype("float32")

    def post_process(self, cube, data, coords, period, **kwargs):
        time = cube.coord("time")
        calendar = time.units.calendar
        offsets = np.empty_like(time.points, dtype=data.dtype)
        for i, representative_date in enumerate(time.cells()):
            year = representative_date.point.year
            start_date = datetime(year, period.first_month_number, 1)
            units = Unit(f"days since {year}-01-01", calendar=calendar)
            offsets[i] = units.date2num(start_date)
        result_data = data + offsets[:, None, None]
        return cube, result_data


class InterdayDiurnalTemperatureRange(IndexFunction):
    def __init__(self):
        super().__init__(units=Unit("degree_Celsius"))

    def prepare(self, input_cubes, parameters=None):
        props = {
            (cube.dtype, cube.units, cube.standard_name)
            for cube in input_cubes.values()
        }
        assert len(props) == 1
        dtype, units, standard_name = props.pop()
        assert units.is_convertible(Unit("degree_Celsius"))
        if parameters is not None:
            aux_coords = mask_data_from_parameters(input_cubes, parameters)
            self.extra_coords.extend(aux_coords)
        super().prepare(input_cubes)

    def call_func(self, data, axis, **kwargs):
        res = np.absolute(
            np.diff(data["high_data"] - data["low_data"], axis=axis)
        ).mean(axis=axis)
        return res.astype("float32")

    def lazy_func(self, data, axis, **kwargs):
        res = da.absolute(
            da.diff(data["high_data"] - data["low_data"], axis=axis)
        ).mean(axis=axis)
        return res.astype("float32")


class LastOccurrence(ThresholdMixin, IndexFunction):
    def __init__(self, threshold, condition):
        super().__init__(threshold, condition, units=Unit("days"))

    def prepare(self, input_cubes, parameters=None):
        if parameters is not None:
            raise NotImplementedError(
                "Parameter files cannot be used with this index function."
            )
        super().prepare(input_cubes)

    def call_func(self, data, axis, **kwargs):
        axis = normalize_axis(axis, data.ndim)
        mask = np.ma.getmaskarray(data).any(axis=axis)
        cond = self.condition(np.flip(data, axis=axis), self.threshold.points)
        ndays = data.shape[axis]
        res = np.where(cond.any(axis=axis), ndays - cond.argmax(axis=axis), np.nan)
        res = np.ma.masked_array(np.ma.getdata(res), mask)
        res = np.ma.masked_invalid(res)
        return res.astype("float32")

    def lazy_func(self, data, axis, **kwargs):
        axis = normalize_axis(axis, data.ndim)
        mask = da.ma.getmaskarray(data).any(axis=axis)
        cond = self.lazy_condition(da.flip(data, axis), self.threshold.points)
        ndays = data.shape[axis]
        res = da.where(cond.any(axis=axis), ndays - cond.argmax(axis=axis), np.nan)
        res = da.ma.masked_array(da.ma.getdata(res), mask)
        res = da.ma.masked_invalid(res)
        return res.astype("float32")

    def post_process(self, cube, data, coords, period, **kwargs):
        time = cube.coord("time")
        calendar = time.units.calendar
        offsets = np.empty_like(time.points, dtype=data.dtype)
        for i, representative_date in enumerate(time.cells()):
            year = representative_date.point.year
            start_date = datetime(year, period.first_month_number, 1)
            units = Unit(f"days since {year}-01-01", calendar=calendar)
            offsets[i] = units.date2num(start_date)
        result_data = data + offsets[:, None, None]
        return cube, result_data


class Percentile(IndexFunction):
    def __init__(self, percentiles, method="linear"):
        super().__init__()
        self.percentiles = percentiles
        assert np.all(self.percentiles.points > 0)
        assert np.all(self.percentiles.points < 100)
        self.method = method

    def prepare(self, input_cubes, parameters=None):
        super().prepare(input_cubes)
        ref_cube = next(iter(input_cubes.values()))
        self.standard_name = ref_cube.standard_name
        self.units = ref_cube.units
        if parameters is not None:
            raise NotImplementedError(
                "Parameter files cannot be used with this index function."
            )

    def call_func(self, data, axis, **kwargs):
        axis = normalize_axis(axis, data.ndim)
        mask = np.ma.getmaskarray(data).any(axis=axis)
        filled = np.ma.filled(data, fill_value=np.nan)
        res = np.nanpercentile(
            filled, q=self.percentiles.points, axis=axis, method=self.method
        ).squeeze()
        res = np.ma.masked_array(np.ma.getdata(res), mask)
        res = np.ma.masked_where(np.isnan(res), res)
        return res.astype("float32")

    def lazy_func(self, data, axis, **kwargs):
        axis = normalize_axis(axis, data.ndim)
        mask = da.ma.getmaskarray(data).any(axis=axis)
        filled = da.ma.filled(data, fill_value=np.nan)

        def percentile(arr):
            return np.nanpercentile(arr, q=self.percentiles.points, method=self.method)

        res = da.apply_along_axis(percentile, axis=axis, arr=filled).squeeze()
        res = da.ma.masked_array(da.ma.getdata(res), mask)
        res = da.ma.masked_where(da.isnan(res), res)
        return res.astype("float32")


class Statistics(ReducerMixin, IndexFunction):
    def __init__(self, statistic):
        super().__init__(statistic)

    def prepare(self, input_cubes, parameters=None):
        super().prepare(input_cubes)
        ref_cube = next(iter(input_cubes.values()))
        self.standard_name = ref_cube.standard_name
        self.units = ref_cube.units
        if parameters is not None:
            aux_coords = mask_data_from_parameters(input_cubes, parameters)
            self.extra_coords.extend(aux_coords)

    def call_func(self, data, axis, **kwargs):
        axis = normalize_axis(axis, data.ndim)
        res = self.reducer(data, axis=axis)
        return res.astype("float32")

    def lazy_func(self, data, axis, **kwargs):
        axis = normalize_axis(axis, data.ndim)
        res = self.lazy_reducer(data, axis=axis)
        return res.astype("float32")


class ThresholdedPercentile(ThresholdMixin, IndexFunction):
    def __init__(self, threshold, condition, percentiles, method="linear"):
        super().__init__(threshold, condition)
        self.percentiles = percentiles
        assert np.all(self.percentiles.points > 0)
        assert np.all(self.percentiles.points < 100)
        self.method = method

    def prepare(self, input_cubes, parameters=None):
        super().prepare(input_cubes)
        ref_cube = next(iter(input_cubes.values()))
        self.standard_name = ref_cube.standard_name
        self.units = ref_cube.units
        if parameters is not None:
            raise NotImplementedError(
                "Parameter files cannot be used with this index function."
            )

    def call_func(self, data, axis, **kwargs):
        axis = normalize_axis(axis, data.ndim)
        mask = np.ma.getmaskarray(data).any(axis=axis)
        cond = self.condition(data, self.threshold.points)
        masked = np.ma.masked_where(~cond, data)
        filled = np.ma.filled(masked, fill_value=np.nan)
        res = np.nanpercentile(
            filled,
            q=self.percentiles.points,
            axis=axis,
            method=self.method,
        ).squeeze()
        res = np.ma.masked_array(np.ma.getdata(res), mask)
        res = np.ma.masked_where(np.isnan(res), res)
        return res.astype("float32")

    def lazy_func(self, data, axis, **kwargs):
        axis = normalize_axis(axis, data.ndim)
        mask = da.ma.getmaskarray(data).any(axis=axis)
        cond = self.condition(data, self.threshold.points)
        masked = da.ma.masked_where(~cond, data)
        filled = da.ma.filled(masked, fill_value=np.nan)

        def percentile(arr):
            return np.nanpercentile(arr, q=self.percentiles.points, method=self.method)

        res = da.apply_along_axis(percentile, axis=axis, arr=filled).squeeze()
        res = da.ma.masked_array(da.ma.getdata(res), mask)
        res = da.ma.masked_where(da.isnan(res), res)
        return res.astype("float32")


class ThresholdedStatistics(ThresholdMixin, ReducerMixin, IndexFunction):
    def __init__(self, threshold, condition, statistic):
        super().__init__(threshold, condition, statistic, units=Unit("days"))

    def prepare(self, input_cubes, parameters=None):
        super().prepare(input_cubes)
        ref_cube = next(iter(input_cubes.values()))
        self.standard_name = ref_cube.standard_name
        self.units = ref_cube.units
        if parameters is not None:
            aux_coords = mask_data_from_parameters(input_cubes, parameters)
            self.extra_coords.extend(aux_coords)

    def call_func(self, data, axis, **kwargs):
        axis = normalize_axis(axis, data.ndim)
        comb = self.condition(data, self.threshold.points)
        res = self.reducer(np.ma.masked_where(~comb, data), axis=axis)
        return res.astype("float32")

    def lazy_func(self, data, axis, **kwargs):
        axis = normalize_axis(axis, data.ndim)
        comb = self.lazy_condition(data, self.threshold.points)
        res = self.lazy_reducer(da.ma.masked_where(~comb, data), axis=axis)
        return res.astype("float32")


class RunningStatistics(RollingWindowMixin, IndexFunction):
    def __init__(self, rolling_aggregator, window_size, overall_statistic):
        super().__init__(rolling_aggregator, window_size, overall_statistic)
        self.fuse_periods = True
        self.bandwidth = self.window_size.points[0] // 2
        self.tail_overlap = self.window_size.points[0] - 1
        self.head_overlap = self.tail_overlap + self.window_size.points[0] % 2

    def prepare(self, input_cubes, parameters=None):
        super().prepare(input_cubes)
        ref_cube = next(iter(input_cubes.values()))
        self.standard_name = ref_cube.standard_name
        self.units = ref_cube.units
        if parameters is not None:
            raise NotImplementedError(
                "Parameter files cannot be used with this index function."
            )

    def pre_aggregate_shape(self, *args, **kwargs):
        return (self.head_overlap + self.tail_overlap + 1,)

    def call_func(self, data, axis, **kwargs):
        axis = normalize_axis(axis, data.ndim)
        mask = np.ma.getmaskarray(data).any(axis=axis)
        rolling_view = np.lib.stride_tricks.sliding_window_view(
            data, self.window_size.points, axis
        )
        aggregated = self.rolling_aggregator(rolling_view, -1)
        reduced = self.reducer(aggregated, axis=axis)
        masked = np.ma.masked_array(np.ma.getdata(reduced), mask)
        head_slices = (slice(None, None),) * axis + (slice(None, self.head_overlap),)
        head = np.moveaxis(data[head_slices], axis, -1)
        tail_slices = (slice(None, None),) * axis + (slice(-self.tail_overlap, None),)
        tail = np.moveaxis(data[tail_slices], axis, -1)
        res = np.ma.concatenate([head, masked[..., np.newaxis], tail], axis=-1)
        return res.astype("float32")

    def lazy_func(self, data, axis, **kwargs):
        axis = normalize_axis(axis, data.ndim)
        mask = da.ma.getmaskarray(data).any(axis=axis)
        rolling_view = da.overlap.sliding_window_view(
            data, self.window_size.points, axis
        )
        aggregated = self.lazy_rolling_aggregator(rolling_view, -1)
        reduced = self.lazy_reducer(aggregated, axis=axis)
        masked = da.ma.masked_array(da.ma.getdata(reduced), mask)
        head_slices = (slice(None, None),) * axis + (slice(None, self.head_overlap),)
        head = da.moveaxis(data[head_slices], axis, -1)
        tail_slices = (slice(None, None),) * axis + (slice(-self.tail_overlap, None),)
        tail = da.moveaxis(data[tail_slices], axis, -1)
        res = da.concatenate([head, masked[..., np.newaxis], tail], axis=-1)
        return res.astype("float32")

    def post_process(self, cube, data, coords, period, **kwargs):
        def _aggregate(tail, head):
            window_size = self.window_size.points
            overlap = da.concatenate([tail, head], axis=-1)
            rolling_view = da.overlap.sliding_window_view(overlap, window_size, -1)
            aggregated = self.lazy_rolling_aggregator(rolling_view, axis=-1)
            isnan = da.isnan(overlap)
            if isnan.any():
                rolling_isnan = da.overlap.sliding_window_view(isnan, window_size, -1)
                mask = da.any(rolling_isnan, axis=-1)
                aggregated = da.ma.masked_where(mask, aggregated)
            return aggregated

        def _get_strict_mask(head, pre_stat, tail):
            head_mask = da.ma.getmaskarray(head).any(axis=-1)
            pre_stat_mask = da.ma.getmaskarray(pre_stat)
            tail_mask = da.ma.getmaskarray(tail).any(axis=-1)
            strict_mask = head_mask | pre_stat_mask | tail_mask
            return strict_mask

        def fuse(this, previous_tail, next_head):
            head = this[..., : self.head_overlap]
            pre_statistic = this[..., self.head_overlap]
            tail = this[..., -self.tail_overlap :].copy()
            strict_mask = _get_strict_mask(next_head, pre_statistic, previous_tail)
            head_aggregated = _aggregate(previous_tail[..., -self.bandwidth :], head)
            tail_aggregated = _aggregate(tail, next_head[..., : self.bandwidth])
            concatenated = da.concatenate(
                [head_aggregated, pre_statistic[..., np.newaxis], tail_aggregated],
                axis=-1,
            )
            running_statistic = self.lazy_reducer(concatenated, axis=-1)
            masked = da.ma.masked_where(strict_mask, running_statistic)
            return masked, tail

        if self.fuse_periods and len(data) > 1:
            stack = []
            this = data[0]
            tail_shape = this.shape[:-1] + (self.tail_overlap,)
            previous_tail = da.full(tail_shape, fill_value=np.nan, dtype=np.float32)

            for next_chunk in data[1:]:
                next_head = next_chunk[..., : self.head_overlap].copy()
                running_statistic, previous_tail = fuse(this, previous_tail, next_head)
                stack.append(running_statistic)
                this = next_chunk

            head_shape = this.shape[:-1] + (self.head_overlap,)
            next_head = da.full(head_shape, fill_value=np.nan, dtype=np.float32)
            stack.append(fuse(next_chunk, previous_tail, next_head)[0])
            res_data = da.stack(stack, axis=0)
        else:
            stack = []
            for this in data:
                stack.append(this[..., self.head_overlap])
            res_data = da.stack(stack, axis=0)
        return cube, res_data


class ThresholdedRunningStatistics(ThresholdMixin, RunningStatistics):
    def __init__(
        self, threshold, condition, rolling_aggregator, window_size, overall_statistic
    ):
        super().__init__(
            threshold, condition, rolling_aggregator, window_size, overall_statistic
        )

    def call_func(self, data, axis, **kwargs):
        comb = self.condition(data, self.threshold.points)
        thresholded_data = np.ma.where(comb, data, 0.0)
        return super().call_func(thresholded_data, axis, **kwargs)

    def lazy_func(self, data, axis, **kwargs):
        comb = self.condition(data, self.threshold.points)
        thresholded_data = da.ma.where(comb, data, 0.0)
        return super().lazy_func(thresholded_data, axis, **kwargs)


class TemperatureSum(ThresholdMixin, IndexFunction):
    def __init__(self, threshold, condition):
        super().__init__(threshold, condition, units=Unit("days"))
        if condition in [">", ">="]:
            self.fun = lambda d, t: np.maximum(d - t, 0)
            self.lazy_fun = lambda d, t: da.maximum(d - t, 0)
        else:
            self.fun = lambda d, t: np.maximum(t - d, 0)
            self.lazy_fun = lambda d, t: da.maximum(t - d, 0)

    def prepare(self, input_cubes, parameters=None):
        super().prepare(input_cubes)
        ref_cube = next(iter(input_cubes.values()))
        self.standard_name = ref_cube.standard_name
        if ref_cube.units.is_convertible("degC"):
            self.units = "degC days"
        else:
            raise RuntimeError("Invalid input units")
        if parameters is not None:
            aux_coords = mask_data_from_parameters(input_cubes, parameters)
            self.extra_coords.extend(aux_coords)

    def call_func(self, data, axis, **kwargs):
        axis = normalize_axis(axis, data.ndim)
        threshold = self.threshold.points[0]
        res = np.sum(self.fun(data, threshold), axis=axis)
        return res.astype("float32")

    def lazy_func(self, data, axis, **kwargs):
        axis = normalize_axis(axis, data.ndim)
        threshold = self.threshold.points[0]
        res = da.sum(self.lazy_fun(data, threshold), axis=axis)
        return res.astype("float32")


class CountJointOccurrences(IndexFunction):
    def __init__(self, mapping):
        super().__init__(units=Unit("1"))
        self.mapping = mapping

    def add_extra_coords(self, input_cubes):
        thresholds = []
        for name, _ in input_cubes.items():
            for threshold, _ in self.mapping[name]:
                thresholds.append(threshold)
        if (
            thresholds[0].metadata.equal(thresholds[1].metadata, lenient=True)
            and thresholds[0].metadata.long_name == thresholds[1].metadata.long_name
        ):
            raise ValueError(
                "Auxiliary coordinates with the same metadata must have different "
                "<long_name>."
            )
        self.extra_coords.append(thresholds[0].copy())
        self.extra_coords.append(thresholds[1].copy())

    def prepare(self, input_cubes, parameters=None):
        self.add_extra_coords(input_cubes)
        props = {
            (name, cube.dtype, cube.units, cube.standard_name)
            for name, cube in input_cubes.items()
        }
        for data_name, dtype, units, standard_name in props:
            for threshold, _ in self.mapping[data_name]:
                threshold.points = threshold.points.astype(dtype)
                if threshold.has_bounds():
                    threshold.bounds = threshold.bounds.astype(dtype)
                gordias.util.units.change_units(threshold, units, standard_name)
        if parameters is not None:
            raise NotImplementedError(
                "Parameter files cannot be used with this index function."
            )
        super().prepare(input_cubes)

    def lazy_func(self, data, axis, **kwargs):
        if not isinstance(data, dict):
            data = {"data": data}
        conditions = []
        mask = []
        for name, arr in data.items():
            mask.append(da.ma.getmaskarray(arr).any(axis=axis))
            for threshold, operator in self.mapping[name]:
                conditions.append(operator(arr, threshold.points))
        filled = da.ma.filled(da.stack(conditions, axis=0), fill_value=False)
        cond = da.all(filled, axis=0)
        res = da.count_nonzero(cond, axis=axis)
        masked = da.ma.masked_array(
            da.ma.getdata(res), da.stack(mask, axis=0).any(axis=0)
        )
        return masked.astype("float32")

    call_func = lazy_func


class CountJointOccurrencesPrecipitationTemperature(CountJointOccurrences):
    def __init__(
        self,
        threshold_precip_data,
        threshold_temp_data,
        condition_precip_data,
        condition_temp_data,
    ):
        super().__init__(
            mapping={
                "precip_data": [
                    (threshold_precip_data, DASK_OPERATORS[condition_precip_data])
                ],
                "temp_data": [
                    (threshold_temp_data, DASK_OPERATORS[condition_temp_data])
                ],
            }
        )


class CountJointOccurrencesTemperature(CountJointOccurrences):
    def __init__(
        self,
        threshold_low_data,
        threshold_high_data,
        condition_low_data,
        condition_high_data,
    ):
        super().__init__(
            mapping={
                "data": [
                    (threshold_low_data, DASK_OPERATORS[condition_low_data]),
                    (threshold_high_data, DASK_OPERATORS[condition_high_data]),
                ]
            }
        )


class CountJointOccurrencesPrecipitationDoubleTemperature(CountJointOccurrences):
    def __init__(
        self,
        threshold_precip_data,
        threshold_temp_low_data,
        threshold_temp_high_data,
        condition_precip_data,
        condition_temp_low_data,
        condition_temp_high_data,
    ):
        super().__init__(
            mapping={
                "precip_data": [
                    (threshold_precip_data, DASK_OPERATORS[condition_precip_data])
                ],
                "temp_data": [
                    (threshold_temp_low_data, DASK_OPERATORS[condition_temp_low_data]),
                    (
                        threshold_temp_high_data,
                        DASK_OPERATORS[condition_temp_high_data],
                    ),
                ],
            }
        )
