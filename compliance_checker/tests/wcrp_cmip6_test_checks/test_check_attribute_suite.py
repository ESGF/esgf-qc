
import os
from netCDF4 import Dataset
from compliance_checker.checks.attribute_checks import check_attribute_suite as checker
from compliance_checker.tests import BaseTestCase
from compliance_checker.base import BaseCheck

class TestCheckAttributeSuite(BaseTestCase):

    def test_check_attribute_suite(self):
        file_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), "..", "..", "data", "CMIP6", "CMIP", "IPSL", "IPSL-CM5A2-INCA",
            "historical", "r1i1p1f1", "Amon", "pr", "gr", "v20240619",
            "pr_Amon_IPSL-CM5A2-INCA_historical_r1i1p1f1_gr_185001-201412.nc"
        ))
        dataset = Dataset(file_path, mode="r")
        results = checker.check_attribute_suite(dataset, "table_id", severity=BaseCheck.MEDIUM, expected_type='str', constraint=None, var_name=None, project_name="cmip6")
        assert len(results) == 4
        for res in results:
            self.assert_result_is_good(res) 		
        #self.assert_result_is_good_or_bad(results[0])
