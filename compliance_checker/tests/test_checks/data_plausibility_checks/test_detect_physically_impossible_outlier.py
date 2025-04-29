#!/usr/bin/env python
"""
Test for detect_physically_impossible_outlier.py
"""

from compliance_checker.base import BaseCheck
from compliance_checker.checks.data_plausibility_checks import detect_physically_impossible_outlier as checker
from compliance_checker.tests import BaseTestCase
from compliance_checker.tests.resources import STATIC_FILES


class TestPhysOutliers(BaseTestCase):

    # NOMINAL TEST CASES
    def test_detect_physically_impossible_outlier(self):
        dataset = self.load_dataset(STATIC_FILES["physical_outliers_not_exist"])
        results = checker.check_outliers(dataset, severity=BaseCheck.MEDIUM)
        print(results)
        assert len(results) == 1
        self.assert_result_is_good(results[0])

    # ERROR TEST CASES
    def test_detect_physically_impossible_outlier_fails(self):
        dataset = self.load_dataset(STATIC_FILES["physical_outliers_exist"])
        results = checker.check_outliers(dataset, severity=BaseCheck.MEDIUM)
        print(results)
        assert len(results) == 1
        result = results[0]
        self.assert_result_is_bad(result)