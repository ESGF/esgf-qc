##!/usr/bin/env python
"""
Test for check_utf8_encoding.py
Author: Ayoub NACHITE ''IPSL''
"""
from compliance_checker.base import BaseCheck
from compliance_checker.checks.attribute_checks import check_utf8_encoding as checker
from compliance_checker.tests import BaseTestCase
from compliance_checker.tests.resources import STATIC_FILES

class TestUTF8Encoding(BaseTestCase):

    def test_utf8_encoding_valid(self):
        dataset = self.load_dataset(STATIC_FILES["climatology"])
        results = checker(dataset, severity=BaseCheck.MEDIUM)
        assert len(results) == 1
        self.assert_result_is_good(results[0])

   
