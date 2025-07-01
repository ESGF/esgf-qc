import numpy as np
import netCDF4 as nc
import json
import itertools
import os


def get_ds_dimensions(dataset):
    """
    Get the names of the longitude, latitude, time, and z dimensions.
    Check for variables with axis attributes or common dimension names.

    Parameters:
    - dataset: netCDF4.Dataset object, the opened NetCDF dataset.

    Returns:
    - dict: A dictionary with keys 'x_dim', 'y_dim', 'time_dim', and 'z_dim'.
    """
    # Constants for axis names
    AXIS_NAMES = ("X", "Y", "Z", "T")

    # Initialize dimension names
    dimensions = {
        'x_dim': None,
        'y_dim': None,
        'time_dim': None,
        'z_dim': None,
        'member_dim': None,
    }

    # Check for variables with axis attributes or common names
    for var_name, var in dataset.variables.items():
        # Check axis attribute
        if hasattr(var, 'axis'):
            axis = var.axis
            if axis in AXIS_NAMES:
                if axis == 'X':
                    dimensions['x_dim'] = var_name
                elif axis == 'Y':
                    dimensions['y_dim'] = var_name
                elif axis == 'T':
                    dimensions['time_dim'] = var_name
                elif axis == 'Z':
                    dimensions['z_dim'] = var_name

        # Check common dimension names if axis attribute is not present
        if dimensions['x_dim'] is None and var_name.lower() in ['lon', 'longitude',"x"]:
            dimensions['x_dim'] = var_name
        if dimensions['y_dim'] is None and var_name.lower() in ['lat', 'latitude',"y"]:
            dimensions['y_dim'] = var_name
        if dimensions['time_dim'] is None and var_name.lower() in ['time']:
            dimensions['time_dim'] = var_name
        if dimensions['z_dim'] is None and var_name.lower() in ['z', 'depth', 'level']:
            dimensions['z_dim'] = var_name

    if 'member' in dataset.dimensions:
        dimensions['member_dim'] = 'member'
    # Raise an error if any of the essential dimensions are not found
    if None in [dimensions['x_dim'], dimensions['y_dim'], dimensions['time_dim']]:
        raise ValueError("Could not determine longitude, latitude, or time dimensions.")
    # Drop keys with None values before returning
    dimensions = {k: v for k, v in dimensions.items() if v is not None}
    return dimensions




def get_filtered_dimensions(dataset, variable_name):
    """
    Get the filtered dimensions of a variable in a NetCDF file, excluding longitude and latitude dimensions.

    Parameters:
    - dataset: netCDF4.Dataset object, the opened NetCDF dataset.
    - variable_name: str, the name of the variable in the NetCDF file.

    Returns:
    - filtered_dimensions: list, the filtered list of dimension names.
    """

    # Choose a variable
    variable = dataset.variables[variable_name]

    # Get the longitude, latitude, and time dimensions
    dimensions= get_ds_dimensions(dataset)
    x_dim = dimensions['x_dim']
    y_dim = dimensions['y_dim']
 
    # Get the list of dimension names for the variable
    dimension_names = list(variable.dimensions)

    # Filter out the longitude and latitude dimensions
    filtered_dimensions = [dim for dim in dimension_names if dim not in [x_dim, y_dim]]

    return filtered_dimensions



def get_var_dimensions(dataset,variable):
    """
    Compare the dimensions of a specific variable with the dataset dimensions.

    Parameters:
    - dataset: netCDF4.Dataset object, the opened NetCDF dataset.
    - variable: str, the name of the variable to compare dimensions.

    Returns:
    - dict: A dictionary with the same keys as dataset_dims but only with the dimensions that exist in the variable.

    Raises:
    - ValueError: If the variable dimensions are not a subset of the dataset dimensions.
    """

    var_dims=dataset.variables[variable].dimensions
    ds_dims=get_ds_dimensions(dataset)
    # Check if variable dimensions are a subset of dataset dimensions
    if not all(dim in ds_dims.values() for dim in var_dims):
        raise ValueError("The variable dimensions are not a subset of the dataset dimensions.")

    # Create a dictionary with the same keys as dataset_dims but only with the dimensions that exist in the variable
    common_dims = {key: value for key, value in ds_dims.items() if value in var_dims}

    return common_dims

def get_dimension_indices(dataset, variable):
    """
    Get the index positions of the dimensions for a specific variable in a NetCDF dataset.

    Parameters:
    - dataset: netCDF4.Dataset object, the opened NetCDF dataset.
    - variable: str, the name of the variable to get dimension indices for.

    Returns:
    - dict: A dictionary with dimension names as keys and their index positions as values.
    """
    # Get the variable object
    var = dataset.variables[variable]

    # Get the dimension names of the variable
    dim_names = var.dimensions

    # Create a dictionary to store dimension indices
    dim_indices = {dim_name: idx for idx, dim_name in enumerate(dim_names)}

    return dim_indices

def get_dimension_info(dataset, variable):
    """
    Get a dictionary with dimension names and the indices for a specific variable.

    Parameters:
    - dataset: netCDF4.Dataset object, the opened NetCDF dataset.
    - variable: str, the name of the variable to get dimension info for.

    Returns:
    - dict: A dictionary with keys from ds_dims and values as {'name': dimension_name, 'index': dimension_index}.
    """
    ds_dims = get_ds_dimensions(dataset)
    dim_indices = get_dimension_indices(dataset, variable)

    dimension_info = {}

    for key, dim_name in ds_dims.items():
        if dim_name in dim_indices:
            dimension_info[key] = {
                'name': dim_name,
                'i': dim_indices[dim_name]
            }

    return dimension_info


def check_variable_conditions_expanded(dataset, variable_name,check_dims,check_func,data=None,parameters=None):
    """
    Check values for any combination of specified dimensions and collect results of a given function for every aditional dimension to lon,lat and time

    Parameters:
    - dataset: netCDF4.Dataset
        The NetCDF dataset to check.
    - variable_name: str
        Name of the variable to check.
    - check_dims: list of str
        List of dimensions to check combinations of (e.g., ['time', 'member']).
    - check_func: function
        A function that takes a data slice and returns a boolean or numerical result.

    Returns:
    - list of tuples or list of coordinates
        Depending on the return type of check_func, returns coordinates or tuples containing coordinates and numerical results.
    """
    if data is None:
        data = dataset.variables[variable_name][:]

    data=dataset.variables[variable_name] 
    basic_dimensions=["x_dim","y_dim","time_dim"]
    ds_dims=get_ds_dimensions(dataset)
    basic_dims_name = [value for key, value in ds_dims.items() if key in basic_dimensions]

    additional_dimensions = [k for k in check_dims if k not in basic_dims_name]
    check_dims_slice=[k for k in check_dims if k not in additional_dimensions]
        # Generate all combinations of indices for the dimensions
    combinations = list(itertools.product(*[range(len(dataset.dimensions[dim])) for dim in additional_dimensions]))

    # Create a nested dictionary to store the dimension combinations and their coordinates
    combination_dict = {}
    # Populate the dictionary
    for combo in combinations:
        # Create a string representation of the combination name
        combination_name = ', '.join(additional_dimensions)

        # Create a dictionary to map the combination indices to their data values
        if combination_name not in combination_dict:
            combination_dict[combination_name] = {}

        # Create a key for the inner dictionary
        combo_key = ', '.join(map(str, combo))

        data_slice=data[combo]

        combination_dict[combination_name][combo_key] =check_variable_conditions(dataset, variable_name, check_dims_slice, check_func,data=data_slice,parameters=parameters)

    return combination_dict

def check_variable_conditions(dataset, variable_name, check_dims, check_func,data=None,parameters=None):
    """
    Check values for any combination of specified dimensions and collect results of a given function.

    Parameters:
    - dataset: netCDF4.Dataset
        The NetCDF dataset to check.
    - variable_name: str
        Name of the variable to check.
    - check_dims: list of str
        List of dimensions to check combinations of (e.g., ['time', 'member']).
    - check_func: function
        A function that takes a data slice and returns a boolean or numerical result.

    Returns:
    - list of tuples or list of coordinates
        Depending on the return type of check_func, returns coordinates or tuples containing coordinates and numerical results.
    """
    if data is None:
        variable = dataset.variables[variable_name][:]
    else:
        variable=data
    var_dim_names = dataset.variables[variable_name].dimensions
    check_dim_indices = [var_dim_names.index(dim) for dim in check_dims]
    slices = [slice(None)] * variable.ndim
    results = []

    # Generate all combinations of indices
    index_combinations = np.ndindex(*[variable.shape[i] for i in check_dim_indices])

    for indices in index_combinations:
        for idx, dim_index in enumerate(check_dim_indices):
            slices[dim_index] = indices[idx]
        data_slice = variable[tuple(slices)]
        if parameters is not None:
            result = check_func(data_slice,parameters)
        else:
            result = check_func(data_slice)    
        if isinstance(result, bool):
            # If the result is a boolean, store indices where the condition is True
            if result:
                results.append(indices)
        else:
            # If the result is numerical, store both the indices and the result
            results.append((indices, result))

    return results


def transform_of_tuples(list_tuple):
    # Transform to a list of tuples with regular integers
    transformed_list_tuple= [(int(x), int(y)) for x, y in list_tuple]
    return transformed_list_tuple


def format_coordinates(indices):
    # indices = extract_outlier_indices(coords)
    indices = [tuple(int(x) for x in idx) for idx in indices]
    return set(indices[:5]) if indices else set()


def prepare_results_expanded(coordinate_values, predicate, label="detected"):
    """
    Prepare expanded results for detections. It returns a dictionary of generic results dictionaries
    for every aditional dimension detected with check_variable_conditions_expanded.
    Parameters:
    - coordinate_values: dict of (dim_combination:dim_indices) or list of (coordinate, value)
    - predicate: function that returns True if value is detected
    - label: str, label for the result dictionary key
    Returns:
    - results: dict
    - check: bool
    """
    dict_results = {}
    check_general=False
    example_fail=None
    if isinstance(coordinate_values, dict)  and  len(coordinate_values) == 1:
       single_key = next(iter(coordinate_values))
       dict_results[single_key] = {}
       for dim_combination, values in coordinate_values[single_key].items():
          results, check = prepare_results_generic(coordinate_values[single_key][dim_combination], predicate, label=label)
          
          dict_results[single_key][dim_combination] = results
          if check:
              check_general=True
              example_fail=results
              
    else:
        raise ValueError("coordinate_values must be a dictionary")
    
    return dict_results, check_general, example_fail


def detect_changes_in_values(coordinate_values):
    """
    Detects coordinates where the values change in a list of coordinate-value pairs.

    Parameters:
    coordinate_values (list of tuples): A list of tuples where each tuple is (coordinate, value).

    Returns:
    list: A list of tuples where the values change.
    """
    if not coordinate_values:
        return []

    coordinates, values = zip(*coordinate_values)
    values_array = np.array(values)

    # Compute the differences between consecutive values
    diff_values = np.diff(values_array)

    # Find the indices where the differences are not zero
    non_zero_diff_indices = np.nonzero(diff_values)[0]

    # Adjust indices to match the original array
    non_zero_diff_indices = non_zero_diff_indices + 1

    # Get the coordinates where the values are not the same
    detected = [coordinate_values[i] for i in non_zero_diff_indices]

    # Include the first element if it's different from the second
    if len(values_array) > 1 and values_array[0] != values_array[1]:
        detected.insert(0, coordinate_values[0])
    return detected

def prepare_results_generic(coordinate_values, predicate, label="detected"):
    """
    Prepare generic results for detections.
    Parameters:
    - coordinate_values: list of (coordinate, value)
    - predicate: function that returns True if value is detected
    - label: str, label for the result dictionary key
    Returns:
    - results: dict
    - check: bool
    """
    detected = [(coord, val) for coord, val in coordinate_values if predicate(val)]
    # Check if the second value of the first tuple is an integer
    if detected and isinstance(detected[0][1], (int, np.integer)):
        # Sum the second elements of the tuples if they are integers
        total = sum(int(value) for _, value in detected if isinstance(value, (int, np.integer)))
    else:
        total = len(detected)
    results = {
        f"{label}_coordinates": detected,
        f"num_{label}s": total,
        f"num_of_failing_times": len(detected)
    }
    if label=="fill_missing":
        detected_diff = detect_changes_in_values(coordinate_values)
        results[f"diff_coordinates"] = detected_diff
        results[f"diff_num"] = len(detected_diff)
    check = len(detected) > 0
    return results, check


def format_example_coords(coords, max_examples=5):
    """
    Formats a list of coordinates to show examples in messages.
    - coords: list of tuples or list of pairs (tuple, bool/array).
    - max_examples: maximum number of examples to display.
    """
    # If coords is a list of (tuple, bool/array), extract only the tuple
    if coords and isinstance(coords[0], (list, tuple)) and len(coords[0]) == 2:
        # If the first element is a tuple of ints, use it
        if isinstance(coords[0][0], (list, tuple)):
            indices = [tuple(int(x) for x in c[0]) for c in coords]
        else:
            indices = [tuple(int(x) for x in c) for c in coords]
    else:
        indices = [tuple(int(x) for x in c) for c in coords]
    return indices[:max_examples] if indices else []


def dump_data_file(dataset, variable, check_name, ctx):
    """
    Dumps the results of a check to a file.
    Parameters:
    - dataset: netCDF4.Dataset or similar object, the dataset being checked.
    - variable: str, the name of the variable being checked.
    - check_name: str, the name of the check being performed.
    - ctx: TestCtx, the context containing messages and results of the check.
    """

    try:
        dataset_path = dataset.filepath() if hasattr(dataset, "filepath") else str(variable)
    except Exception:
        dataset_path = str(variable)
    dataset_name = os.path.splitext(os.path.basename(dataset_path))[0]
    reports_dir = "reports"
    os.makedirs(reports_dir, exist_ok=True)
    filename = os.path.join(
        reports_dir,
        f"{dataset_name}_{check_name}_fail.txt"
    )
    with open(filename, "w") as f:
        f.write(f"Test: {check_name}\n")
        f.write(f"File: {dataset_path}\n")
        f.write("Messages:\n")
        for msg in ctx.messages:
            f.write(f"{msg}\n")
        if hasattr(ctx, "failures"):
            f.write("Failures:\n")
            for fail in ctx.failures:
                f.write(f"{fail}\n")
        f.write(f"Score: {ctx.score}\n")



def extract_fail_info_fill_missing(example_fail):
    if isinstance(example_fail, dict):
        for k, v in example_fail.items():
            if k.endswith("_coordinates"):
                example_fail[k] = [coord for coord in format_example_coords(v)]
            elif k.startswith("num_"):
                example_fail[k]= v 
            
    return example_fail