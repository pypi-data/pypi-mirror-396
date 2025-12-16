#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import glob
import logging
import os
import textwrap
import time

import gordias.dask_setup
import gordias.datahandling
import gordias.util.cmip_path


from climix import __version__
from climix.metadata import load_metadata
from climix.period import Annual

LOG_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}


def parse_args():
    parser = argparse.ArgumentParser(
        description=(f"A climate index package, version {__version__}."),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "-l",
        "--log-level",
        choices=LOG_LEVELS.keys(),
        default="info",
        help="the lowest priority level of log messages to display",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="write more detailed log messages"
    )
    parser.add_argument("-d", "--dask-scheduler", default="distributed-local-cluster")
    parser.add_argument(
        "-k",
        "--keep-open",
        action="store_true",
        help="keep climix running until key press (useful for debugging)",
    )
    parser.add_argument(
        "-p",
        "--period",
        help=textwrap.dedent(
            """\
            Specify period for index (overrides index default period).
            Must be one of annual,seasonal,monthly. For annual period,
            an optional argument can be given to specify a range of months,
            e.g. annual[jja] for multiple months, or annual[feb] for a
            single month.
            """
        ),
    )
    parser.add_argument(
        "-s",
        "--sliced-mode",
        action="store_true",
        help="activate calculation per period to avoid memory problems",
    )
    parser.add_argument(
        "--split-output",
        help=textwrap.dedent(
            """\
               Split the output into multiple files.

               Example of usage:
               --split-output month
               --split-output year
               --split-output season
               --split-output year[nr]

               Here 'nr' can be any number of year:
               --split-output year[5]
               --split-output year[10]
            """
        ),
    )
    parser.add_argument(
        "-o", "--output", dest="output_template", help="output filename"
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help=textwrap.dedent(
            """\
            By default, Climix will not overwrite an already existing output file.
            Use this switch to allow the overwriting of a file with the same
            output filename.
            """
        ),
    )
    parser.add_argument(
        "-f",
        "--metadata-file",
        metavar="METADATA_FILE",
        dest="metadata_files",
        action="append",
        help=textwrap.dedent(
            """\
            add an external metadata file (overrides any default definitions),
            can be used multiple times to add several files (the last specified
            file will override any earlier definitions)
            """
        ),
    )
    parser.add_argument(
        "--mask-start",
        metavar="MASK_START",
        dest="mask_start",
        action="append",
        help=textwrap.dedent(
            """\
            add a parameter file to mask the start of the data. Use to mask the start of
            the input data given a parameter-file. The grid of the input data and the
            parameter-file must be the same. The parameter-file should contain yearly
            data, where the data value should represent the day of the year. For each
            matching year all days before this day will be masked. If a year exists in
            the input data but not in the parameter-file this year will not be masked.
            This flag can be used for most standard indicies and works with any annual
            period, i.e, annual, annual[mjja] etc. If not a full year period is
            specified, a offset will be computed from the first day of the year and the
            first day of the data.
            """
        ),
    )
    parser.add_argument(
        "--mask-end",
        metavar="MASK_END",
        dest="mask_end",
        action="append",
        help=textwrap.dedent(
            """\
            add a parameter file to mask the end of the data. Use to mask the end of
            the input data given a parameter-file. The grid of the input data and the
            parameter-file must be the same. The parameter-file should contain yearly
            data, where the data value should represent the day of the year. For each
            matching year all days from this day until the end will be masked. If a year
            exists in the input data but not in the parameter-file this year will not
            be masked. This flag can be used for most standard indicies and works with
            any annual period, i.e, annual, annual[mjja] etc. If not a full year period
            is specified, a offset will be computed from the first day of the year and
            the first day of the data.
            """
        ),
    )
    parser.add_argument(
        "--activate-config",
        action="store_true",
        dest="activate_config",
        help=textwrap.dedent(
            """\
            specify if the climix configuration should be activated. This will apply
            the default configuration for the output global attributes metadata.
            The default configuration file can be overridden by adding an external
            climix config metadata file.
            """
        ),
    )
    parser.add_argument(
        "-r",
        "--reference-period",
        help=textwrap.dedent(
            """\
                specify reference period for an index (overrides the default
                reference period in the index definition), accepted formats are
                ISO 8601.
                Examples of usage:
                -r 1971/2000
                -r 1971-06-01/2000
                -r P48Y/2000
                -r P47Y7M/2000
                --reference-period 1971/2000
            """
        ),
    )
    parser.add_argument(
        "-cp",
        "--computational-period",
        help=textwrap.dedent(
            """\
                Specify computational period for the index, i.e. limit the time
                interval to a subset of what is available in the input data.
                The start and end time strings must follow `yyyy-mm-dd/yyyy-mm-dd`
                format, e.g. 1961-01-01/1990-12-31.
            """
        ),
    )
    parser.add_argument(
        "-x",
        "--index",
        action="append",
        required=True,
        metavar="INDEX",
        dest="indices",
        help=textwrap.dedent(
            """\
            the index to calculate
            (use "-x list" to get a list of all available indices)
            """
        ),
    )
    parser.add_argument(
        "datafiles", nargs="*", metavar="DATAFILE", help="the input data files"
    )
    return parser.parse_args()


def setup_logging(log_level, verbose=False):
    if verbose:
        format = (
            "%(relativeCreated)8dms:%(filename)s:%(funcName)s() "
            "%(levelname)s:%(name)s:%(message)s"
        )
    else:
        format = "%(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(level=LOG_LEVELS[log_level], format=format)


def setup_configuration(index, configuration):
    if configuration:
        index_distribution = index.metadata.distribution
        extra_attributes = {
            "CLIMIX_VERSION": f"climix-{__version__}",
            "INDEX_DISTRIBUTION": (
                f"{index_distribution.name}-{index_distribution.version}"
                if index_distribution is not None
                and index_distribution.name is not None
                else ""
            ),
        }
        configuration["global_attributes"].extra_attributes = extra_attributes


def build_output_filename(
    index, datafiles, output_template=None, computational_period=None
):
    """Construct output filename from template and basic information.

    Uses `output_template` to form the output filename by replacing the
    components `frequency` and `var_name`. If no `output_template` is given, it
    will try to guess a good template along CMIP/CORDEX naming standards.

    Parameters
    ----------
    index : climix.index.Index
        Index class.
    datafiles : list[str]
        List of files used to form output filename. Wildcards are expanded.
    output_template : str, optional
        A template to use as basis for output filename. If `None`, a template
        will be guessed based on the datafiles list.
    computational_period : str, optional
        A string with format `yyyy-mm-dd/yyyy-mm-dd` defining a time period.
        Default is None.

    Returns
    -------
    str
        Suggested output file name.
    """
    if output_template is None:
        path_list = []
        for file in datafiles:
            expand = [f for f in glob.glob(file)]
            path_list.extend(expand)

        if computational_period is not None:
            output_template = gordias.util.cmip_path.build_cmip_like_filename_template(
                path_list, time_range_placeholder=True
            )
            time_range = gordias.util.time_string.parse_isodate_time_range(
                computational_period
            )

            # Start and end time string should be in CORDEX/CMIP form, daily resolution.
            # Time range end is be inclusive, which means we have to reduce by a delta
            # (day resolution format = 8 characters) to get correct end CORDEX/CMIP time
            # string.
            #
            start_str = time_range.start.strftime("%Y%m%d")
            end_str = (
                time_range.end - gordias.util.time_string.TIME_RELATIVE_DELTAS[8]
            ).strftime("%Y%m%d")

            output_template = output_template.format(
                output_template.format,
                start=start_str,
                end=end_str,
                var_name="{var_name}",
                frequency="{frequency}",
            )
        else:
            output_template = gordias.util.cmip_path.build_cmip_like_filename_template(
                path_list
            )

    period_specialization = index.period.specialization
    if period_specialization is not None:
        var_name = f"{{var_name}}-{period_specialization}"
    else:
        var_name = "{var_name}"
    drs_copy = index.metadata.output.drs.copy()
    drs_copy["var_name"] = var_name.format(**index.metadata.output.drs)
    drs_copy["frequency"] = index.period.label
    return output_template.format(**drs_copy)


def do_main(
    index_catalog,
    configuration,
    requested_indices,
    period,
    reference_period,
    computational_period,
    datafiles,
    parameter_files,
    output_template,
    overwrite,
    sliced_mode,
    split_output,
    scheduler,
):
    logging.debug("Preparing indices")
    indices = index_catalog.prepare_indices(
        requested_indices, period, reference_period, computational_period
    )
    for index_no, index in enumerate(indices):
        logging.info(
            "Starting calculations for index <"
            f"{requested_indices[index_no]}> in {index}"
        )
        logging.debug("Building output filename")
        output_filename = build_output_filename(
            index, datafiles, output_template, computational_period
        )
        setup_configuration(index, configuration)
        logging.debug("Preparing input data")
        input_data = gordias.datahandling.prepare_input_data(datafiles, configuration)
        parameters = prepare_parameter_files(parameter_files, index)
        logging.debug("Calculating index")
        result = index(
            input_data,
            client=scheduler.client,
            sliced_mode=sliced_mode,
            parameters=parameters,
        )
        logging.info(f"Saving result in {os.path.abspath(output_filename)}")
        gordias.datahandling.save(
            result=result,
            output_filename=output_filename,
            split_output=split_output,
            client=scheduler.client,
            overwrite=overwrite,
            conventions_override=(configuration is not None),
            configuration=configuration,
        )


def prepare_parameter_files(parameter_files, index):
    """Prepare the parameter files used for masking the data.

    Parameters
    ----------
        parameter_files : list[str]
            Input parameter files to load.
        index :  climix.index.Index
            Index Class.

    Returns
    -------
        dict[str, iris.cube.Cube] | None
            A dict with the parameter cubes or `None` if no parameter files were given.

    """
    if parameter_files:
        assert isinstance(
            index.period, Annual
        ), "Parameter files is only supported for annual period."
        parameters = {}
        for key, value in parameter_files.items():
            params = gordias.datahandling.prepare_input_data(value)
            assert len(params) == 1, "Failed to concatenate parameter files."
            parameters[key] = next(iter(params))
    else:
        parameters = None
    return parameters


def parse_parameter_files(args):
    if args.mask_start is None and args.mask_end is None:
        return None
    parameter_files = {}
    if args.mask_start is not None:
        parameter_files["start"] = args.mask_start
    if args.mask_end is not None:
        parameter_files["end"] = args.mask_end
    return parameter_files


def main():
    args = parse_args()
    setup_logging(args.log_level, args.verbose)
    parameter_files = parse_parameter_files(args)
    logging.debug("Loading metadata")
    index_catalog, configuration = load_metadata(
        args.metadata_files, args.activate_config
    )
    if "list" in args.indices:
        print("Available indices are:")
        print(list(index_catalog.get_list()))
        return

    with gordias.dask_setup.setup_scheduler(args) as scheduler:
        logging.debug("Scheduler ready; starting main program.")
        start = time.time()
        try:
            do_main(
                index_catalog=index_catalog,
                configuration=configuration,
                requested_indices=args.indices,
                period=args.period,
                reference_period=args.reference_period,
                computational_period=args.computational_period,
                datafiles=args.datafiles,
                parameter_files=parameter_files,
                output_template=args.output_template,
                overwrite=args.overwrite,
                sliced_mode=args.sliced_mode,
                split_output=args.split_output,
                scheduler=scheduler,
            )
        finally:
            end = time.time()
            logging.info(f"Calculation took {end - start:.4f} seconds.")  # noqa: E231
        if args.keep_open:
            input("Press enter to close the cluster ")


if __name__ == "__main__":
    main()
