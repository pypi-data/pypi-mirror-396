import dask.array as da
import iris
import numpy as np


def multicube_aggregated_by(cubes, coords, aggregator, **kwargs):
    # We assume all cubes have the same coordinates,
    # but a test needs to be added.
    groupby_coords = []
    dimension_to_groupby = None

    # We can't handle weights
    if isinstance(
        aggregator, iris.analysis.WeightedAggregator
    ) and aggregator.uses_weighting(**kwargs):
        raise ValueError(
            "Invalid Aggregation, multicube_aggregated_by() cannot use weights."
        )

    ref_cube = next(iter(cubes.values()))

    coords = ref_cube._as_list_of_coords(coords)
    for coord in sorted(coords, key=lambda coord: coord.metadata):
        if coord.ndim > 1:
            msg = (
                "Cannot aggregate_by coord %s as it is "
                "multidimensional." % coord.name()
            )
            raise iris.exceptions.CoordinateMultiDimError(msg)
        dimension = ref_cube.coord_dims(coord)
        if not dimension:
            msg = (
                'Cannot group-by the coordinate "%s", as its '
                "dimension does not describe any data." % coord.name()
            )
            raise iris.exceptions.CoordinateCollapseError(msg)
        if dimension_to_groupby is None:
            dimension_to_groupby = dimension[0]
        if dimension_to_groupby != dimension[0]:
            msg = "Cannot group-by coordinates over different dimensions."
            raise iris.exceptions.CoordinateCollapseError(msg)
        groupby_coords.append(coord)

    # Determine the other coordinates that share the same group-by
    # coordinate dimension.
    shared_coords = list(
        filter(
            lambda coord_: coord_ not in groupby_coords,
            ref_cube.coords(contains_dimension=dimension_to_groupby),
        )
    )

    # Determine which of each shared coord's dimensions will be aggregated.
    shared_coords_and_dims = [
        (coord_, index)
        for coord_ in shared_coords
        for (index, dim) in enumerate(ref_cube.coord_dims(coord_))
        if dim == dimension_to_groupby
    ]

    # Create the aggregation group-by instance.
    groupby = iris.analysis._Groupby(groupby_coords, shared_coords_and_dims)

    # Create the resulting aggregate-by cube and remove the original
    # coordinates that are going to be groupedby.
    # aggregateby_cube = iris.util._strip_metadata_from_dims(
    #     ref_cube, [dimension_to_groupby]
    # )
    key = [slice(None, None)] * ref_cube.ndim
    # Generate unique index tuple key to maintain monotonicity.
    key[dimension_to_groupby] = tuple(range(len(groupby)))
    key = tuple(key)
    # aggregateby_cube = aggregateby_cube[key]
    aggregateby_cube = ref_cube[key]
    for coord in groupby_coords + shared_coords:
        aggregateby_cube.remove_coord(coord)

    # Determine the group-by cube data shape.
    data_shape = list(ref_cube.shape + aggregator.pre_aggregate_shape(**kwargs))
    data_shape[dimension_to_groupby] = len(groupby)

    # Aggregate the group-by data.
    if aggregator.lazy_func is not None and ref_cube.has_lazy_data():

        def data_getter(cube):
            return cube.lazy_data()

        aggregate = aggregator.lazy_aggregate
        stack = da.stack
    else:

        def data_getter(cube):
            return cube.data

        aggregate = aggregator.aggregate
        stack = np.stack

    front_slice = (slice(None, None),) * dimension_to_groupby
    back_slice = (slice(None, None),) * (len(data_shape) - dimension_to_groupby - 1)

    if len(cubes) == 1:
        groupby_subcubes = map(
            lambda groupby_slice: ref_cube[front_slice + (groupby_slice,) + back_slice],
            groupby.group(),
        )

        def agg(cube):
            data = data_getter(cube)
            result = aggregate(data, axis=dimension_to_groupby, cube=cube, **kwargs)
            return result

    else:
        groupby_subcubes = map(
            lambda groupby_slice: {
                argname: cube[front_slice + (groupby_slice,) + back_slice]
                for argname, cube in cubes.items()
            },
            groupby.group(),
        )

        def agg(cubes):
            data = {argname: data_getter(cube) for argname, cube in cubes.items()}
            result = aggregate(data, axis=dimension_to_groupby, cube=cubes, **kwargs)
            return result

    result = list(map(agg, groupby_subcubes))
    aggregateby_data = stack(result, axis=dimension_to_groupby)

    # Add the aggregation meta data to the aggregate-by cube.
    aggregator.update_metadata(
        aggregateby_cube, groupby_coords, aggregate=True, **kwargs
    )
    # Replace the appropriate coordinates within the aggregate-by cube.
    (dim_coord,) = ref_cube.coords(
        dimensions=dimension_to_groupby, dim_coords=True
    ) or [None]
    for coord in groupby.coords:
        if (
            dim_coord is not None
            and dim_coord.metadata == coord.metadata
            and isinstance(coord, iris.coords.DimCoord)
        ):
            aggregateby_cube.add_dim_coord(coord.copy(), dimension_to_groupby)
        else:
            aggregateby_cube.add_aux_coord(coord.copy(), ref_cube.coord_dims(coord))

    # Attach the aggregate-by data into the aggregate-by cube.
    aggregateby_cube = aggregator.post_process(
        aggregateby_cube, aggregateby_data, coords, **kwargs
    )

    return aggregateby_cube
