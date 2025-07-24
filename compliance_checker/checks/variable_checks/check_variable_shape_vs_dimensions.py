from compliance_checker.base import BaseCheck, TestCtx, Result

def check_variable_shape(var_name, ds, severity):
    ctx = TestCtx(severity, f"[ZZZZZ01]Shape check for '{var_name}'")
    try:
        var = ds.variables[var_name]
        dims = var.dimensions
        shape = var.shape
        expected_shape = tuple(ds.dimensions[dim].size for dim in dims)
        print(f"[DEBUG] Var '{var_name}': shape={shape}, expected={expected_shape}, dims={dims}")
        if shape != expected_shape:
            ctx.add_failure(
                f"Variable '{var_name}' has shape {shape} but expected {expected_shape} "
                f"based on declared dimensions {dims}"
            )
        else:
            ctx.add_pass()
    except KeyError as e:
        ctx.add_failure(f"Missing dimension '{e.args[0]}' used in variable '{var_name}'")
    except Exception as e:
        ctx.add_failure(f"Unexpected error in shape check for '{var_name}': {e}")

    return [ctx.to_result()]
