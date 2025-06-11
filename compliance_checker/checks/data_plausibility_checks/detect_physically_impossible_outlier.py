#!/usr/bin/env python
"""
detect_physically_impossible_outlier.py

Check if the specified netCDF dataset has physically impossible outliers.

Intended to be included in the WCRP plugins.
"""

from compliance_checker.base import BaseCheck, TestCtx
import numpy as np
import os
import json


def get_lon_lat_time_dimensions(dataset):
    """
    Get the names of the longitude, latitude, and time dimensions.
    Check for variables with axis attributes.

    Parameters:
    - dataset: netCDF4.Dataset object, the opened NetCDF dataset.

    Returns:
    - lon_dim: str, the name of the longitude dimension.
    - lat_dim: str, the name of the latitude dimension.
    - time_dim: str, the name of the time dimension.
    """
    lon_dim = None
    lat_dim = None
    time_dim = None

    # Check for variables with axis attributes
    for var_name, var in dataset.variables.items():
        if hasattr(var, 'axis'):
            if var.axis == 'X':
                lon_dim = var_name
            elif var.axis == 'Y':
                lat_dim = var_name
            elif var.axis == 'T':
                time_dim = var_name
                
    if lon_dim is None or lat_dim is None or time_dim is None:
        raise ValueError("Could not determine longitude, latitude, or time dimensions.")
    
    return lon_dim, lat_dim, time_dim

def get_thresholds_variable(dataset, thresholds_file):
    """
    Get variables in the dataset that have a standard_name matching any field in the JSON file.

    Parameters:
    - dataset: netCDF4.Dataset object, the opened NetCDF dataset.
    - thresholds_file: str, the path to the JSON file containing the outlier definitions.

    Returns:
    - thresholds: dict, the thresholds for the matching variable.
    - matching_var: str, the name of the variable that matches the standard name in the JSON file.

    Raises:
    - ValueError: If no matching variables are found.
    - ValueError: If more than one matching variable is found.
    """
    # Load the JSON file
    thresholds_file = os.path.join(os.path.dirname(__file__), thresholds_file)
    with open(thresholds_file, 'r') as f:
        thresholds = json.load(f)

    # Get the list of standard names from the JSON file
    standard_names = thresholds.keys()

    # List to store matching variables
    matching_vars = []

    # Iterate through the variables in the dataset
    for var_name, var in dataset.variables.items():
        if hasattr(var, 'standard_name'):
            if var.standard_name in standard_names:
                matching_vars.append(var_name)
                standard_name = var.standard_name

    if not matching_vars:
        raise ValueError("No matching variables found in the dataset.")
    if len(matching_vars) > 1:
        raise ValueError("More than one matching variable found in the dataset.")

    return thresholds[standard_name], matching_vars[0]


def detect_outliers(data: np.ndarray, min_threshold: float, max_threshold: float):
    """
    Detect outliers in a numpy array based on predefined thresholds.

    Parameters:
    - data (np.ndarray): The input numpy array to be checked.
    - min_threshold (float): The minimum threshold for the variable.
    - max_threshold (float): The maximum threshold for the variable.

    Returns:
    - outliers: dict, a dictionary containing the coordinates and values of detected outliers.
    """
    
    mask_min = data < min_threshold
    mask_max = data > max_threshold

    outlier_coords_min = np.column_stack(np.where(mask_min))
    outlier_coords_max = np.column_stack(np.where(mask_max))

    outliers = {
        'coordinates': [],
        'values': [],
        'types': []
    }

    if len(outlier_coords_min) > 0:
        outliers['coordinates'].extend(outlier_coords_min)
        outliers['values'].extend(data[mask_min])
        outliers['types'].extend(['min'] * len(outlier_coords_min))


    if len(outlier_coords_max) > 0:
        outliers['coordinates'].extend(outlier_coords_max)
        outliers['values'].extend(data[mask_max])
        outliers['types'].extend(['max'] * len(outlier_coords_max))
    # Calculate the proportion of outliers
    total_data_points = data.size
    num_outliers = len(outliers['values'])
    proportion_outliers = num_outliers / total_data_points

    outliers['proportion'] = proportion_outliers
    return outliers


def extract_outlier_coordinates(dataset, results, lon_dim, lat_dim, time_dim):
    """
    Extract the longitude, latitude, and time values for the outlier indices.

    Parameters:
    - dataset: netCDF4.Dataset object, the opened NetCDF dataset.
    - results: dict, the results from the detect_outliers function.
    - lon_dim: str, the name of the longitude dimension.
    - lat_dim: str, the name of the latitude dimension.
    - time_dim: str, the name of the time dimension.

    Returns:
    - outlier_coords_values: np.ndarray, the coordinate values for the outliers.
    """
    # Access the variables for longitude, latitude, and time

    lon = dataset.variables[lon_dim][:]  
    lat = dataset.variables[lat_dim][:]  
    time = dataset.variables[time_dim][:]  

    # Extract the outlier indices from the results
    outlier_coords= np.array(results["outliers"]["coordinates"])


    # Extract the coordinate values for the outlier indices
    outlier_lon = lon[outlier_coords[:, 2]]
    outlier_lat = lat[outlier_coords[:, 1]]
    outlier_time = time[outlier_coords[:, 0]]

    # Combine the coordinate values into a single array for each set of outliers
    outlier_coords_values = np.column_stack((outlier_time, outlier_lat, outlier_lon))

    return outlier_coords_values


def prepare_results(outliers, thresholds, dataset, variable, number_limit=100000):
    """
    Prepare the results for outliers detection.

    Parameters:
    - outliers: dict, containing the outliers information.
    - thresholds: dict, containing the threshold information.
    - dataset: netCDF4.Dataset object, the opened NetCDF dataset.
    - variable: str, the name of the variable being checked.
    - number_limit: int, the maximum number of outliers to report.

    Returns:
    - results: dict, the prepared results.
    - check: bool, indicating whether outliers were detected.
    """
    lon_dim, lat_dim, time_dim=get_lon_lat_time_dimensions(dataset)
    # Prepare the results
    results = {
        'outliers': {
            'coordinates': outliers['coordinates'],
            'values': outliers['values'],
            'types': outliers['types'],
            'proportion': outliers['proportion']
        },
        'num_outliers': len(outliers['coordinates']),
        'min_threshold': thresholds['min'],
        'max_threshold': thresholds['max']
    }

    if len(results["outliers"]["coordinates"]) > 0:
        outlier_coords_values = extract_outlier_coordinates(dataset, results, lon_dim, lat_dim, time_dim)
        check=True
        print(f"Outliers detected for variable '{variable}'.")
        if len(outlier_coords_values) > number_limit:
            print(f"Too many outliers to write {len(outlier_coords_values)} > limit: {number_limit}")
    else:
        print(f"No outliers detected for variable '{variable}'.")
        check=False
        outlier_coords_values = []

    results["outliers"]["coordinates_values"] = outlier_coords_values
    results['variable'] = variable
    results['unit'] = thresholds['unit']

    return results,check


def check_outliers(dataset, thresholds_file='outliers_thresholds.json', severity=BaseCheck.MEDIUM):
    """
    Check for outliers in a dataset based on predefined thresholds.

    Parameters:
    - dataset: netCDF4.Dataset object, the dataset containing the values to be checked.
    - thresholds_file: str, the path to the JSON file containing the thresholds.
    - severity: int, the severity level of the check.

    Returns:
    - results: list, a list containing the results of the check.
    """
    ctx = TestCtx(severity, "Check for outliers in a dataset based on predefined thresholds.")

    try:
        thresholds, variable = get_thresholds_variable(dataset, thresholds_file)
    except ValueError as e:
        ctx.add_failure(str(e))
        return [ctx.to_result()]

    data = dataset.variables[variable][:]
    outliers = detect_outliers(data, thresholds['min'], thresholds['max'])


    try:
        # Prepare the results
        results, check = prepare_results(outliers, thresholds, dataset, variable)
    except Exception as e:
        ctx.add_failure(f"Error preparing results: {e}")
        return [ctx.to_result()]

    if check:
        ctx.add_failure(f"Physically impossible outliers detected in the dataset."
                        f"Example, value:{results['outliers']['values'][0]},coordinates:{results['outliers']['coordinates_values'][0]} " 
                        f"for a total of {results['num_outliers']} outliers and thresholds parameters:{thresholds}")
    else:
        ctx.add_pass()

    return [ctx.to_result()]
