# -*- coding: utf-8 -*-

import numpy as np
import sparse


def dask_take_along_axis_chunk(x, idx, offset, x_size, axis):
    # Needed when idx is unsigned
    idx = idx.astype(np.int64)

    # Normalize negative indices
    idx = np.where(idx < 0, idx + x_size, idx)

    # A chunk of the offset dask Array is a numpy array with shape (1, ).
    # It indicates the index of the first element along axis of the current
    # chunk of x.
    idx = idx - offset

    # Drop elements of idx that do not fall inside the current chunk of x
    idx_filter = (idx >= 0) & (idx < x.shape[axis])
    idx[~idx_filter] = 0
    res = np.take_along_axis(x, idx, axis=axis)
    res[~idx_filter] = 0
    return sparse.COO(np.expand_dims(res, axis))


def dask_take_along_axis(x, index, axis):
    from dask.array.core import Array, blockwise, from_array, map_blocks

    if axis < 0:
        axis += x.ndim

    assert 0 <= axis < x.ndim

    assert (
        x.shape[:axis] + x.shape[axis + 1 :]
        == index.shape[:axis] + index.shape[axis + 1 :]
    )

    if np.isnan(x.chunks[axis]).any():
        raise NotImplementedError(
            "take_along_axis for an array with unknown chunks with "
            "a dask.array of ints is not supported"
        )

    # Calculate the offset at which each chunk starts along axis
    # e.g. chunks=(..., (5, 3, 4), ...) -> offset=[0, 5, 8]
    offset = np.roll(np.cumsum(x.chunks[axis]), 1)
    offset[0] = 0
    offset = from_array(offset, chunks=1)
    # Tamper with the declared chunks of offset to make blockwise align it with
    # x[axis]
    offset = Array(offset.dask, offset.name, (x.chunks[axis],), offset.dtype)

    # Define axis labels for blockwise
    x_axes = tuple(range(x.ndim))
    idx_label = (x.ndim,)  # arbitrary unused
    index_axes = x_axes[:axis] + idx_label + x_axes[axis + 1 :]
    offset_axes = (axis,)
    p_axes = x_axes[: axis + 1] + idx_label + x_axes[axis + 1 :]

    # Calculate the cartesian product of every chunk of x vs
    # every chunk of index
    p = blockwise(
        dask_take_along_axis_chunk,
        p_axes,
        x,
        x_axes,
        index,
        index_axes,
        offset,
        offset_axes,
        x_size=x.shape[axis],
        axis=axis,
        meta=sparse.COO(
            np.empty((0, 0), dtype=int),
            np.empty((), dtype=x.dtype),
            shape=(0,) * len(p_axes),
        ),
        dtype=x.dtype,
    )

    res = p.sum(axis=axis)

    res = map_blocks(lambda sparse_x: sparse_x.todense(), res, dtype=res.dtype)

    return res
