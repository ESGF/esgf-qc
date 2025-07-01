#!/usr/bin/env python
"""
check_nan_inf.py

Check if the specified netCDF dataset has NaN values in the data along specific dimensions.

Intended to be included in the WCRP plugins.
"""

from compliance_checker.base import BaseCheck, TestCtx
import numpy as np
from compliance_checker.checks.data_plausibility_checks.utilities import (
    prepare_results_generic,
    format_example_coords,
    dump_data_file
)


def check_any_nan(data_slice):
    """Check if there are any NaN values in the data slice."""
    return np.any(np.isnan(data_slice))

def check_any_inf(data_slice):
    """Check if there are any infinite values in the data slice."""
    return np.any(np.isinf(data_slice))

def get_nan_coordinates(data_slice):
    """Get the coordinates of all NaN values in the data slice."""
    return np.where(np.isnan(data_slice))

def get_inf_coordinates(data_slice):
    """Get the coordinates of all infinite values in the data slice."""
    return np.where(np.isinf(data_slice))

def check_nan_inf(dataset, variable, parameter="NaN", severity=BaseCheck.MEDIUM):
    """
    Check for nans in a dataset 
    Parameters:
    - dataset (netCDF4.Dataset): The dataset containing the values to be checked.
    - variable (str): The variable to be checked.
    - json_file (str): The path to the JSON file containing the thresholds.
    Returns:
    - dict: A dictionary containing the coordinates and values of detected outliers.
    """

    ctx = TestCtx(severity, "Check for outliers in a dataset based on predefined thresholds.")
    var = dataset.variables[variable]
    var.set_auto_mask(False)
    var.set_auto_scale(False)
    data=var[:]
    fill_value = getattr(var, '_FillValue')
    ctx.variable = variable

    if np.isnan(fill_value):
        message="Warning: _FillValue is NaN. NaN detected, see Fill_value check for more information."
        ctx.add_failure(message)
        return ctx
    if parameter=="NaN":
        check=check_any_nan(data)
    elif parameter=="Inf":
        check=check_any_inf(data)
    
    else:
        raise ValueError(f"Invalid parameter {parameter}")
    if check:
        # Get the coordinates of the detected values
        if parameter == "NaN":
            coords = get_nan_coordinates(data)
        elif parameter == "Inf":
            coords = get_inf_coordinates(data)
        else:
            coords = []
        # Convert to a list of tuples (e.g., [(i, j), ...])
        coord_list = list(zip(*coords))
        results, _ = prepare_results_generic(
            [(coord, True) for coord in coord_list], predicate=bool, label=parameter.lower()
        )
        num_key = f'num_{parameter.lower()}s'
        coord_key = f'{parameter.lower()}_coordinates'
        coords = format_example_coords(results[coord_key])
        coords_str = ''
        for i in coords:
            coords_str += f"{i}\n"
        message = (
            f"{parameter} detected in the dataset.\n"
            f"Number of {parameter}s: {results[num_key]}\n"
            f"Coordinates:\n"
            f"{coords_str}"
        )
        ctx.add_failure(message)
        dump_data_file(dataset, variable, 'check_nan_inf', ctx)
    else:
        ctx.messages.append(f"No {parameter} detected in the dataset.")
        ctx.add_pass()
    return ctx
