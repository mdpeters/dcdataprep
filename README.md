## Scripts for prepping data for DAMS ingest

### geocheck.py
Goes through the subject:geographic columns looking for subject headings that
are not referenced in local geo.csv file. New headings are appended to the end
of a copy of the current geo.csv as geo_updated.csv. New geographic subject
headings are reconciled manually.

### dcdataprep.py
Goes through data of DAMS output csv of Marc data (marcxml -> LOC mods xslt (with
local modifications) -> DAMS data model).
* Attempts to create begin and end dates based on the Date field.
* Standarizes "circa" and "between" date expressions
* Adds local identifier scarare
* Reconciles geographic subjects against geo.csv list converting headings
over to preferred form.
