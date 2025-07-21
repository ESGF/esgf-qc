
# A dataset-aware checker for time-axis consistency, inspired by nctime and user-provided scripts.

import os
import re
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

import networkx as nx
import numpy as np
import xarray as xr
from compliance_checker.base import BaseCheck, Result, TestCtx
from netCDF4 import Dataset

# Regex to parse CMIP-style date spans from filenames
DATE_SPAN_RE = re.compile(r"_(\d{6,8})-(\d{6,8})\.nc$", re.I)

class FileTimeInfo:
    """A helper class to store time metadata parsed from filenames."""
    def __init__(self, path: Path):
        self.path = path
        m = DATE_SPAN_RE.search(path.name)
        if not m:
            raise ValueError(f"Filename '{path.name}' does not match expected date pattern.")
        
        start_str, end_str = m.groups()
        self.start_date = self._parse_date(start_str)
        self.end_date = self._parse_date(end_str)

    @staticmethod
    def _parse_date(code: str) -> datetime:
        if len(code) == 6:  # YYYYMM
            return datetime.strptime(code + "01", "%Y%m%d")
        return datetime.strptime(code, "%Y%m%d")

class WCRPTimeCheck(BaseCheck):
    """
    Performs intra-file time checks (continuity, bounds) and inter-file
    dataset checks (gaps, overlaps) using a graph-based approach.
    """
    _cc_spec = "wcrp_time"
    _cc_spec_version = "1.0"
    _cc_description = "Time-axis consistency checks (file and dataset level)"
    supported_ds = [Dataset]

    def __init__(self, options=None):
        super().__init__(options)
        self.files_to_check = self.options.get('dataset_location', [])
        # This will store the results of the one-time dataset analysis
        self._dataset_analysis_results = None

    def setup(self, ds):
        """
        This method is called once. It runs the dataset-level analysis for gaps and overlaps.
        """
        if self._dataset_analysis_results is not None:
            return # Analysis has already been done

        print(f"INFO: Starting dataset-level time analysis on {len(self.files_to_check)} files...")
        
        try:
            files_info = sorted([FileTimeInfo(Path(p)) for p in self.files_to_check], key=lambda fi: fi.start_date)
        except ValueError as e:
            print(f"Warning: Could not parse all filenames for time analysis. {e}")
            self._dataset_analysis_results = {"gaps": ["Error parsing filenames"], "overlaps": []}
            return

        if len(files_info) < 2:
            print("Info: Not enough files to perform dataset-level checks.")
            self._dataset_analysis_results = {"gaps": [], "overlaps": []}
            return
            
        # Build graph using networkx, as inspired by dataset_qc_filen.py
        g = nx.DiGraph()
        for i, fi in enumerate(files_info):
            g.add_node(i, info=fi)
            if i > 0:
                prev_fi = files_info[i-1]
                # A direct connection means the end of the previous file is right before the start of the current one
                # For monthly data, next month's start is what we expect.
                expected_start = prev_fi.end_date.replace(day=1) + pd.DateOffset(months=1)
                if fi.start_date == expected_start:
                    g.add_edge(i-1, i)

        # Find gaps and overlaps by analyzing the graph structure
        gaps = []
        overlaps = []
        for i in range(len(files_info) - 1):
            if not g.has_edge(i, i+1):
                prev_fi = files_info[i]
                curr_fi = files_info[i+1]
                if prev_fi.end_date >= curr_fi.start_date:
                    overlaps.append(f"Overlap between {prev_fi.path.name} and {curr_fi.path.name}")
                else:
                    gaps.append(f"Gap between {prev_fi.path.name} and {curr_fi.path.name}")
        
        self._dataset_analysis_results = {"gaps": gaps, "overlaps": overlaps}
        print("INFO: Dataset-level time analysis complete.")

    # ==============================================================================
    # == DATASET-LEVEL CHECKS 
    # ==============================================================================
    def check_dataset_gaps(self, ds):
        """[DSET_TIM001] Reports any time gaps found between consecutive files."""
        ctx = TestCtx(BaseCheck.HIGH, "[DSET_TIM001] No time gaps between dataset files")
        if self._dataset_analysis_results is None:
            ctx.add_failure("Dataset analysis could not be performed.")
        elif self._dataset_analysis_results["gaps"]:
            for gap_msg in self._dataset_analysis_results["gaps"]:
                ctx.add_failure(gap_msg)
        else:
            ctx.add_pass()
        return ctx.to_result()

    def check_dataset_overlaps(self, ds):
        """[DSET_TIM002] Reports any time overlaps found between consecutive files."""
        ctx = TestCtx(BaseCheck.HIGH, "[DSET_TIM002] No time overlaps between dataset files")
        if self._dataset_analysis_results is None:
            ctx.add_failure("Dataset analysis could not be performed.")
        elif self._dataset_analysis_results["overlaps"]:
            for overlap_msg in self._dataset_analysis_results["overlaps"]:
                ctx.add_failure(overlap_msg)
        else:
            ctx.add_pass()
        return ctx.to_result()

    # ==============================================================================
    # == INTRA-FILE CHECKS 
    # ==============================================================================
    def check_intrafile_continuity(self, ds):
        """[INTRA_TIM001] Checks for regular time steps within this single file."""
        ctx = TestCtx(BaseCheck.MEDIUM, "[INTRA_TIM001] Time axis has regular steps")
        try:
            with xr.open_dataset(ds.filepath(), decode_times=True) as xds:
                if 'time' not in xds or xds.time.size < 3:
                    ctx.add_pass() # Not enough points to check continuity
                    return ctx.to_result()
                
                deltas = pd.Series(xds.time.values).diff().dropna()
                if deltas.nunique(dropna=False) > 1:
                    ctx.add_failure("Time steps are not regular within the file.")
                else:
                    ctx.add_pass()
        except Exception as e:
            ctx.add_failure(f"Could not check time continuity: {e}")
        
        return ctx.to_result()

    def check_intrafile_bounds(self, ds):
        """[INTRA_TIM002] Checks the integrity of the time_bnds variable."""
        ctx = TestCtx(BaseCheck.MEDIUM, "[INTRA_TIM002] Time bounds are consistent")
        try:
            with xr.open_dataset(ds.filepath(), decode_times=True) as xds:
                if 'time' not in xds or 'time_bnds' not in xds.variables:
                    ctx.add_pass() # No bounds to check
                    return ctx.to_result()
                
                time_bnds = xds['time_bnds']
                time_vals = xds['time']

                if time_bnds.shape != (time_vals.size, 2):
                    ctx.add_failure(f"time_bnds shape {time_bnds.shape} is not ({time_vals.size}, 2).")
                
                if np.any(time_bnds.isel(bnds=1) <= time_bnds.isel(bnds=0)):
                     ctx.add_failure("Found time bounds where end_time <= start_time.")

                if not ctx.msgs:
                    ctx.add_pass()

        except Exception as e:
            ctx.add_failure(f"Could not check time bounds: {e}")

        return ctx.to_result()