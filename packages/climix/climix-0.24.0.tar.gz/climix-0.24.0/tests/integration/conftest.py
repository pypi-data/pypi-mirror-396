from gordias import dask_setup
import pathlib
import pytest
import yaml

from climix import metadata


def read_test_configuration():
    """Read test configuration from 'configuration.yml'."""
    config_string = (
        pathlib.Path(__file__).parent.joinpath("configuration.yml").read_text()
    )
    config = yaml.safe_load(config_string)
    return config


@pytest.fixture(scope="session")
def f_test_configuration():
    """Return test configuration."""
    return read_test_configuration()


@pytest.fixture(scope="session")
def f_climix_metadata():
    """Create Climix index catalog."""
    return metadata.load_metadata()


@pytest.fixture
def f_default_scheduler():
    """Create a default dask scheduler."""
    return dask_setup.DistributedLocalClusterScheduler()
