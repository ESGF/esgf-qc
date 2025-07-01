#!/usr/bin/env python
'''
Tests for check_nan_inf.py
'''

from compliance_checker.base import BaseCheck
from compliance_checker.checks.data_plausibility_checks import check_nan_inf_v451 as checker
from compliance_checker.tests import BaseTestCase
from compliance_checker.tests.resources import STATIC_FILES

class TestNan(BaseTestCase):

    # NOMINAL TEST CASES
    def test_nan(self):
        dataset = self.load_dataset(STATIC_FILES["data_check_reference"])
        variable="tas"
        parameter="NaN"
        output = checker.check_nan_inf(dataset,variable,parameter,severity=BaseCheck.MEDIUM)
        results = output.to_result()
        assert results is not None
        self.assert_result_is_good(results)

    def test_inf(self):
        dataset = self.load_dataset(STATIC_FILES["data_check_reference"])
        variable="tas"
        parameter="Inf"
        output = checker.check_nan_inf(dataset,variable,parameter,severity=BaseCheck.MEDIUM)
        results = output.to_result()
        assert results is not None
        self.assert_result_is_good(results)

    # ERROR TEST CASES
    def test_inf_fails(self):
        #tests -inf and +inf
        dataset_pos_inf = self.load_dataset(STATIC_FILES['data_check_reference_inf'])
        dataset_neg_inf = self.load_dataset(STATIC_FILES['data_check_reference_inf_neg'])
        variable="tas"
        parameter="Inf"
        output_pos = checker.check_nan_inf(dataset_pos_inf,variable,parameter,severity=BaseCheck.MEDIUM)
        output_neg = checker.check_nan_inf(dataset_neg_inf,variable,parameter,severity=BaseCheck.MEDIUM)
        res_pos = output_pos.to_result()
        res_neg = output_neg.to_result()

        assert (res_pos is not None)and (res_neg is not None)
        self.assert_result_is_bad(res_pos)
        self.assert_result_is_bad(res_neg)


    # ERROR TEST CASES
    def test_nan_fails(self):
        dataset = self.load_dataset(STATIC_FILES["data_check_reference_nan"])
        variable="tas"
        parameter="NaN"
        output = checker.check_nan_inf(dataset,variable,parameter,severity=BaseCheck.MEDIUM)
        results = output.to_result()
        assert results is not None
        self.assert_result_is_bad(results)
