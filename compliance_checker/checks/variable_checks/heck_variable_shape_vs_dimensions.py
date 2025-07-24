from compliance_checker.base import BaseCheck, TestCtx, Result

def check_variable_shape_vs_dimensions(ds, severity=BaseCheck.HIGH):
    """
    Check that each variable's shape aligns with its declared dimensions.
    """
    ctx = TestCtx(severity, "Variable shape matches dimension sizes")
    
    for var_name in ds.variables:
        var = ds.variables[var_name]
        dims = var.dimensions
        shape = var.shape

        expected_shape = tuple(ds.dimensions[dim].size for dim in dims)

        if shape != expected_shape:
            ctx.add_failure(
                f"Variable '{var_name}' has shape {shape} but expected {expected_shape} "
                f"based on dimensions {dims}"
            )

    if not ctx.failures:
        ctx.add_pass()

    return [ctx.to_result()]
