# Checks Overview

ESGF-QC is built from many **atomic checks**, grouped by category. The plugin just decides which ones to run; each category focuses on a specific aspect of file quality.

---

## Dimension Checks
Verify that required dimensions exist, have a positive/expected size, and match the declared shapes of variables.

## Variable Checks
Ensure variables are present, their shape matches their dimensions, and (when bounds are declared) each value lies **within its bounds**.

## Time Checks
Focus on the `time` axis: presence of bounds with the right shape, and consistency between the time axis and the filename’s time range.

## Attribute Checks
Check that mandatory global and variable attributes are there, correctly typed/encoded, and their values are valid against regex patterns or controlled vocabularies.

## DRS & Consistency Checks
Validate filenames and directory paths and compare with the netcdf file's attributes; verify consistency between attributes like **frequency vs table_id**, `experiment_id`, `institution`, `variant_label`, etc., against project rules/CVs.


---

#Coming Next
- **Data plausibility checks** (e.g. physical plausible, statisctically meaningful, ...).
- **Dataset-level checks** across multiple files (time continuity, no gaps/overlaps, consistent metadata ).

---

## Detailed Inventory
For the full list of checks (IDs, severities), see the spreadsheet :

**🔗[Checks_QC_Table](https://docs.google.com/spreadsheets/d/15LytNx3qE7mvuCpyFYAsGFFKqzmm1MH_BoApoqbmLQk/edit?gid=1447223205#gid=1447223205)**
