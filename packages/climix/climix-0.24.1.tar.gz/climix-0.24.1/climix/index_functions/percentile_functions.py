import logging

from cf_units import Unit
import dask.array as da
from gordias.dask_setup import progress
import gordias.util.time_string
import gordias.util.time_period
import gordias.util.units
import numpy as np

from ..dask_take_along_axis import dask_take_along_axis
from .support import (
    IndexFunction,
    normalize_axis,
    NUMPY_OPERATORS,
    DASK_OPERATORS,
)


def calc_doy_indices(day_of_year):
    max_doy = day_of_year.max()
    for doy in range(1, max_doy + 1):
        exact_inds = np.nonzero(day_of_year == doy)[0]
        inds = np.stack(
            [exact_inds + i for i in range(-2, 3)],
            axis=-1,
        ).ravel()
        yield doy, inds


def convert_to_desired_output(self, data, masked_data, axis, output_unit):
    self.units = Unit(output_unit)
    if output_unit == "mm":
        return np.sum(masked_data, axis=axis)
    if output_unit == "1":
        return np.count_nonzero(masked_data, axis=axis)
    if output_unit == "%":
        sum_masked_data = np.sum(masked_data, axis=axis)
        return 100.0 * (sum_masked_data / np.sum(data, axis=axis))
    raise ValueError(
        f"Output unit <{output_unit}> is not supported for index "
        "function <count_thresholded_percentile_occurrences>."
    )


def hyndman_fan_params(prob, n):
    r"""
    Compute coefficient and index for quantile calculation.

    Following Hyndman and Fan (1996), the quantile for probability :math:`p`,
    :math:`Q(p)`, given the order statistics of a sample with size :math:`n`,
    :math:`X_{(1)} < \dots < X_{(n)}` can be calculated as a linear combination of two
    neighbouring order statistics according to

    .. math:: Q(p) = (1-\gamma)X_{(j)} + \gamma X_{(j+1)},

    where :math:`j = \lfloor pn + m \rfloor` and :math:`\gamma = pn + m - j`, i.e.
    :math:`j` and :math:`\gamma` are the integer and the fractional part of
    :math:`pn + m`, respectively, with :math:`m \in \mathbb{R}` some number such that

    .. math:: \frac{j - m}{n} \le p \le \frac{j - m + 1}{n}

    holds. Choosing :math:`m` now allows one to define different ways to calculate the
    quantiles. In particular, Hyndman and Fan go on to define a class of such approaches
    with

    .. math:: m = \alpha + p(1 - \alpha - \beta)

    characterized by the choice of the constants :math:`\alpha` and :math:`\beta`.
    For consistency with previous methods, here we follow there Definition 8 with
    :math:`\alpha = \frac{1}{3}`, :math:`\beta = \frac{1}{3}`.

    Defining :math:`\delta(\alpha, \beta) = pn + m = p(n + 1 - \alpha - \beta) +
    \alpha`, we find :math:`\delta(\frac{1}{3}, \frac{1}{3}) = p(n + \frac{1}{3}) +
    \frac{1}{3}`, which allows us to calculate :math:`j` and :math:`\gamma`.
    """
    n_array = da.asanyarray(n)
    delta = prob * (n_array + 1.0 / 3.0) + 1.0 / 3.0
    j = delta.astype(np.int64)
    gamma = delta - j
    return (j, gamma.astype(np.float64))


def hyndman_fan_to_topk(n, j, window_size):
    r"""
    Calculate topk argument for Hyndman and Fan order statistics index.

    We need order statistics :math:`j` and :math:`j + 1` to calculate the quantile in
    question. In a parallel setting, it is more efficient to avoid a full sorting of the
    input data and instead to only extract the :math:`j` largest or :math:`j + 1`
    smallest data points, particularly if :math:`j` is small or close to :math:`n` as is
    the case for the often sought extreme quantiles.
    If :math:`j > \frac{n}{2}` we want to calculate the :math:`n - j` largest points,
    else we want to calculate the :math:`j + 1` smallest points, indicated by the
    negative `k` (cf :func:`da.topk`).

    Calculating the quantile on input data that contains masked values, the sample size
    :math:`n` should specify the number of unmasked values. To account for the number of
    masked values we can use :math:`n_masked_values`. When calculating the window for
    the smallest data points, i.e, :math:`k_ext`, we need to include the number of
    masked values. This method assumes that the masked input data is filled with a
    relatively large negative value in relation to the input data. If the input data
    does not contain any masked values :math:`n_masked_values` should be set to zero.
    """
    if da.array((j > n / 2)).any():
        k = n - j
        k_ext = np.max(k + window_size)
    else:
        k = -(j + 1)
        k_ext = np.min(k - window_size)
    return (da.asanyarray(k).astype(np.int64), k_ext.astype(np.int64))


class BootstrapQuantiles:
    def __init__(self, data, prob, first_year, window_size, client, axis):
        data_mask = da.ma.getmaskarray(data)
        if data_mask.any():
            logging.warning(
                "Masked input data is not supported for index function "
                "<count_percentile_occurrences>."
            )
        self.axis = axis
        self.first_year = first_year
        n = data.shape[axis]
        self.j, self.gamma = hyndman_fan_params(prob, n)
        self.k, k_ext = hyndman_fan_to_topk(n, self.j, window_size)
        order_indices = client.persist(da.argtopk(data, k_ext, axis=self.axis))
        progress(order_indices)
        self.order_statistics = client.persist(
            dask_take_along_axis(data, order_indices, axis=self.axis).rechunk()
        )
        progress(self.order_statistics)
        self.years = client.persist(
            first_year + da.floor(order_indices / window_size).rechunk()
        )
        progress(self.years)

    def quantiles(self, ignore_year=None, duplicate_year=None):
        abs_k = abs(self.k)
        if ignore_year is None and duplicate_year is None:
            if self.k.ndim == 0:
                if abs_k < 1:
                    quantiles = self.order_statistics[..., abs_k]
                else:
                    if self.k >= 0:
                        ind_j = abs_k
                        ind_j_plus_one = abs_k - 1
                    else:
                        ind_j = abs_k - 1
                        ind_j_plus_one = abs_k
                    quantiles = (1.0 - self.gamma) * self.order_statistics[
                        ..., ind_j
                    ] + self.gamma * self.order_statistics[..., ind_j_plus_one]
            else:
                if (abs_k < 1).any():
                    ind_j = abs_k
                    ind_j_plus_one = da.where(abs_k > 0, abs_k + 1, abs_k)
                else:
                    if (self.k > 0).any():
                        ind_j = abs_k
                        ind_j_plus_one = abs_k - 1
                    else:
                        ind_j = abs_k - 2.0
                        ind_j_plus_one = abs_k - 1.0
                qi = dask_take_along_axis(
                    self.order_statistics,
                    da.stack([ind_j, ind_j_plus_one], axis=self.axis),
                    axis=self.axis,
                )
                quantiles = (1.0 - self.gamma) * qi[..., 0] + self.gamma * qi[..., 1]
        else:
            offset = da.sum(self.years[..., :abs_k] == ignore_year, axis=self.axis)
            offset -= da.sum(self.years[..., :abs_k] == duplicate_year, axis=self.axis)
            offset += abs_k
            if self.k >= 0:
                ind_j = offset
                ind_j_plus_one = da.where(offset >= 1, offset - 1, offset)
            else:
                ind_j = da.where(offset >= 1, offset - 1, offset)
                ind_j_plus_one = offset
            qi = dask_take_along_axis(
                self.order_statistics,
                da.stack([ind_j, ind_j_plus_one], axis=self.axis),
                axis=self.axis,
            )
            quantiles = (1.0 - self.gamma) * qi[..., 0] + self.gamma * qi[..., 1]
        return quantiles.astype(np.float32)


class BootstrapQuantilesThreshold(BootstrapQuantiles):
    def __init__(
        self, data, threshold, data_condition, prob, window_size, client, axis
    ):
        self.axis = axis
        cond = data_condition(data, threshold)
        n_effective = client.persist(da.count_nonzero(cond, axis=self.axis))
        progress(n_effective)
        self.j, self.gamma = hyndman_fan_params(prob, n_effective)
        self.k, k_ext = hyndman_fan_to_topk(n_effective, self.j, window_size)
        if k_ext < 0:
            fill_value = np.finfo(data.dtype).max
        else:
            fill_value = np.finfo(data.dtype).min
        input_data = da.where(cond, data, fill_value)
        del cond
        order_indices = client.persist(da.argtopk(input_data, k_ext, axis=self.axis))
        progress(order_indices)
        del input_data
        self.order_statistics = client.persist(
            dask_take_along_axis(data, order_indices, axis=self.axis).rechunk()
        )
        progress(self.order_statistics)

    def quantiles(self):
        return super().quantiles()


def build_indices(time, max_doy, no_years, window_size):
    """
    Build indices

    Given a linear time coordinate, build an index array `idx` of shape
    `(max_doy, no_years, window_size)` such that `idx[doy, yr]` contains the
    indices of the `window_size` days in the time coordinate that should
    contribute to the day of year `doy` for the year `yr`. If `doy` is smaller
    than `window_size`, this will include days from the year `yr -
    1`. Conversely, if `doy` is larger than `max_doy - window_size`, it will
    include days from `yr + 1`.
    """
    window_width = window_size // 2
    first_year = time.cell(0).point.timetuple()[0]
    np_indices = np.zeros((max_doy, no_years, window_size), int)
    for c in time.cells():
        tt = c.point.timetuple()
        year = tt[0]
        day_of_year = tt[7] - 1
        if day_of_year >= max_doy:
            continue
        idx_y = year - first_year
        days = np.arange(day_of_year - window_width, day_of_year + window_width + 1)
        np_indices[day_of_year, idx_y] = window_width + idx_y * 365 + days
    np_indices[0, 0, :2] = window_width
    np_indices[1, 0, :1] = window_width
    np_indices[-1, -1, -2:] = np_indices[-1, -1, -3]
    np_indices[-2, -1, -1:] = np_indices[-2, -1, -2]
    return np_indices


class CountPercentileOccurrences(IndexFunction):
    def __init__(self, percentile, condition, reference_period, bootstrapping=True):
        super().__init__(units="%")
        self.reference_period = reference_period
        percentile.convert_units("1")
        self.percentile = float(percentile.points)
        self.condition = NUMPY_OPERATORS[condition]
        self.lazy_condition = DASK_OPERATORS[condition]
        self.bootstrapping = bootstrapping

    def prepare(self, input_cubes, parameters=None):
        super().prepare(input_cubes)
        if parameters is not None:
            raise NotImplementedError(
                "Parameter files cannot be used with this index function."
            )

    def preprocess(self, cubes, client):
        window_size = 5
        window_width = window_size // 2
        cube = cubes[0]
        reference_period = gordias.util.time_string.parse_isodate_time_range(
            self.reference_period
        )
        gordias.util.time_period.validate_time_bounds(cube, reference_period)
        self.extra_coords.append(
            gordias.util.time_period.create_aux_coord_for_time_range(
                cube, reference_period
            )
        )
        max_doy = 365
        self.years = {
            y: np.arange(i * window_size, (i + 1) * window_size)
            for i, y in enumerate(
                range(
                    reference_period.start.year,
                    reference_period.end.year,
                )
            )
        }
        logging.info("Building indices")
        time = cube.coord("time")
        idx_0, idx_n = gordias.util.time_period.get_first_and_last_indices(
            reference_period,
            gordias.util.time_period.get_times_helper(cube),
            time.units.calendar,
        )
        try:
            np_indices = build_indices(
                time[idx_0 : idx_n + 1],
                max_doy,
                len(self.years),
                window_size,
            )
        except IndexError as e:
            raise IndexError(
                "Can only build indices for a reference period that includes "
                "full years, e.g. 1990-01-01/1999-12-31. Unable to build indices "
                "for a subset of years, e.g. 1990-05-01/1999-04-30"
            ) from e
        logging.info("Arranging data")
        all_data = da.moveaxis(
            gordias.util.time_period.extract_data_for_time_range(
                cube, reference_period, padding=window_width
            ),
            0,
            -1,
        )
        all_data = all_data.rechunk(("auto",) * (all_data.ndim - 1) + (-1,))
        all_data = client.persist(all_data)
        progress(all_data)
        data = []
        for idx_d in range(max_doy):
            d = client.persist(all_data[..., np_indices[idx_d].ravel()])
            progress(d)
            data.append(d)
            logging.info(f"Finished doy {idx_d}")
        data = da.stack(data, axis=0)
        data = data.rechunk({0: "auto"})
        logging.info(f"data chunks: {data.chunks}")
        data = client.persist(data)
        progress(data)
        logging.info(f"data chunks: {data.chunks}")
        chunks = (-1,) + (10,) * (data.ndim - 2) + (-1,)
        data = data.rechunk(chunks)
        data = client.persist(data)
        progress(data)
        logging.info("Initializing quantiles")
        self.quantiler = BootstrapQuantiles(
            data,
            self.percentile,
            reference_period.start.year,
            window_size,
            client,
            axis=-1,
        )
        logging.info("Starting quantile calculation")
        res = client.persist(self.quantiler.quantiles().rechunk())
        progress(res)
        self.out_of_base_quantiles = res

    def call_func(self, data, axis, **kwargs):
        pass

    def lazy_func(self, data, axis, cube, client, **kwargs):
        year = cube.coord("time").cell(0).point.year
        logging.info(f"Starting year {year}")
        if data.shape[0] > 365:
            data = data[:-1]
        if self.bootstrapping and year in self.years:
            logging.info("Using bootstrapping")
            quantile_years = [y for y in self.years.keys() if y != year]
            counts = []
            for duplicate_year in quantile_years:
                quantiles = self.quantiler.quantiles(
                    ignore_year=year, duplicate_year=duplicate_year
                )
                cond = self.lazy_condition(data[...], quantiles)
                count = da.count_nonzero(cond, axis=0)
                counts.append(count)
            counts = da.stack(counts, axis=-1)
            counts = counts.rechunk(("auto",) * (counts.ndim - 1) + (-1,))
            avg_counts = counts.mean(axis=-1)
            percents = avg_counts / (data.shape[0] / 100.0)
        else:
            logging.info("Not using bootstrapping")
            cond = self.lazy_condition(data, self.out_of_base_quantiles)
            counts = da.count_nonzero(cond, axis=0).astype(np.float32)
            percents = counts / (data.shape[0] / 100.0)
        return percents


class CountThresholdedPercentileOccurrences(CountPercentileOccurrences, IndexFunction):
    def __init__(
        self,
        percentile,
        data_threshold,
        data_condition,
        percentile_condition,
        reference_period,
        **kwargs,
    ):
        super().__init__(percentile, percentile_condition, reference_period)
        self.data_threshold = data_threshold
        self.data_condition = NUMPY_OPERATORS[data_condition]
        self.data_lazy_condition = DASK_OPERATORS[data_condition]

    def preprocess(self, cubes, client):
        cube = cubes[0]
        logging.info("Convert threshold unit to match data unit")
        data_threshold = self.data_threshold
        data_threshold.points = data_threshold.points.astype(cube.dtype)
        if data_threshold.has_bounds():
            data_threshold.bounds = data_threshold.bounds.astype(cube.dtype)
        gordias.util.units.change_units(data_threshold, cube.units, cube.standard_name)
        reference_period = gordias.util.time_string.parse_isodate_time_range(
            self.reference_period
        )
        gordias.util.time_period.validate_time_bounds(cube, reference_period)
        self.extra_coords.append(
            gordias.util.time_period.create_aux_coord_for_time_range(
                cube, reference_period
            )
        )
        logging.info("Arranging data")
        ref_data = da.moveaxis(
            gordias.util.time_period.extract_data_for_time_range(
                cube, reference_period
            ),
            0,
            -1,
        )
        ref_data = ref_data.rechunk(("auto",) * (ref_data.ndim - 1) + (-1,))
        progress(ref_data)
        logging.info(f"data chunks: {ref_data.chunks}")
        logging.info("Initializing quantiles")
        quantiler = BootstrapQuantilesThreshold(
            ref_data,
            self.data_threshold.points,
            self.data_lazy_condition,
            self.percentile,
            365,
            client,
            axis=-1,
        )
        logging.info("Starting quantile calculation")
        res = client.persist(quantiler.quantiles().rechunk())
        progress(res)
        res = client.persist(da.ma.filled(res, fill_value=0.0))
        progress(res)
        self.out_of_base_quantiles = res

    def call_func(self, data, axis, **kwargs):
        self.axis = normalize_axis(axis, data.ndim)
        data_mask = np.ma.getmaskarray(data)
        data_mask = data_mask.any(axis=axis)
        cond = self.data_condition(data, self.data_threshold.points)
        threshold_cond = np.ma.masked_where(~cond, data)
        percentile_cond = self.condition(threshold_cond, self.out_of_base_quantiles)
        masked_data = np.ma.masked_where(~percentile_cond, data)
        output_unit = kwargs["output_metadata"].units
        res = convert_to_desired_output(
            self, threshold_cond, masked_data, axis, output_unit
        )
        res = np.ma.filled(res, fill_value=0.0)
        res = np.ma.masked_where(data_mask, res)
        return res.astype(np.float32)

    def lazy_func(self, data, axis, **kwargs):
        self.axis = normalize_axis(axis, data.ndim)
        data_mask = da.ma.getmaskarray(data)
        data_mask = data_mask.any(axis=axis)
        cond = self.data_lazy_condition(data, self.data_threshold.points)
        threshold_cond = da.ma.masked_where(~cond, data)
        percentile_cond = self.lazy_condition(
            threshold_cond, self.out_of_base_quantiles
        )
        masked_data = da.ma.masked_where(~percentile_cond, data)
        output_unit = kwargs["output_metadata"].units
        res = convert_to_desired_output(
            self, threshold_cond, masked_data, axis, output_unit
        )
        res = da.ma.filled(res, fill_value=0.0)
        res = da.ma.masked_where(data_mask, res)
        return res.astype(np.float32)
