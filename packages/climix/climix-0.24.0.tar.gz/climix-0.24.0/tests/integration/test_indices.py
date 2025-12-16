import pathlib

import cf_units
import dask.array as da
import iris
import pytest

from climix import main

from .conftest import read_test_configuration


def validate_coord(cube, reference_cube, coord_name):
    coord = cube.coord(coord_name)
    reference_coord = reference_cube.coord(coord_name)
    assert coord.units == reference_coord.units
    assert da.allclose(coord.points, reference_coord.points)
    if coord.bounds is not None or reference_coord.bounds is not None:
        assert da.allclose(coord.bounds, reference_coord.bounds)


def validate_data(cube, reference_cube, validation):
    assert cube.units == reference_cube.units or (
        cube.units == cf_units.Unit("1")
        and reference_cube.units == cf_units.Unit("days")
    )

    assert da.equal(cube.data.mask, reference_cube.data.mask).all()

    data = da.ma.filled(cube.data, fill_value=0).astype("float32")
    reference_data = da.ma.filled(reference_cube.data, fill_value=0).astype("float32")

    for validation_type, value in validation.items():
        if validation_type == "allclose":
            assert da.allclose(data, reference_data, atol=value)
        elif validation_type == "mismatch_ratio":
            diff = da.absolute(data - reference_data).compute()
            ratio = da.count_nonzero(diff).compute() / diff.size
            assert ratio <= value
        else:
            raise Exception(f"Unknown validation type {validation_type}.")


def generate_test_index_parametrization():
    config = read_test_configuration()
    test_params_list = []
    for test_set_name, test_set_config in config["test_configuration"].items():
        for test_config in test_set_config["tests"].values():
            test_params_list.append(
                (
                    test_set_name,
                    test_config["index"],
                    test_config["reference_data"],
                    test_config["period"],
                    test_config["comparisons"],
                    test_config["compare_coords"],
                )
            )
    return test_params_list


@pytest.mark.parametrize(
    "test_set, index, reference_data, period, comparisons, compare_coords",
    generate_test_index_parametrization(),
)
def test_index(
    test_set,
    index,
    reference_data,
    period,
    comparisons,
    compare_coords,
    f_test_configuration,
    f_climix_metadata,
    f_default_scheduler,
    f_test_data_output_path,
):
    """Test specified index using dataset in f_dataset fixture."""

    index_catalog, climix_config = f_climix_metadata
    test_settings = f_test_configuration["test_settings"]
    data_config = f_test_configuration["test_configuration"][test_set]["data"]

    # Prep index
    indices = index_catalog.prepare_indices([index], period)
    assert len(indices) == 1

    # Get input file paths and reference file path from test config
    input_file_path = (
        pathlib.Path(test_settings["base_path"]) / data_config["variable_path"]
    )
    var_list = [v.var_name for v in indices[0].metadata.input.values()]
    input_file_list = []
    for var in var_list:
        input_file_list.extend(input_file_path.glob(data_config["variables"][var]))
    ref_file_path = (
        pathlib.Path(test_settings["base_path"])
        / data_config["index_path"]
        / reference_data
    )

    # Generate output using Climix
    frequency = {"annual": "yr", "seasonal": "sem", "monthly": "mon"}
    output_filename = f"{index}_{frequency[period]}.nc"
    output_file_path = f_test_data_output_path / output_filename
    with f_default_scheduler as scheduler:
        main.do_main(
            index_catalog=index_catalog,
            configuration=climix_config,
            requested_indices=[index],
            period=period,
            reference_period=None,
            computational_period=None,
            datafiles=input_file_list,
            parameter_files=None,
            output_template=str(output_file_path),
            overwrite=True,
            sliced_mode=False,
            split_output=None,
            scheduler=scheduler,
        )

    cube = iris.load_cube(output_file_path)
    reference_cube = iris.load_cube(ref_file_path)

    if compare_coords:
        for coord in reference_cube.coords():
            validate_coord(cube, reference_cube, coord.name())

    validate_data(cube, reference_cube, comparisons)
