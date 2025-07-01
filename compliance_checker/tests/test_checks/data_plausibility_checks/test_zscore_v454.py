#!/usr/bin/env python
"""
Test for zscore_v454.py
"""

from compliance_checker.base import BaseCheck
from compliance_checker.checks.data_plausibility_checks import zscore_v454 as checker
from compliance_checker.tests import BaseTestCase
from compliance_checker.tests.resources import STATIC_FILES


class TestPhysOutliers(BaseTestCase):

    # NOMINAL TEST CASES
    def test_statistical_outlier(self):
        dataset = self.load_dataset(STATIC_FILES["data_check_reference"])
        variable="tas"
        output = checker.check_zscore(dataset, variable, severity=BaseCheck.MEDIUM)
        results = output.to_result()
        assert results is not None
        self.assert_result_is_good(results)

    # ERROR TEST CASES
    def test_statistical_outlier_fails(self):
        dataset = self.load_dataset(STATIC_FILES["data_check_reference_outliers"])
        variable="tas"
        output = checker.check_zscore(dataset, variable, severity=BaseCheck.MEDIUM)
        results = output.to_result()
        print(output,results)
        assert results is not None
        self.assert_result_is_bad(results)
