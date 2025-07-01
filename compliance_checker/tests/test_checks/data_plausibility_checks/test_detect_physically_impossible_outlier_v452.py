#!/usr/bin/env python
"""
Test for detect_physically_impossible_outlier_v452.py
"""

from compliance_checker.base import BaseCheck
from compliance_checker.checks.data_plausibility_checks import detect_physically_impossible_outlier_v452 as checker
from compliance_checker.tests import BaseTestCase
from compliance_checker.tests.resources import STATIC_FILES


class TestPhysOutliers(BaseTestCase):

    # NOMINAL TEST CASES
    def test_detect_physically_impossible_outlier(self):
        dataset = self.load_dataset(STATIC_FILES["data_check_reference"])
        print(dataset)
        print(dataset.variables["tas"][:])
        output = checker.check_outliers(dataset, severity=BaseCheck.MEDIUM)
        results = output.to_result()
        print(results)
        assert results is not None
        self.assert_result_is_good(results)

    # ERROR TEST CASES
    def test_detect_physically_impossible_outlier_fails(self):
        dataset = self.load_dataset(STATIC_FILES["data_check_reference_outliers"])
        output = checker.check_outliers(dataset, severity=BaseCheck.MEDIUM)
        results = output.to_result()
        assert results is not None
        self.assert_result_is_bad(results)
