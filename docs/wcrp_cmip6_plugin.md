# The `WCRP Project` Plugin 
The WCRP plugin rely on the wcrp_project.py file, which acts as the “conductor” for WCRP projects ((CMIP6 for Beta release, CMIP7, CORDEX, etc. soon)  that calls all the small atomic checks and decides which ones to run, with which severity.

---

## What it does

- **Loads a configuration file** (`wcrp_config.toml`) that lists:
  - Which checks to run (DRS, attributes, variables, time, etc.)
  - The severity/priority of each check (High ''Mandatory''/ Medium ''Optional'' /Low ''Warning'' )
- **Runs the atomic checks** implemented in `compliance_checker/checks/…`
  - Example: dimension existence/size, variable shape, time bounds, filename/DRS consistency, etc.
- **Aggregates results** and returns them to the Compliance Checker core, which formats them (text, html, json…).

---

## TOML configuration files

- **`wcrp_config.toml`**  
  Tells the plugin *what to verify* and *how strict to be*. It’s essentially a checklist with severities.

- **`mapping_variables.toml`**  
  Temporary helper that maps `<table_id>.<variable_id>` to an intermediate “universe”/registry name so we can grab expected info (dimensions, cell_methods, etc.).  
  **This is a stop‑gap** until the necessary information is fully exposed in the ESGVOC vocabulary.

---



## Key takeaway

- The plugin itself doesn’t “do” heavy validation logic—**it orchestrates** the atomic checks using a **config-driven** approach.
- The variable mapping to the “universe” is **temporary**; the goal is to rely directly on ESGVOC vocabularies in the near future.
