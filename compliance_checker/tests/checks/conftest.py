import netCDF4
import pytest


@pytest.fixture(scope="session")
def checks_test_ds(tmp_path_factory):
    path_to_file = tmp_path_factory.mktemp("testdata")
    full_path = path_to_file / "checks_test_ds.nc"

    ds = netCDF4.Dataset(full_path, "w")

    # Dimensions
    ds.createDimension("time", None)

    # Coordinate variables
    time = ds.createVariable("time", "f8", ("time",))
    time.standard_name = "time"
    time.long_name = "time"
    time.axis = "T"
    time.calendar = "standard"
    time.units = "days since 1950-01-01T00:00:00Z"
    time[:] = [0.0, 1.0, 2.0, 3.0, 4.0]

    # Close to return dataset as readonly
    ds.close()
    return netCDF4.Dataset(full_path)
