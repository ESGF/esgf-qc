from compliance_checker.base import BaseCheck, TestCtx
import numpy as np

def check_bounds_value_consistency(ds, var_name, severity=BaseCheck.MEDIUM):
    """
    Ensure each value of `var_name` lies within the range specified
    by its corresponding bounds variable, if one is defined.

    Parameters
    ----------
    ds : netCDF4.Dataset
    var_name : str
        Name of the variable to check.
    severity : int
        Severity level.

    Returns
    -------
    List[Result]
    """
    ctx = TestCtx(severity, f"[ZWWZZZZ04] Bounds value consistency for '{var_name}'")

    if var_name not in ds.variables:
        ctx.add_failure(f"Variable '{var_name}' not found in dataset.")
        return [ctx.to_result()]

    var = ds.variables[var_name]
    bnds_name = getattr(var, "bounds", None)

    if not bnds_name:
        ctx.add_pass()
        return [ctx.to_result()]

    if bnds_name not in ds.variables:
        ctx.add_failure(f"Declared bounds variable '{bnds_name}' not found for '{var_name}'.")
        return [ctx.to_result()]

    bnds_var = ds.variables[bnds_name]

    try:
        values = var[:].compressed() if hasattr(var[:], "compressed") else var[:]
        bounds = bnds_var[:]
        lower, upper = bounds[:, 0], bounds[:, 1]

        outside = np.logical_or(values < lower, values > upper)
        if outside.any():
            idx = np.where(outside)[0][:5]  # show only first 5
            examples = ", ".join(
                f"{i}/{values[i]}∉[{lower[i]}, {upper[i]}]" for i in idx
            )
            ctx.add_failure(
                f"{len(idx)} value(s) lie outside declared bounds. Example(s): {examples}"
            )
        else:
            ctx.add_pass()
    except Exception as e:
        ctx.add_failure(f"Error checking bounds for '{var_name}': {e}")

    return [ctx.to_result()]
