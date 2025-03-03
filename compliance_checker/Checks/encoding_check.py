"""
check_utf8_encoding.py
Ayoub NACHITE

This module provides an atomic function to verify that all global
and variable attributes in a netCDF dataset can be encoded in UTF-8.

Intended to be included in the WCRP plugins.
"""

from compliance_checker.base import BaseCheck, TestCtx

def check_utf8_encoding(ds, severity=BaseCheck.MEDIUM):
    """
    Verify that all global and variable attributes in the given dataset 'ds'
    can be successfully encoded in UTF-8.

    Parameters
    ----------
    ds : netCDF4.Dataset
        An already open netCDF dataset.
    severity : int, optional
        The severity level to assign to this check (default: BaseCheck.MEDIUM).

    Returns
    -------
    List[Result]
        A list containing one Result object, where the .value is a tuple
        (number_of_passes, total_checks) and .msgs contains error messages
        for any attribute that fails the UTF-8 encoding test.

    Note:
      Only attributes that are Python strings (str) are checked. This is
      sufficient for our purposes as the netCDF4 library converts NC attributes
      to Python types upon reading.
    """
    ctx = TestCtx(severity, "UTF-8 Encoding Validation")
    
    # Check global attributes
    for attr in ds.ncattrs():
        value = ds.getncattr(attr)
        if isinstance(value, str):
            try:
                value.encode("utf-8")
                ctx.assert_true(True)
            except UnicodeError:
                ctx.assert_true(False, f"Global attribute '{attr}' is not valid UTF-8")
    
    # Check attributes for each variable
    for var_name, var_obj in ds.variables.items():
        for attr in var_obj.ncattrs():
            value = getattr(var_obj, attr)
            if isinstance(value, str):
                try:
                    value.encode("utf-8")
                    ctx.assert_true(True)
                except UnicodeError:
                    ctx.assert_true(False, f"Variable '{var_name}' attribute '{attr}' is not valid UTF-8")
    
    return [ctx.to_result()]
