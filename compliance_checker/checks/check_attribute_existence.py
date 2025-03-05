#!/usr/bin/env python
"""
check_attribute_existence.py
Author : NACHITE Ayoub ''IPSL''


This module provides an atomic check that verifies whether a specified attribute
exists (globally or within a given variable) in a netCDF dataset, using a try/except 
block to handle potential errors.

Intended to be included in the WCRP plugins.
"""

from compliance_checker.base import BaseCheck, TestCtx

def check_attribute_existence(
    ds,
    attribute_name,
    var_name=None,
    severity=BaseCheck.MEDIUM
):
    """
    Verify that an attribute named 'attribute_name' exists in the dataset 'ds'.
    If 'var_name' is specified, the check looks for 'attribute_name' in that 
    variable; otherwise, it checks for a global attribute of the same name.


    Parameters
    ----------
    ds : netCDF4.Dataset
        An already open netCDF dataset.
    attribute_name : str
        The name of the attribute to check for.
    var_name : str, optional
        If specified, we look for the attribute within this variable.
        If None, we look for a global attribute.
    severity : int, optional
        The severity level of this check (default: BaseCheck.MEDIUM).

    Returns
    -------
    List[Result]
        A list containing one Result object. The .value is a tuple
        (passed_assertions, total_assertions), and .msgs contains error messages
        if the attribute is missing or cannot be retrieved.

    Usage Example:
        from check_attribute_existence import check_attribute_existence
       
        results = check_attribute_existence(ds, 'Conventions')
    """
    ctx = TestCtx(severity, "Attribute Existence Check (with try/except)")

    if var_name is None:
        # Checking global attribute
        try:
            value = ds.getncattr(attribute_name)
            # If getncattr succeeds, the attribute exists
            ctx.assert_true(True, "")
        except AttributeError:
            # If an AttributeError is raised, the attribute doesn't exist
            ctx.assert_true(False, f"Global attribute '{attribute_name}' is missing.")
        except Exception as e:
            # Any other error that might occur unexpectedly
            ctx.assert_true(False, f"Error retrieving global attribute '{attribute_name}': {e}")
    else:
        # Checking attribute on a specific variable
        if var_name not in ds.variables:
            ctx.assert_true(False, f"Variable '{var_name}' not found in dataset.")
        else:
            variable = ds.variables[var_name]
            try:
                value = variable.getncattr(attribute_name)
                # If getncattr succeeds, the attribute exists
                ctx.assert_true(True, "")
            except AttributeError:
                ctx.assert_true(False, f"Attribute '{attribute_name}' missing in variable '{var_name}'.")
            except Exception as e:
                ctx.assert_true(False, f"Error retrieving '{attribute_name}' in variable '{var_name}': {e}")

    return [ctx.to_result()]

