
import os
from netCDF4 import Dataset
from compliance_checker.checks.time_checks import check_time_bounds as checker
from compliance_checker.tests import BaseTestCase
from compliance_checker.base import BaseCheck

class TestCheckTimeBounds(BaseTestCase):

    def test_check_time_bounds(self):
        file_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), "..", "..", "data", "CMIP", "IPSL", "IPSL-CM5A2-INCA",
            "historical", "r1i1p1f1", "Amon", "pr", "gr", "v20240619",
            "pr_Amon_IPSL-CM5A2-INCA_historical_r1i1p1f1_gr_185001-201412.nc"
        ))
        dataset = Dataset(file_path, mode="r")
        results = checker.check_time_bounds(dataset, severity=BaseCheck.MEDIUM)
        assert len(results) == 1
        self.assert_result_is_good_or_bad(results[0])
