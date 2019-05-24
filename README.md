IATI-Publishing-Statistics
===========================

Tables and files presenting different stats for IATI publishers

Introduction
-------------

This repository will contain the split of the IATI-Dashboard and IATI-Publishing-Statistics, as a first iteration it will use code from IATI-Stats and IATI-Dashboard, whilst relying on data obtained from the IATI-Registry-Refresher. This is due to be changed once the new datastore is live and a refactor around it will take place.

Process
--------

- Remove decorators from `IATI-Stats/stats/dashboard.py` that will not be used by Publishing-Statistics, bearing in mind that some of the generated json files rely on each other to calculate further stats.
- Modify publishing statistics python scripts from `IATI-Dashboard` to ensure they load the required files.
- Import any common modules from the standalone version of `IATI-Dashboard` that will not require changes. 
- Remove unnecessary templates from `IATI-Dashboard/static/templates`.
- Define an index page for Publishing Statistics
- Link publishers to their dashboard publisher page from the tables in Publishing-Statistics
- Remove additional functions that aid in the generation of unused stats.
- Clear other modules and modify scripts to only generate publishing statistics.
