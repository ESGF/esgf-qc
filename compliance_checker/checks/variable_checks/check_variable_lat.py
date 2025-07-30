#!/usr/bin/env python3
"""
check_variable_lat.py
------------------------
Verify latitude coordinate in NetCDF files (WCRP compliance style).

Checks implemented
------------------
ID    Description
V030  Existence of variable `lat`
V031  Variable stored as NC_FLOAT (numpy.float32)
V032  Shape matches its own dimension (len(lat) == dim_size)
V033  No missing, Inf, or NaN values
V034  Values are non-decreasing (monotonic)
V035  Values are unique
V036  All values within –90 .. 90
V037  Each value lies within its bounds (lat_bnds)

Run as module (used by runner script)
-------------------------------------
from check_lat_compliance import LatitudeChecks

with Dataset("example.nc", "r") as ds:
    checker = LatitudeChecks()
    results = checker.check_latitude(ds)
    print(results[0])
"""

from compliance_checker.base import BaseCheck, TestCtx
from netCDF4 import Dataset
import numpy as np


class LatitudeChecks(BaseCheck):
    _cc_spec = "LatitudeCompliance"
    _cc_spec_version = "1.0"
    _cc_description = "Checks on the 'lat' variable"
    _cc_priority = BaseCheck.HIGH

    def check_latitude(self, dataset):
        ctx = TestCtx(BaseCheck.HIGH, "Latitude variable compliance checks")

        # V030 – Check if 'lat' variable exists
        if not self._check_existence(dataset, ctx):
            return [ctx.to_result()]

        lat = dataset.variables['lat']

        try:
            self._check_type(lat, ctx)
            self._check_shape(dataset, lat, ctx)
            self._check_no_nan_or_inf(lat, ctx)
            self._check_monotonic(lat, ctx)
            self._check_unique(lat, ctx)
            self._check_range(lat, ctx)
            self._check_bounds(dataset, lat, ctx)
        except Exception as e:
            ctx.add_failure(f"Unexpected error during checks: {e}")

        return [ctx.to_result()]

    def _check_existence(self, dataset, ctx):
        """
        V030 – Ensure the dataset contains a variable named 'lat'.
        """
        if 'lat' not in dataset.variables:
            ctx.add_failure("V030: lat variable missing")
            return False
        ctx.add_pass()
        return True

    def _check_type(self, lat, ctx):
        """
        V031 – Check that 'lat' is stored as float32 (NC_FLOAT).
        """
        if lat.dtype != np.float32:
            ctx.add_failure(f"V031: lat dtype is {lat.dtype}, expected float32")
        else:
            ctx.add_pass()

    def _check_shape(self, dataset, lat, ctx):
        """
        V032 – Ensure the number of latitude values matches the dimension size.
        """
        if len(lat.dimensions) == 0:
            ctx.add_failure("V032: lat has no dimensions")
            return
        dim_name = lat.dimensions[0]
        if dim_name not in dataset.dimensions:
            ctx.add_failure(f"V032: dimension '{dim_name}' not found in dataset")
            return
        if len(dataset.dimensions[dim_name]) != lat.size:
            ctx.add_failure("V032: lat length does not match its dimension")
        else:
            ctx.add_pass()

    def _check_no_nan_or_inf(self, lat, ctx):
        """
        V033 – Check that all latitude values are finite (no NaNs or Infs).
        """
        try:
            vals = lat[:]
            if not np.isfinite(vals).all():
                ctx.add_failure("V033: lat contains NaN or Inf values")
            else:
                ctx.add_pass()
        except Exception as e:
            ctx.add_failure(f"V033: failed to read lat values – {e}")

    def _check_monotonic(self, lat, ctx):
        """
        V034 – Check that latitude values are non-decreasing (monotonic).
        """
        try:
            vals = lat[:]
            if vals.size >= 2:
                diff = np.diff(vals)
                if np.all(diff >= 0):
                    ctx.add_pass()
                elif np.all(diff <= 0):
                    ctx.add_failure("V034: lat values are decreasing")
                else:
                    ctx.add_failure("V034: lat values are not monotonic (they change direction)")
            else:
                ctx.add_pass()
        except Exception as e:
            ctx.add_failure(f"V034: failed to check monotonicity – {e}")

    def _check_unique(self, lat, ctx):
        """
        V035 – Check that all latitude values are unique (no duplicates).
        """
        try:
            vals = lat[:]
            if len(np.unique(vals)) != len(vals):
                ctx.add_failure("V035: lat has duplicate values")
            else:
                ctx.add_pass()
        except Exception as e:
            ctx.add_failure(f"V035: failed to check uniqueness – {e}")

    def _check_range(self, lat, ctx):
        """
        V036 – Check that all latitude values are within valid range [-90, 90].
        """
        try:
            vals = lat[:]
            if not np.all((vals >= -90.0) & (vals <= 90.0)):
                ctx.add_failure("V036: lat out of range −90..90")
            else:
                ctx.add_pass()
        except Exception as e:
            ctx.add_failure(f"V036: failed to check value range – {e}")

    def _check_bounds(self, dataset, lat, ctx):
        """
        V037 – If 'lat_bnds' exists, check each lat is within its bound range.
        """
        if 'lat_bnds' not in dataset.variables:
            ctx.add_pass()  # optional
            return

        try:
            vals = lat[:]
            bnds = dataset.variables['lat_bnds'][:]
            if bnds.ndim != 2 or bnds.shape[1] < 2 or bnds.shape[0] != vals.shape[0]:
                ctx.add_failure("V037: lat_bnds shape mismatch")
                return
            if not np.all((vals >= bnds[:, 0]) & (vals <= bnds[:, 1])):
                ctx.add_failure("V037: lat outside its bounds (lat_bnds)")
            else:
                ctx.add_pass()
        except Exception as e:
            ctx.add_failure(f"V037: failed to check bounds – {e}")
