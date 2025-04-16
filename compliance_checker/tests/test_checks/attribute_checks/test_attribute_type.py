#!/usr/bin/env python
"""
Test for check_attribute_type.py
Author: Ayoub NACHITE ''IPSL''
"""

from compliance_checker.base import BaseCheck
from compliance_checker.checks.attribute_checks import check_single_attribute_type as checker
from compliance_checker.tests import BaseTestCase
from compliance_checker.tests.resources import STATIC_FILES

class TestAttributeType(BaseTestCase):

    def test_global_attribute_type_correct(self):
        dataset = self.load_dataset(STATIC_FILES["climatology"])
        results = checker(dataset, None, "Conventions", str, severity=BaseCheck.MEDIUM)
        assert len(results) == 1
        self.assert_result_is_good(results[0])

    def test_global_attribute_type_incorrect(self):
        dataset = self.load_dataset(STATIC_FILES["climatology"])
        results = checker(dataset, None, "Conventions", int, severity=BaseCheck.MEDIUM)
        assert len(results) == 1
        result = results[0]
        self.assert_result_is_bad(result)
        assert "Global attribute 'Conventions'" in result.msgs[0]

    def test_variable_attribute_type_correct(self):
        dataset = self.load_dataset(STATIC_FILES["climatology"])
        results = checker(dataset, "lat", "units", str, severity=BaseCheck.MEDIUM)
        assert len(results) == 1
        self.assert_result_is_good(results[0])

    def test_variable_attribute_type_incorrect(self):
        dataset = self.load_dataset(STATIC_FILES["climatology"])
        results = checker(dataset, "lat", "units", int, severity=BaseCheck.MEDIUM)
        assert len(results) == 1
        result = results[0]
        self.assert_result_is_bad(result)
        assert "Variable 'lat' attribute 'units'" in result.msgs[0]

     
