# ESGF-QC

Quality-control Framework  for WCRP projects, built on top of the IOOS Compliance Checker.

---

## What is it?

ESGF-QC runs a set of **plugins** on NetCDF files to ensure they follow projects and conventions (WCRP/CMIP/Cf/Copernicus...) rules (DRS paths, attributes, data, etc.).  



## Key Features

- **Config-driven**: TOML files decide which checks to run and how strict they are  
- **Modular checks**: dimensions,attributes, variables, time, attributes, DRS and consistency, etc.  
- **Multiple outputs**: text (CLI), HTML reports, Json/Json_new  
- **Extendable**: easy to add new checks or whole project suites


