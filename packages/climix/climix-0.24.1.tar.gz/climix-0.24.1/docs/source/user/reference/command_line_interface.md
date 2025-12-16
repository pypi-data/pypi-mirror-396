(command-line-interface)=
# Command Line Interface
The following CLI options are available when running Climix:
:::{list-table}
:widths: auto
:align: center
:header-rows: 1

*   - Option
    - Args
    - Description
*   - `-h`, `--help`
    -
    - Show help, e.g., usage, version, positional arguments, and, CLI options.
*   - `-l`, `--log-level`
    - _debug, info, warning, error, critical_
    - Set the lowest priority level of log messages to display, default is `info`.
*   - `-v`, `--verbose`
    -
    - Output more detailed log messages.
*   - `-d`, `--dask-scheduler`
    - _distributed-local-cluster, external, threaded, mpi, single-threaded_
    - For more advanced usage of dask schedulers. Default is `distributed-local-cluster`.
*   - `-k`, `--keep-open`
    -
    - Keep Climix running until key press (useful for debugging).
*   - `-p`, `--period`
    - _seasonal, annual, monthly, annual[jan], annual[djf] etc._
    - Specify period for index (overrides index default period). Must be one of annual, seasonal, monthly. For annual period, an optional argument can be given to specify a range of months, e.g. annual[jja] for multiple months, or annual[feb] for a single month.
*   - `-s`, `--sliced-mode`
    -
    - Activate calculation per period to avoid memory problems.
*   - `--split-output`
    - _month, season, year, year[5], year[10], year[nr]_
    -   Split the output into multiple files. `nr` can be any number of year.
*   - `-o`, `--output`
    - _/path/myfile.nc_
    - Specify where the result is stored. If not used, by default Climix uses {ref}`output-template-generation` to give the file a name and stores the result in the current working directory.
*   - `--overwrite`
    -
    - By default, Climix will not overwrite an already existing output file. Use this switch to allow the overwriting of a file with the same output filename.
*   - `-f`, `--metadata-file`
    - _/path/mymetadatafile.yml_
    - Add an external metadata file (overrides any default definitions), can be used multiple times to add several files (the last specified file will override any earlier definitions).
*   - `--mask-start`
    - _/path/myparameterfile.nc_
    - Use to mask the start of the input data given a parameter-file. The grid of the input data and the parameter-file must be the same. The parameter-file should contain yearly data, where the data value should represent the day of the year. For each matching year all days before this day will be masked. If a year exists in the input data but not in the parameter-file this year will not be masked. This flag can be used for most standard indicies and works with any annual period, i.e, _annual, annual[mjja] etc._ If not a full year period is specified, a offset will be computed from the first day of the year and the first day of the data.
*   - `--mask-end`
    - _/path/myparameterfile.nc_
    - Use to mask the end of the input data given a parameter-file. The grid of the input data and the parameter-file must be the same. The parameter-file should contain yearly data, where the data value should represent the day of the year. For each matching year all days from this day until the end will be masked. If a year exists in the input data but not in the parameter-file this year will not be masked. This flag can be used for most standard indicies and works with any annual period, i.e, _annual, annual[mjja] etc._ If not a full year period is specified, a offset will be computed from the first day of the year and the first day of the data.
*   - `--activate-config`
    -
    -  Specify if the Climix configuration should be activated. This will apply the default configuration for the output global attributes metadata. The default configuration file can be overridden by adding an external metadata file containing a configuration.
*   - `-r`, `--reference-period`
    - _1971/2000, P48Y/2000, 1971-06-01/2000, P47Y7M/2000_
    - Specify reference period for an index (overrides the default reference period in the index definition), accepted formats are **ISO 8601**.
*   - `cp`, `--computational-period`,
    - _1961-01-01/1990-12-31, 2001-03-13/2009-05-20, etc._
    - Specify computational period for the index, i.e. limit the time interval to a subset of what is available in the input data. The start and end time strings must follow `yyy-mm-dd/yyy-mm-dd` format.
*   - `-x`, `--index`
    - _list, tn, fd, cdd, rx10day, r95pctl, tngtm2, txgt30, etc._
    - The index to calculate. `-x list` returns a list of all available indices.
:::
