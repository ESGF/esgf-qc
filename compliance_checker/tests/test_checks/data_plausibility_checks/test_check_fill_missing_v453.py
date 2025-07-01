#!/usr/bin/env python
"""
Test for check_fill_missing_v453.py 
"""

from compliance_checker.base import BaseCheck
from compliance_checker.checks.data_plausibility_checks import check_fill_missing_v453 as checker
from compliance_checker.tests import BaseTestCase
from compliance_checker.tests.resources import STATIC_FILES


class TestPhysOutliers(BaseTestCase):

    # NOMINAL TEST CASE FillValue
    def test_detect_fillvalues(self):
        dataset = self.load_dataset(STATIC_FILES["data_check_reference"])
        variable="tas"
        parameter="FillValue"
        output = checker.check_fillvalues_timeseries(dataset,variable,parameter=parameter, severity=BaseCheck.MEDIUM)
        results = output.to_result()
        assert results is not None
        self.assert_result_is_good(results)

    # ERROR TEST CASES FillValue
    def test_detect_fillvalues_fails(self):
        dataset = self.load_dataset(STATIC_FILES["data_check_reference_FillValue"])
        variable="tas"
        parameter="FillValue"
        output = checker.check_fillvalues_timeseries(dataset,variable,parameter=parameter, severity=BaseCheck.MEDIUM)
        results = output.to_result()
        assert results is not None
        self.assert_result_is_bad(results)
    
    # NOMINAL TEST CASE MissingValue
    def test_detect_missingvalues(self):
        dataset = self.load_dataset(STATIC_FILES["data_check_reference"])
        variable="tas"
        parameter="MissingValue"
        output = checker.check_fillvalues_timeseries(dataset,variable,parameter=parameter, severity=BaseCheck.MEDIUM)
        results = output.to_result()
        assert results is not None
        self.assert_result_is_good(results)

    # ERROR TEST MissingValue
    def test_detect_missingvalues_fails(self):
        dataset = self.load_dataset(STATIC_FILES["data_check_reference_missing_values"])
        variable="tas"
        parameter="MissingValue"
        output = checker.check_fillvalues_timeseries(dataset,variable,parameter=parameter, severity=BaseCheck.MEDIUM)
        print(output)
        results = output.to_result()
        assert results is not None
        self.assert_result_is_bad(results)
