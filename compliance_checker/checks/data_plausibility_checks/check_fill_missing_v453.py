#!/usr/bin/env python
"""
check_fill_missing.py

Check if the specified netCDF dataset has FillValue or missing values in the data along specific dimensions.

Intended to be included in the WCRP plugins.
"""

from compliance_checker.base import BaseCheck, TestCtx
import numpy as np
from compliance_checker.checks.data_plausibility_checks.utilities import (get_filtered_dimensions,
                        check_variable_conditions,
                        dump_data_file,
                        prepare_results_expanded,
                        check_variable_conditions_expanded,
                        extract_fail_info_fill_missing)
import numpy.ma as ma

def check_all_nan(data_slice):
    return np.sum(np.isnan(data_slice))

def check_value(data_slice, parameters):
    val = parameters['val']
    val_name = parameters['name']
    if val_name == 'FillValue' or val_name == 'MissingValue':
        filled_data = data_slice.filled(fill_value=val)
    return np.sum(filled_data == val)

def load_value_to_check(var_obj, parameter, ctx):
    # Load the FillValue or MissingValue from the variable attributes
    fill_value = getattr(var_obj, '_FillValue', None)
    missing_value = getattr(var_obj, 'missing_value', None)

    if fill_value is not None and missing_value is not None and fill_value == missing_value:
        ctx.messages.append("Warning: _FillValue and missing_value are the same.")
    if parameter == "FillValue":
        parameters_func = {'val': fill_value, "name": "FillValue"}
        if fill_value is None:
            raise ValueError("FillValue not found in the variable attributes.")  
    elif parameter == "MissingValue":
        parameters_func = {'val': missing_value, "name": "MissingValue"}
    else:
        raise ValueError(f"Invalid parameter {parameter}")
    return parameters_func, ctx

def check_fillvalues_timeseries(dataset, variable, parameter="FillValue", severity=BaseCheck.MEDIUM):
    """
    Check for FillValue or MissingValue in a dataset.

    Parameters:
    - dataset (netCDF4.Dataset): The dataset containing the values to be checked.
    - variable (str): The variable to be checked.
    - parameter (str): The parameter to check, either "FillValue" or "MissingValue".
    - severity : The severity level of the check.

    Returns:
    - TestCtx: A TestCtx object containing the results of the check.

    Notes:
    - This function writes a file with the results of the check when a anomaly in the data is detected.
    """
    ctx = TestCtx(severity, "Check for FillValue or MissingValue in a dataset.")

    ctx.variable = variable
    check_dims = get_filtered_dimensions(dataset, variable)

    var_obj = dataset.variables[variable]

    parameters_func, ctx = load_value_to_check(var_obj, parameter, ctx)
    if parameters_func["val"] is None:
        ctx.add_pass()
        ctx.messages.append(f"{parameter} not found in the variable attributes.")
        return ctx
    
    label = "fill_missing"
    if len(check_dims) > 1:
        nans_coordinates = check_variable_conditions_expanded(dataset, variable, check_dims, check_value, parameters=parameters_func)
    elif len(check_dims) == 1:
        nans_coordinates = {}
        nans_coordinates[parameter] = {}
        nans_coordinates[parameter]["None"] = check_variable_conditions(dataset, variable, check_dims, check_value, parameters=parameters_func)
    results, check, example_fail = prepare_results_expanded(nans_coordinates, predicate=lambda x: x > 0, label=label)
    if check:
        example_fail = extract_fail_info_fill_missing(example_fail)

        message = (
            f"{parameter} detected in the dataset. "
            f"{parameter} are not constant. "
            f"Number of failing times : {example_fail['num_of_failing_times']}. "
            f"Number of {parameter}: {example_fail[f'num_{label}s']}. "
            f"Example coordinates: {example_fail[f'{label}_coordinates']}. "
            f"Example coordinates different count of {parameter}: {example_fail['diff_coordinates']}. "
        )
        ctx.add_failure(message)
        dump_data_file(dataset, variable, 'check_fillvalues', ctx)
    else:
        message = (f"Anomalous {parameter} not detected in the dataset.")
        ctx.add_pass()
        ctx.messages.append(message)

    return ctx
