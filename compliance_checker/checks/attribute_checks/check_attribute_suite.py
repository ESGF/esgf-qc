#!/usr/bin/env python

#check_attribute_suite.py


from compliance_checker.base import BaseCheck, Result, TestCtx
import numpy as np
from esgvoc import api as voc

def check_attribute_suite(
    ds,
    attribute_name,
    severity,
    expected_type=None,
    var_name=None,
    project_name=None  # <- Ajouté pour vocabulaire ATTR004
):
    """
    Runs a basic suite of checks on a single attribute:
    1. Existence (ATTR001)
    2. Type (ATTR002) - if expected_type is provided
    3. UTF-8 Encoding (ATTR003) - for strings only
    4. Vocabulary Compliance (ATTR004) - for  attributes without pattern
    """
    #print(f" Running attribute check for: {attribute_name}")
    all_results = []
    
    # --- Check 1: Existence (ATTR001) ---
    existence_ctx = TestCtx(severity, f"[ATTR001] Existence: {'Global' if var_name is None else 'Var ' + var_name} Attribute '{attribute_name}'")
    attr_value = None
    try:
        if var_name:
            if var_name not in ds.variables:
                existence_ctx.add_failure(f"Cannot check attribute '{attribute_name}' because variable '{var_name}' does not exist.")
                all_results.append(existence_ctx.to_result())
                return all_results
            attr_value = ds.variables[var_name].getncattr(attribute_name)
        else:
            attr_value = ds.getncattr(attribute_name)
        existence_ctx.add_pass()
        all_results.append(existence_ctx.to_result())
    except AttributeError:
        existence_ctx.add_failure(f"Attribute '{attribute_name}' is missing.")
        all_results.append(existence_ctx.to_result())
        return all_results

    # --- Check 2: Type (ATTR002) ---
    if expected_type:
        type_ctx = TestCtx(severity, f"[ATTR002] Type: Attribute '{attribute_name}' (expected {expected_type})")
        type_map = {"str": str, "int": (int, np.integer), "float": (float, np.floating),}
        py_type = type_map.get(str(expected_type).lower())

        if py_type and isinstance(attr_value, py_type):
            type_ctx.add_pass()
        elif not py_type:
            type_ctx.add_failure(f"Configuration error: unknown expected_type '{expected_type}'.")
        else:
            type_ctx.add_failure(f"Value has type {type(attr_value).__name__}, expected {py_type.__name__}.")
        all_results.append(type_ctx.to_result())

    # --- Check 3: UTF-8 Encoding (ATTR003) ---
    if isinstance(attr_value, str):
        utf8_ctx = TestCtx(severity, f"[ATTR003] UTF-8 Encoding: Attribute '{attribute_name}'")
        try:
            attr_value.encode('utf-8')
            utf8_ctx.add_pass()
        except UnicodeEncodeError:
            utf8_ctx.add_failure("Attribute contains non-UTF-8 characters.")
        all_results.append(utf8_ctx.to_result())

    # --- Check 4: ESGVOC Vocabulary (ATTR004) ---
    if isinstance(attr_value, str) and expected_type == "str" and project_name:
        
        vocab_ctx = TestCtx(severity, f"[ATTR004] Vocabulary: Attribute '{attribute_name}'")

        try:
            is_valid = voc.valid_term_in_collection(
                value=attr_value,
                project_id=project_name,
                collection_id=attribute_name
            )
            print(is_valid)
            if is_valid:
                vocab_ctx.add_pass()
            else:
                vocab_ctx.add_failure(f"Value '{attr_value}' is not valid in collection '{attribute_name}' for project '{project_name}'.")
        except Exception as e:
            vocab_ctx.add_failure(f"Vocabulary validation failed: {str(e)}")

        all_results.append(vocab_ctx.to_result())

    return all_results
