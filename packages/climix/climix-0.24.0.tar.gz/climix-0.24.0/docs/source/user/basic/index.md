# Basic

Climix is a tool to calculate climate indices.
We focus on high performance for the efficient calculation of indices in large datasets, such as long simulations performed by high-resolution global or regional climate models, and on high-quality metadata, maximizing re-use and utility of these computations.

For now, we always base our calculations on daily input, though an extension to sub-daily input for specialized indices, or monthly input for long-running datasets with limited data availability may be considered in the future.

## Getting started
### Install
If you already have an installed version of Climix available, you can move on to {ref}`first-index`.

The easiest way to install Climix is using the Conda-forge distribution.

#### Conda-forge (recommended)
To install Climix from Conda-forge, you use the Conda package manager or its faster sibling Mamba.
If you don't already have a version of Conda or Mamba available to you, the best way to get started is by installing [Mambaforge](https://github.com/conda-forge/miniforge#mambaforge), an installer for Mamba that will pre-configure your installation to use the Conda-forge distribution.

:::{tip}
If you prefer to use Conda instead of Mamba, for example because this has been pre-installed for you, just replace `mamba` with `conda` in the following commands.
:::

To install the latest version of Climix, just create an environment with the `climix` package in it by running
```{code-block} bash
mamba create -n my-climix climix
```
where `my-climix` is an arbitrary name you choose.

To use Climix at any time, you need to make sure that the `my-climix` environment is activated.
To do that, execute:
```{code-block} bash
mamba activate my-climix
```
Try running Climix with the help-option:
```{code-block} bash
climix --help
```
If installed correctly Climix will print information about the usage, installed version and available command line options.
:::{seealso}
{ref}`command-line-interface`
:::
(first-index)=
### Calculating a first index
As a first example, let's calculate the index {ref}`idx-cdd` or consecutive dry days.
This index is based on precipitation, which we provide to Climix in the form of a Netcdf file.
Climix works with a wide variety of these files which are commonly used for climate and earth data.
Here, we use `pr.nc` as a standin, try to run the program with a precipitation data file of your choosing, for example from CMIP6.

```{code-block} bash
climix -x cdd -o cdd.nc pr.nc
```
You select the index you want to calculate with the `-x` option. Climix will store the result in a new Netcdf file in the current working directory.
You can specify the name with the `-o` option as we did above, or you can let Climix choose a filename. For further information, see {ref}`output-template-generation`.
:::{tip}
For a quick overview of the available indices you can give the command: `climix -x list`
:::
You will see a message `Calculation completed` when Climix is done with the computation.
:::{seealso}
{ref}`available-indices`
:::

(output-template-generation)=
### Output template generation
When running Climix, it automatically generates an output template for the filename. This works well for files with the same basic filename structure, where only the time stamp, variable and simulation components differ. For example, given an index `cdd` and two input files:
:::{code}
1:"/path/tasmin_project_historical_run_model_version_day_20060101-20101231.nc"
2:"/path/tasmin_project_scenario_run_model_version_day_200110101-20151231.nc"
:::
The output template starts with the index that is being computed, in this case `cdd`. If there is any period constrains it will be connected to the index with a hyphen, e.g, `cdd-jfm`. Thereafter, the parts that are similar between the files are kept. If the input files contains both historical and scenario simulations, these will be concatenated with a hyphen in the output template. The time period of the template will always represent the whole period as covered by all files. Thus, it will be reformatted to ensure hyphenated form, `start-end`, even in the case of a single timestamp, e.g, a single year. A `computational_period` can be given as input argument to define a new time period. This period must be given in the format `yyyy-mm-dd/yyyy-mm-dd` and must be inside the original time period. If the input files contains a frequency keyword, the keyword will be replaced by the output frequency. Otherwise, the output frequency will be added to the end of the output template. The input files from above would result in the following output template:
:::{code}
"cdd_project_historical-scenario_run_model_version_{frequency}_20060101-20151231"
:::
:::{Note}
If Climix fails to construct the output template because the time period could not be determined, the template will be given as `{index}_{base}.nc`. If the construction failes due to any other problems the fallback template `{index}_{frequency}.nc` will be returned.
:::
:::{Tip}
This works well with CMIP/CORDEX style filenames.
:::
