# Overview & Installation

## Scientific Context
WCRP projects (e.g. CMIP6) generate large volumes of NetCDF files. ESGF-QC provides **conformity checks** to verify that these files follow the specifications (DRS, mandatory attributes, temporal consistency, etc.).

## Architecture in a Nutshell
- **Base framework**: IOOS Compliance Checker
- **Extensions**: `compliance_checker/checks/` contains atomic checks grouped by theme
- **WCRP/Project plugin**: `compliance_checker/wcrp/wcrp_cmip6.py` + TOML configuration

## Requirements
- Python ≥ 3.10
- Standard scientific stack (installed automatically): `netCDF4`, `xarray`, etc.

## Installation
Install ESGF-QC from the Git repository

```bash
pip install git+[https://github.com/ESGF/esgf-qc.git@main]
```
And then install Esgvoc and Universe to get the Controlled Vocabulary (Mandatory)

```bash
esgvoc config set universe:branch=esgvoc_dev
esgvoc install
```

## Verify the installation:
For **esgqc** :
```bash
esgqc --version
# or
python cchecker.py --version
```
For **esgvoc** :
```bash
esgvoc --help
# or
pip show esgvoc
```