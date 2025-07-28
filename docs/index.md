# ESGF-QC
This project is a QC framework that extends the IOOS Compliance Checker. We forked the IOOS Compliance Checker and are developing our own plugins to support specific checks relevant to WCRP projects.

## ⚙️ Install

To get ESGF-QC up and running, follow these steps:

```bash
pip install git+[https://github.com/ESGF/esgf-qc.git@main]
```
And then install Esgvoc and universe to get the Controlled Vocabulary.

```bash
esgvoc config set universe:branch=esgvoc_dev
esgvoc install
```

## 🚀 Running the ESGF-QC
To run the ESGF-QC , use the following command:
```bash  
esgqc --test=''check''  ''filepath'' 
``` 
Example for WCRP CMIP6 plugin : 
```bash
esgqc  --test=wcrp_cmip6:1.0  path/to/data/CMIP6/CMIP/IPSL/IPSL-CM5A2-INCA/historical/r1i1p1f1/Amon/pr/gr/v20240619/pr_Amon_IPSL-CM5A2-INCA_historical_r1i1p1f1_gr_185001-201412.nc
```
## 📖  Quality Control Checks
The checks are categorized into key areas, including :
* **Dimensional Integrity.** Validation of dimensions like time, latitude, and longitude.
* **Metadata Validation:** Ensuring attributes exist and comply with conventions and controlled vocabularies.
* **Temporal Consistency:** Ensure different cheks in time.
* **Data Plausibility:** Detecting outliers and ensuring values fall within expected ranges.
* **General Checks:** Ensuring the overall structure, file integrity, and consistency between experiments.


 🔎 For a detailed account of the QC checks, we have compiled an inventory available in a Google Sheet. This document includes the categories, severity levels, and tools associated with each check. You can access the full inventory via the following link:
🔗 https://docs.google.com/spreadsheets/d/15LytNx3qE7mvuCpyFYAsGFFKqzmm1MH_BoApoqbmLQk/edit?gid=1295657304#gid=1295657304
## 📖  Documentation


## 🤝 Contribution Guidelines

When contributing to this project, please follow these guidelines:

* **Check for Existing Implementations:**
    * **CF Convention:** Check the google sheet table and identify the checks already covered by the CF plugin in the IOOS Compliance Checker. This will prevent us from duplicating effort and ensure consistency.
    * **IOOS CC Functions:** Before implementing a new check, please review the existing functions in the IOOS compliance checker to see if there are any relevant functions that can be reused or adapted to avoid redundancy.
* **Error Handling:** Use `try-except` blocks in your checks to handle potential errors gracefully and prevent the code from stopping unexpectedly.
* **WCRP Plugins:** The checks you develop will be called in the project specific scripts under WCRP directory. If you're confident in your understanding of the implementation, you can directly act on the designated script and add your check call, otherwise you can mention it in the pull request and we can assist you in plugging it in.
* **Tests:** For every new check file created, please add a corresponding test file in the `tests` directory to ensure the functionality and correctness of your checks.



