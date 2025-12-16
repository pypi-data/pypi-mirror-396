# -*- coding: utf-8 -*-

import logging
import time

import dask.array as da
from iris.analysis import Aggregator
import iris.coords

import gordias.dask_setup
import gordias.util.units


class PointLocalAggregator(Aggregator):
    def __init__(self, index_function, output_metadata, **kwargs):
        self.index_function = index_function
        self.output_metadata = output_metadata
        super().__init__(
            cell_method=None,
            call_func=self.index_function.call_func,
            lazy_func=self.index_function.lazy_func,
            **kwargs,
        )

    def update_metadata(self, cube, coords, **kwargs):
        super().update_metadata(cube, coords, **kwargs)
        cube.var_name = self.output_metadata.var_name
        cube.long_name = self.output_metadata.long_name
        cube.standard_name = self.index_function.standard_name
        cube.units = self.index_function.units
        cube.cell_methods = tuple(
            [
                iris.coords.CellMethod(cm.method, cm.name)
                for cm in self.output_metadata.cell_methods
            ]
        )

    def add_extra_coordinates(self, cube, extra_coords):
        for extra_coord in extra_coords:
            ndims = ()
            if not len(extra_coord.shape) == 1:
                for dim in extra_coord.shape:
                    try:
                        index = cube.shape.index(dim)
                        ndims += (index,)
                    except ValueError:
                        raise ValueError(
                            f"Auxiliary coordinate <{extra_coord.var_name}> "
                            "dimensions must match the cubes dimensions. Auxiliary "
                            f"coordinate shape <{extra_coord.shape}>. Cube shape "
                            f"<{cube.shape}>"
                        )
            try:
                cube.add_aux_coord(extra_coord, data_dims=ndims)
            except ValueError as e:
                logging.warning(
                    f"Extra coordinate <{extra_coord.var_name}> already exists in the"
                    f"cube <{e}>. Replacing coordinate with the new."
                )
                cube.remove_coord(extra_coord)
                cube.add_aux_coord(extra_coord, data_dims=ndims)

    def compute_pre_result(self, data, client, sliced_mode):
        if sliced_mode:
            logging.debug("Computing pre-result in sliced mode")
            stack = []
            end = time.time()
            cumulative = 0.0
            no_slices = len(data)
            for i, d in enumerate(data):
                result_id = f"{i + 1}/{no_slices}"
                logging.info(f"Computing partial pre-result {result_id}")
                d = client.persist(d)
                gordias.dask_setup.progress(d)
                print()
                stack.append(d)
                start = end
                end = time.time()
                last = end - start
                cumulative += last
                eta = cumulative / (i + 1) * no_slices
                logging.info(
                    f"Finished {result_id} in (last cum eta): "
                    f"{last:4.0f} {cumulative:4.0f} {eta:4.0f}"  # noqa: E231
                )
            data = da.stack(stack, axis=0)
        else:
            logging.debug("Setting up pre-result in aggregate mode")
            start = time.time()
            data = client.persist(data)
            end = time.time()
            logging.debug(f"Setup completed in {end - start:4.0f}")  # noqa: E231
        return data

    def post_process(self, cube, data, coords, client, sliced_mode, **kwargs):
        data = self.compute_pre_result(data, client, sliced_mode)
        try:
            post_processor = self.index_function.post_process
        except AttributeError:
            # this index function does not require post processing
            pass
        else:
            cube, data = post_processor(cube, data, coords, **kwargs)
        cube = super().post_process(cube, data, coords, **kwargs)
        standard_name = self.output_metadata.standard_name
        unit_standard_name = standard_name
        proposed_standard_name = self.output_metadata.proposed_standard_name
        if unit_standard_name is None:
            unit_standard_name = proposed_standard_name
        gordias.util.units.change_units(
            cube, self.output_metadata.units, unit_standard_name
        )
        cube.standard_name = standard_name
        if proposed_standard_name is not None:
            cube.attributes["proposed_standard_name"] = proposed_standard_name
        # Remove auxiliary coordinates added to slice the data into time periods
        for coord in coords:
            cube.remove_coord(coord)
        self.add_extra_coordinates(cube, self.index_function.extra_coords)
        return cube

    def pre_aggregate_shape(self, *args, **kwargs):
        return self.index_function.pre_aggregate_shape(*args, **kwargs)
