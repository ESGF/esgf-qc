#!/usr/bin/env python
"""
check_single_attribute_type.py
Author : NACHITE Ayoub (IPSL)

An atomic check that verifies a single netCDF attribute (global or variable)
has the correct Python type (e.g., str, int, float). We do NOT handle 
existence here, as that is assumed to be done in a separate check.

We do include a try/except to avoid crashing if the attribute or variable 
isn't found, but we won't fail in that case (we'll just skip), since the 
existence check is external.

Usage (in your plugin):
  from check_single_attribute_type import check_single_attribute_type

  # e.g. we want the global attribute "Conventions" to be str:
  results = check_single_attribute_type(ds, None, "Conventions", str)

  # e.g. we want variable "time" attribute "units" to be int (hypothetical):
  results = check_single_attribute_type(ds, "time", "units", int)
"""

from compliance_checker.base import BaseCheck, TestCtx

def check_single_attribute_type(
    ds,
    var_name,
    attr_name,
    expected_type,
    severity=BaseCheck.MEDIUM
):
    """
    Verify that a single netCDF attribute has the Python type 'expected_type'.
    We assume a separate check deals with the attribute's existence, 
    so if it's missing we skip.

    Parameters
    ----------
    ds : netCDF4.Dataset
        An already open netCDF dataset.
    var_name : str or None
        If None, we check the global attribute 'attr_name'.
        Otherwise, we check attribute 'attr_name' in ds.variables[var_name].
    attr_name : str
        The name of the attribute to check.
    expected_type : type
        The Python type expected (str, int, float, etc.).
    severity : int, optional
        Severity level for the check (default: BaseCheck.MEDIUM).

    Returns
    -------
    List[Result]
        A list with one Result object. This Result has .value = (passed, total).
        - If the attribute is found and has the correct type, we pass.
        - If it's found and type mismatches, we fail.
        - If it's missing or an error occurs, we skip (since existence is 
          supposedly handled elsewhere).

    Slack context:
      - netCDF4 auto-converts NC_* -> Python types.
      - We just do isinstance(value, expected_type).
      - For Fortran or strict NC_* checks, a separate approach might be needed.
    """
    ctx = TestCtx(severity, "Single Attribute Type Check")

    def _type_assert(val, exp_type, desc):
        """Checks if val is an instance of exp_type, records pass/fail in ctx."""
        if isinstance(val, exp_type):
            ctx.assert_true(True)
        else:
            ctx.assert_true(False,
                            f"{desc} is type {type(val).__name__}, expected {exp_type.__name__}")

    try:
        if var_name is None:
            # Global attribute
            value = ds.getncattr(attr_name)
            _type_assert(value, expected_type, f"Global attribute '{attr_name}'")
        else:
            # Variable attribute
            value = ds.variables[var_name].getncattr(attr_name)
            _type_assert(value, expected_type,
                         f"Variable '{var_name}' attribute '{attr_name}'")
    except (AttributeError, KeyError):
        # If variable or attribute isn't found, we skip (no fail).
        # Because existence is supposed to be checked by a separate check.
        pass
    except Exception as e:
        # Any other unexpected error (I/O, etc.) -> skip or handle as you wish
        pass

    return [ctx.to_result()]
