# -*- coding: utf-8 -*-

import logging

from .aggregators import PointLocalAggregator
from .iris import multicube_aggregated_by
from .period import build_period


class Index:
    def __init__(self, index_function, metadata, period_spec):
        self.index_function = index_function
        self.metadata = metadata
        self.period = build_period(period_spec)
        self.aggregator = PointLocalAggregator(index_function, metadata.output)
        self.input_argnames = set(metadata.input.keys())
        self.mapping = {}
        for argname, iv in metadata.input.items():
            for key in [iv.var_name] + iv.aliases:
                self.mapping[key] = argname

    def __call__(self, cubes, client=None, sliced_mode=False, parameters=None):
        logging.debug("Starting preprocess")
        self.index_function.preprocess(cubes, client)
        logging.debug("Finished preprocess")
        cube_mapping = {
            argname: cube.extract(self.period.constraint)
            for cube in cubes
            if (argname := self.mapping.get(cube.var_name)) is not None  # noqa
        }
        for argname in self.input_argnames:
            if argname in cube_mapping:
                logging.debug("Data found for input <{}>".format(argname))
                if cube_mapping[argname] is None:
                    raise ValueError(
                        f"Cube <{argname}> is empty. Note: Make sure that the data is "
                        "covered by any period constraints."
                    )
            else:
                args = ", ".join(
                    [
                        "{}: {}".format(argname, iv.var_name)
                        for argname, iv in self.metadata.input.items()
                    ]
                )
                raise ValueError(
                    "No data found for input {}. Requested: ({})".format(argname, args)
                )
        assert len(self.input_argnames) == len(cubes), (
            "The number of cubes does not match the required input data. Number of "
            f"required input data <{len(self.input_argnames)}> and number of cubes "
            f"<{len(cubes)}>. Make sure the input data is compatible."
        )
        logging.debug("Adding coord categorisation.")
        coord_name = list(
            map(self.period.add_coord_categorisation, cube_mapping.values())
        )[0]
        logging.debug("Preparing cubes")
        self.index_function.prepare(cube_mapping, parameters)
        logging.debug("Setting up aggregation")
        aggregated = multicube_aggregated_by(
            cube_mapping,
            coord_name,
            self.aggregator,
            period=self.period,
            client=client,
            sliced_mode=sliced_mode,
            output_metadata=self.metadata.output,
        )
        aggregated.attributes["frequency"] = self.period.label
        return aggregated
