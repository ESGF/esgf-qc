#!/usr/bin/env python
"""
check_zscore.py

Check for outliers in the specified netCDF dataset based on the Z-Score along specific dimensions.
"""

from compliance_checker.base import BaseCheck, TestCtx
import numpy as np
from compliance_checker.checks.data_plausibility_checks.utilities import (get_filtered_dimensions,
                         check_variable_conditions,
                         get_dimension_indices,
                         get_ds_dimensions,
                         dump_data_file,
                         prepare_results_expanded,
                         check_variable_conditions_expanded,
                         format_coordinates)

def calculate_zscore(data_slice):
    """Calculate the Z-Score for a given data slice."""
    mean = np.mean(data_slice)
    std = np.std(data_slice)
    if std == 0:
        return np.zeros_like(data_slice)  # Avoid division by zero
    return (data_slice - mean) / std

def is_outlier(zscore, threshold=5):
    """Determine if a Z-Score is an outlier."""
    return np.abs(zscore) > threshold

def calculate_time_series_max_min(dataset, variable):
    """
    Calculate the maximum and minimum time series along the time axis.

    Parameters:
    - dataset (netCDF4.Dataset): The dataset containing the values to be checked.
    - variable (str): The variable to be checked.

    Returns:
    - tuple: A tuple containing the max and min time series.
    """
    i_time = get_dimension_indices(dataset, variable)["time"]
    variable_data = dataset.variables[variable][:]
    max_time_series = np.max(variable_data, axis=i_time)
    min_time_series = np.min(variable_data, axis=i_time)

    return max_time_series, min_time_series

def is_outlier_bool(val):
    """Return True if there is any outlier (True value) in the result of the slice."""
    if isinstance(val, np.ndarray):
        return np.any(val)
    return bool(val)

def extract_outlier_indices(outlier_coordinates):
    # outlier_coordinates: [((), masked_array)]
    indices = []
    for coord, mask in outlier_coordinates:
        # mask is a boolean array, find True values
        if hasattr(mask, 'shape') and mask.shape != ():  # 2D or higher array
            outlier_idx = np.argwhere(mask)
            for idx in outlier_idx:
                indices.append(tuple(idx))
        elif mask:  # scalar True
            indices.append(coord)
    return indices

def check_zscore(dataset, variable, severity=BaseCheck.MEDIUM, threshold=5):
    """
    Check for outliers in a dataset based on Z-Score.

    Parameters:
    - dataset (netCDF4.Dataset): The dataset containing the values to be checked.
    - variable (str): The variable to be checked.
    - severity: Severity level for the check.
    - threshold (float): The Z-Score threshold to consider a value an outlier.

    Returns:
    - TestCtx: A TestCtx object containing the results of the check.

    Notes:
    - This function writes a file with the results of the check when a anomaly in the data is detected.
    """
    ctx = TestCtx(severity, f"Check for outliers in a dataset based on Z-Score with threshold {threshold}.")
    dim_dict = get_ds_dimensions(dataset)
    check_dims = get_filtered_dimensions(dataset, variable)
    max_ts, min_ts = calculate_time_series_max_min(dataset, variable)

    def zscore_condition(data_slice):
        zscores = calculate_zscore(data_slice)
        return is_outlier(zscores, threshold)

    ctx.variable = variable
    check_dims.remove(dim_dict['time_dim'])
    if len(check_dims) > 0:
        # Detect outliers
        values_max = check_variable_conditions_expanded(dataset, variable, check_dims, zscore_condition, max_ts)
        values_min = check_variable_conditions_expanded(dataset, variable, check_dims, zscore_condition, min_ts)
    elif len(check_dims) == 0:
        values_max = {}
        values_max["timeseries"] = {}
        values_min = {}
        values_min["timeseries"] = {}
        values_max["timeseries"]["max"] = check_variable_conditions(dataset, variable, check_dims, zscore_condition, max_ts)
        values_min["timeseries"]["min"] = check_variable_conditions(dataset, variable, check_dims, zscore_condition, min_ts)

    # Prepare the results
    results_max, check_max, example_fail_max = prepare_results_expanded(values_max, predicate=is_outlier_bool, label='outlier')
    results_min, check_min, example_fail_min = prepare_results_expanded(values_min, predicate=is_outlier_bool, label='outlier')

    if check_max or check_min:
        messages = []
        coords = set()
        if check_min:
            coords.update(format_coordinates(extract_outlier_indices(example_fail_min.get('outlier_coordinates', []))))
            messages.append(f"Outliers detected in the dataset based on min timeseries Z-Score.\n")

        if check_max:
            coords.update(format_coordinates(extract_outlier_indices(example_fail_max.get('outlier_coordinates', []))))
            messages.append(f"Outliers detected in the dataset based on max timeseries Z-Score.\n")

        coords_string = "\n".join(str(c) for c in coords)
        num_outliers = len(coords)
      
        messages.append(
            f"Number of outliers: {num_outliers}.\n"
            f"Outliers found in the coordinates:\n{coords_string}."
        )

        ctx.add_failure("\n".join(messages))
        dump_data_file(dataset, variable, 'check_zscore', ctx)
    else:
        ctx.messages.append(f"No outliers detected in the dataset based on Z-Score.")
        ctx.add_pass()

    return ctx
