#!/usr/bin/env python
"""
check_constants.py

Check if the specified netCDF dataset has constant values in the data along specific dimensions.

Intended to be included in the WCRP plugins.
"""

from compliance_checker.base import BaseCheck, TestCtx
import numpy as np
from utilities import (get_filtered_dimensions,
                        check_variable_conditions,
                        prepare_results_generic,
                        dump_data_file)


def check_all_constant(data_slice):
    if np.isscalar(data_slice):
        return True
    elif data_slice.size == 0:
        return False
    else:
        # If it's an array, check if all values are equal to the first one
        return np.all(data_slice == data_slice.flat[0])

def check_constants(dataset, variable,  severity=BaseCheck.MEDIUM):
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

    check_dims=get_filtered_dimensions(dataset,variable)
    # Detect outliers
    values = check_variable_conditions(dataset,variable,check_dims,check_all_constant)
    # Prepare the results
    label="constant"
    results,check=prepare_results_generic(values, predicate=bool, label=label)
    
    ctx.variable = variable
    if check:
        num_constants = results[f'num_{label}s']
        coords_only = [c[0] for c in results[f'{label}_coordinates']]
        coords_string = "\n".join(str(c) for c in coords_only)   
        message = (
            f"Constants values detected in the dataset.\n"
            f"Number of Constants: {num_constants}\n"
            f"Coordinates:\n{coords_string}"
        )
        ctx.add_failure(message)
        ctx.add_failure(f"Constant values detected on the dataset.")
        dump_data_file(dataset, variable, 'check_constant', ctx)


    else:
        ctx.messages.append(f"No constant values detected in the dataset.")
        ctx.add_pass()

    return ctx