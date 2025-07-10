# esgf-qc/compliance_checker/wcrp/wcrp_example_project.py
# =============================================================================
# WCRP project
#
# This module defines a WCRP example compliance checker, which serves as 
# the main entry point for executing a series of validation checks on 
# climate data. It relies on configuration defined in a TOML file and 
# calls a suite of checks developed for quality control

# =============================================================================


import os
import toml
from .wcrp_base import WCRPBaseCheck
from netCDF4 import Dataset
from ..checks.consistency_checks.check_drs_filename import check_drs_filename_cv
from ..checks.attribute_checks.check_attribute_suite import check_attribute_suite
from ..checks.consistency_checks.check_source_consistency import check_source_consistency
class ExampleProjectCheck(WCRPBaseCheck):
    """
    Orchestrates attribute checks based on a TOML configuration where each
    attribute is its own table (e.g., [global_attributes.activity_id]).
    """
    _cc_spec = "wcrp_example"
    _cc_spec_version = "1.0"
    _cc_description = "WCRP Project Checks"
    supported_ds = [Dataset]

    def __init__(self, options=None):
        super().__init__(options)
        if options and 'project_config_path' in options:
            self.project_config_path = options['project_config_path']
        else:
            this_dir = os.path.dirname(os.path.abspath(__file__))
            self.project_config_path = os.path.join(this_dir, "resources", "wcrp_config.toml")

        # Define project name here for vocabulary checks 
        self.project_name = "cmip6"

    def _load_project_config(self):
        """Loads the TOML configuration file."""
        if not self.project_config_path or not os.path.exists(self.project_config_path):
            print(f"Warning: Configuration file path not set or file not found at {self.project_config_path}")
            self.config = {}
            return
        try:
            with open(self.project_config_path, 'r', encoding="utf-8") as f:
                self.config = toml.load(f)
        except Exception as e:
            self.config = {}
            print(f"Error parsing TOML configuration from {self.project_config_path}: {e}")

    def setup(self, ds):
        """Loads the configuration before running checks."""
        super().setup(ds)
        self._load_project_config()

    def check_drs_from_config(self, ds):
        """
        Checks the DRS and filename consistency against ESGVOC vocabulary.
        """
       
        if "drs_cv_check" not in self.config:
            return []
        severity = self.get_severity(self.config["drs_cv_check"].get("severity"))
        return check_drs_filename_cv(ds, severity, project_id=self.project_name)    

    def check_all_attributes_from_config(self, ds):
        
        #Orchestrates checks for both global and variable attributes from the TOML config#
   
        results = []
        if not self.config:
            return results

        global_attrs_config = self.config.get('global_attributes', {})
        for attr_name, attr_config in global_attrs_config.items():
            results.extend(check_attribute_suite(
                ds=ds,
                attribute_name=attr_name,
                severity=self.get_severity(attr_config.get('severity')),
                expected_type=attr_config.get('expected_type'),
                var_name=None,
                project_name=self.project_name  
            ))

        variable_attrs_config = self.config.get('variable_attributes', {})
        for var_name, attributes_to_check in variable_attrs_config.items():
            for attr_name, attr_config in attributes_to_check.items():
                results.extend(check_attribute_suite(
                    ds=ds,
                    attribute_name=attr_name,
                    severity=self.get_severity(attr_config.get('severity')),
                    expected_type=attr_config.get('expected_type'),
                    var_name=var_name,
                    project_name=self.project_name  
                ))

        return results  
    
    
  
