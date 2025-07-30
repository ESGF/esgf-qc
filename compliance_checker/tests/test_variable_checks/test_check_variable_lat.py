#!/usr/bin/env python3
"""
test_check_variable_lat.py
---------------------------
Run latitude compliance checks on all test CDL/NC files defined in STATIC_FILES.

Supports:
- --filekey <key>     : Run only on one STATIC_FILES entry
- --indir <folder>    : Run on all .cdl and .nc in a folder
- Default (no args)   : Run on ALL entries in STATIC_FILES
"""

import argparse
from pathlib import Path
from netCDF4 import Dataset
from compliance_checker.checks.variable_checks.check_variable_lat import LatitudeChecks
from compliance_checker.base import BaseCheck
from compliance_checker.tests.resources import STATIC_FILES
import subprocess
import os


def convert_cdl_to_nc(cdl_path):
    """Convert .cdl to .nc using ncgen and return the path to the .nc file."""
    nc_path = Path(str(cdl_path).replace(".cdl", ".nc"))
    if not nc_path.exists():
        try:
            subprocess.run(["ncgen", "-4", "-o", str(nc_path), str(cdl_path)], check=True)
        except subprocess.CalledProcessError as e:
            print(f"ERROR converting {cdl_path.name}: {e}")
            return None
    return nc_path


def run_checks(nc_path, label=None):
    """Run LatitudeChecks on a NetCDF file."""
    checker = LatitudeChecks()
    try:
        with Dataset(nc_path, 'r') as ds:
            results = checker.check_latitude(ds)
            result = results[0]
            name = label or Path(nc_path).name
            if result.msgs:
                print(f"FAIL  {name}")
                for msg in result.msgs:
                    print(f"   - {msg}")
                return "FAIL"
            else:
                print(f"PASS  {name}")
                return "PASS"
    except Exception as e:
        print(f"ERROR {label or nc_path}: {e}")
        return "ERROR"


def main():
    parser = argparse.ArgumentParser(description="Latitude compliance checker")
    parser.add_argument("--filekey", help="Run only this key from STATIC_FILES")
    parser.add_argument("--indir", help="Directory of .nc/.cdl files")
    args = parser.parse_args()

    counters = {"PASS": 0, "FAIL": 0, "ERROR": 0}
    files_to_check = []

    # Case 1: specific filekey
    if args.filekey:
        if args.filekey not in STATIC_FILES:
            print(f"ERROR: filekey '{args.filekey}' not found in STATIC_FILES")
            return
        f = STATIC_FILES[args.filekey]
        if f.suffix == ".cdl":
            nc_path = convert_cdl_to_nc(f)
            if nc_path:
                files_to_check.append((nc_path, args.filekey))
        elif f.suffix == ".nc":
            files_to_check.append((f, args.filekey))

    # Case 2: directory scan
    elif args.indir:
        indir = Path(args.indir)
        if not indir.exists():
            print(f"ERROR: directory '{indir}' does not exist")
            return
        for f in indir.glob("*.cdl"):
            nc_path = convert_cdl_to_nc(f)
            if nc_path:
                files_to_check.append((nc_path, f.name))
        for f in indir.glob("*.nc"):
            files_to_check.append((f, f.name))

    # Case 3: default — all STATIC_FILES
    else:
        for key, f in STATIC_FILES.items():
            if f.suffix == ".cdl":
                nc_path = convert_cdl_to_nc(f)
                if nc_path:
                    files_to_check.append((nc_path, key))
            elif f.suffix == ".nc":
                files_to_check.append((f, key))

    # Run checks
    for path, label in files_to_check:
        status = run_checks(path, label=label)
        counters[status] += 1

    # Summary
    print("\nSummary")
    for k, v in counters.items():
        print(f"{k:<5}: {v}")


if __name__ == "__main__":
    main()
