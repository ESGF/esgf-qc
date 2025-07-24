
#!/usr/bin/env python
"""
Test for check_variant_label_consistency.py
Author: Ayoub NACHITE ''IPSL''
"""

import os
from netCDF4 import Dataset
from compliance_checker.base import BaseCheck
from compliance_checker.checks.consistency_checks import check_variant_label_consistency as checker
from compliance_checker.tests import BaseTestCase

class TestCheckVariantLabelConsistency(BaseTestCase):

    def test_check_variant_label_consistency(self):
        file_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            "..", "..", "data", "CMIP", "IPSL", "IPSL-CM5A2-INCA", "historical", "r1i1p1f1", "Amon", "pr", "gr", "v20240619", "pr_Amon_IPSL-CM5A2-INCA_historical_r1i1p1f1_gr_185001-201412.nc"
        ))
        dataset = Dataset(file_path, mode="r")
        results = checker.check_variant_label_consistency(dataset, severity=BaseCheck.MEDIUM)
        assert len(results) == 1
        self.assert_result_is_good_or_bad(results[0])

