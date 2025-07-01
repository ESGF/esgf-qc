#!/usr/bin/env python

'''
Tests for check_chunk_size.py
'''
from compliance_checker.base import BaseCheck
from compliance_checker.checks.data_plausibility_checks import check_chunk_size as checker
from compliance_checker.tests import BaseTestCase
from compliance_checker.tests.resources import STATIC_FILES

class TestChunkSize(BaseTestCase):
    
    # NOMINAL TEST CASES
    def test_chunk_size(self):
        dataset = self.load_dataset(STATIC_FILES["data_check_reference"])
        output = checker.check_outliers(dataset, severity=BaseCheck.MEDIUM)
        results = output.to_result()
        assert results is not None
        self.assert_result_is_good(results)

    # ERROR TEST CASES
    def test_chunk_size_fails(self):
        dataset = self.load_dataset(STATIC_FILES["data_check_reference_chunksize"])
        output = checker.check_outliers(dataset, severity=BaseCheck.MEDIUM)
        results = output.to_result()
        assert results is not None
        self.assert_result_is_bad(results)
