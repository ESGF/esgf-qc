#!/usr/bin/env python
"""
Test for check_attribute_existence.py
Author : Ayoub NACHITE ''IPSL''
"""

from compliance_checker.base import BaseCheck
from compliance_checker.checks.attribute_checks import check_attribute_existence as checker
from compliance_checker.tests import BaseTestCase
from compliance_checker.tests.resources import STATIC_FILES

class TestAttributeExistence(BaseTestCase):

    def test_global_attribute_exists(self):
        dataset = self.load_dataset(STATIC_FILES["climatology"])
        results = checker(dataset, "Conventions", severity=BaseCheck.MEDIUM)
        assert len(results) == 1
        self.assert_result_is_good(results[0])

    def test_global_attribute_missing(self):
        dataset = self.load_dataset(STATIC_FILES["climatology"])
        attr_name = "non_existing_global_attr"
        results = checker(dataset, attr_name, severity=BaseCheck.MEDIUM)
        assert len(results) == 1
        result = results[0]
        self.assert_result_is_bad(result)
        assert result.msgs[0] == f"Global attribute '{attr_name}' is missing."

    def test_variable_attribute_exists(self):
        dataset = self.load_dataset(STATIC_FILES["climatology"])
        results = checker(dataset, "units", var_name="lat", severity=BaseCheck.MEDIUM)
        assert len(results) == 1
        self.assert_result_is_good(results[0])

    def test_variable_attribute_missing(self):
        dataset = self.load_dataset(STATIC_FILES["climatology"])
        var_name = ""
        attr_name = "non_existing_attr"
        results = checker(dataset, attr_name, var_name=var_name, severity=BaseCheck.MEDIUM)
        assert len(results) == 1
        result = results[0]
        self.assert_result_is_bad(result)
        assert result.msgs[0] == f"Attribute '{attr_name}' missing in variable '{var_name}'."

