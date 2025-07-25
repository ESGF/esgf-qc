# ESGF-QC
This project is a QC framework that extends the IOOS Compliance Checker. We forked the IOOS Compliance Checker and are developing our own plugins to support specific checks relevant to our projects.
## ESGF-QC Install

pip install git+https://github.com/ESGF/esgf-qc.git@Ipsl-Develop
esgvoc config set universe:branch=esgvoc_dev
esgvoc install


## Running the ESGF-QC
To run the ESGF-QC , use the following command:  
esgqc --test=''check''  ''filepath''  
Replace ''check'' with the name of the check suite you want to run (e.g., `cf:1.6`) and ''directory_path'' with the path to your netcdf files.
example for CMIP6 : esgqc  --test=wcrp_cmip6:1.0  /home/anachite/Bureau/Datatest/DATA_QC/C3S-CMIP6/tos_Omon_NorESM2-MM_historical_r1i1p1f1_gn_201001-201412.nc 

## Quality Control Checks
The checks are categorized into key areas, including :
* **Dimensional Integrity.** Validation of dimensions like time, latitude, and longitude.
* **Metadata Validation:** Ensuring attributes comply with conventions and controlled vocabularies.
* **Temporal Consistency:** Checking for gaps, overlaps, and monotonicity in time variables.
* **Data Plausibility:** Detecting outliers and ensuring values fall within expected ranges.
* **General Checks:** Ensuring the overall structure, file integrity, and consistency between experiments.

   For a detailed account of the QC checks, we have compiled an inventory available in a Google Sheet. This document includes the categories, severity levels, and tools associated with each check. You can access the full inventory via the following link:
https://docs.google.com/spreadsheets/d/15LytNx3qE7mvuCpyFYAsGFFKqzmm1MH_BoApoqbmLQk/edit?gid=1295657304#gid=1295657304

## Contribution Guidelines

When contributing to this project, please follow these guidelines:

* **Check for Existing Implementations:**
    * **CF Convention:** Check the google sheet table and identify the checks already covered by the CF plugin in the IOOS Compliance Checker. This will prevent us from duplicating effort and ensure consistency.
    * **IOOS CC Functions:** Before implementing a new check, please review the existing functions in the IOOS compliance checker to see if there are any relevant functions that can be reused or adapted to avoid redundancy.
* **Atomic Checks:** Strive to make each check as small and atomic as possible, potentially only a few lines of code, focusing on a single, specific aspect of compliance. This promotes code reusability and maintainability.
* **Error Handling:** Use `try-except` blocks in your checks to handle potential errors gracefully and prevent the code from stopping unexpectedly.
* **WCRP Plugins:** The checks you develop will be called in the project specific scripts under WCRP directory. If you're confident in your understanding of the implementation, you can directly act on the designated script and add your check call, otherwise you can mention it in the pull request and we can assist you in plugging it in.
* **Tests:** For every new check file created, please add a corresponding test file in the `tests` directory to ensure the functionality and correctness of your checks.


## Project Structure
The project is structured as follows:  
**Note:** The checks in the `/checks` directory are not exhaustive and new checks might be added as needed.

```plaintext
📂 compliance_checker  # Core compliance checking logic and plugin system
│   ├── 📂 checks         # Common QC checks shared across projects
│   │   ├── base_check.py  # Abstract base class for checks
│   │   ├── attribute_checks  # Checks related to attributes
│   │   │   ├── check_attribute_existence.py  # Checks the existence of an attribute
│   │   │   ├── check_attribute_type.py  # Checks the type of an attribute
│   │   │   ├── check_attribute_value_format.py  # Checks the format of an attribute value
│   │   │   ├── check_utf8_encoding.py  # Checks if a value is UTF-8 encoded
│   │   │   ├── check_controlled_vocabulary.py  # Checks the consistency with controlled vocabulary
│   │   ├── dimension_checks  # Checks related to dimensions
│   │   │   ├── check_dimension_existence.py  # Checks the existence of a dimension
│   │   │   ├── check_dimension_type.py  # Checks the type of a dimension
│   │   │   ├── check_dimension_value.py  # Checks the value of a dimension
│   │   ├── variable_checks  # Checks related to variables
│   │   │   ├── check_variable_existence.py  # Checks the existence of a variable
│   │   │   ├── check_variable_type.py  # Checks the type of a variable
│   │   │   ├── check_variable_shape.py  # Checks the shape of a variable
│   │   │   ├── check_missing_values.py  # Checks for missing values in a variable
│   │   │   ├── check_monotonicity.py  # Checks the monotonicity of a variable
│   │   │   ├── check_uniqueness.py  # Checks the uniqueness of values in a variable
│   │   │   ├── check_bounds.py  # Checks the bounds of a variable
│   │   ├── dataset_consistency_checks  # Checks related to dataset consistency
│   │   │   ├── check_directory_structure.py  # Checks the directory structure of a dataset
│   │   │   ├── check_filename_format.py  # Checks the filename format of a dataset
│   │   │   ├── check_metadata_consistency.py  # Checks the consistency of metadata across a dataset
│   │   │   ├── check_time_gaps.py  # Checks for time gaps in a dataset
│   │   │   ├── check_file_integrity.py  # Checks the integrity of files in a dataset
│   │   ├── data_plausibility_checks  # Checks related to data plausibility
│   │   │   ├── check_data_plausibility.py  # Checks the range of data values and outliers
│   │   ├── time_checks  # Dedicated file for time-related checks
│   │   │   ├── check_time_monotonicity.py  # Checks if the time variable is monotonic
│   │   │   ├── check_time_uniqueness.py  # Checks if the time values are unique
│   │   │   ├── check_time_bounds.py  # Checks if the time variable has valid bounds
│   │   │   ├── check_time_gaps.py  # Checks for gaps in the time series
│   │   │   ├── check_time_units.py  # Checks the units of the time variable
│   │   │   ├── check_time_calendar.py  # Checks the calendar attribute of the time variable
│   ├── 📂 cf  # CF-specific compliance checks
│   │   ├── cf.py             	# CF compliance logic (CF1.6, CF1.7, CF1.8)
│   │   ├── cf_base.py        	# CF shared utilities
│   │   ├── cf_1_6.py         	# CF 1.6 validation
│   │   ├── cf_1_7.py         	# CF 1.7 validation
│   │   ├── cf_1_8.py         	# CF 1.8 validation
│   │   ├── cfutil.py         	# CF helper functions (units, time)
│   ├── 📂 wcrp  # Project-Specific Plugins
│   │   ├── wcrp_base.py  # Base class for WCRP checks (similar to cf_base.py) / Shared utility functions for WCRP checks
│   │   ├── wcrp_cmip6.py  # CMIP6 specific checks
│   │   ├── wcrp_cmip7.py  # CMIP7 specific checks
│   │   └── wcrp_cordex_cmip6.py  # CORDEX-CMIP6 specific checks
│   ├── 📂 protocols  # Handling different data formats
│   │   └──...  # Modules for NetCDF, OPeNDAP, Zarr, etc.
│   ├── suite.py  # Plugin manager & execution
│   ├── runner.py  # Runs the compliance checks
│   ├── base.py  # Defines scoring & severity levels
│   ├── util.py  # Generic utility functions
│   └── __init__.py  # Package entry
│   ├── 📂 tests  # Unit & integration tests
├── cchecker.py  # CLI Entry Point (outside core package)
├── pyproject.toml  # Registers available plugins dynamically
└── requirements.txt  # Dependencies


