#!/usr/bin/env python

'''
Tests for check_chunk_size.py
'''
from compliance_checker.base import BaseCheck
from compliance_checker.checks.data_plausibility_checks import check_constant_v453 as checker
from compliance_checker.tests import BaseTestCase
from compliance_checker.tests.resources import STATIC_FILES

class TestConstants(BaseTestCase):
    
    # NOMINAL TEST CASES
    def test_constants(self):
        dataset = self.load_dataset(STATIC_FILES["data_check_reference"])
        variable="tas"
        output = checker.check_constants(dataset,variable, severity=BaseCheck.MEDIUM)
        results = output.to_result()
        assert results is not None
        self.assert_result_is_good(results)

    # ERROR TEST CASES
    def test_constants_fails(self):
        dataset = self.load_dataset(STATIC_FILES["data_check_reference_constant"])
        variable="tas"
        output = checker.check_constants(dataset,variable, severity=BaseCheck.MEDIUM)
        results = output.to_result()
        assert results is not None
        print(results)
        self.assert_result_is_bad(results)
