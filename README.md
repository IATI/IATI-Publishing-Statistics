IATI-Publishing-Statistics
===========================

Tables and files presenting different stats for IATI publishers

Introduction
-------------

This repository contains the split of the IATI-Dashboard and IATI-Publishing-Statistics, as a first iteration it will use code from `IATI-Stats` and `IATI-Dashboard`, whilst relying on data obtained from the `IATI-Registry-Refresher`. This is due to be changed once the new datastore is live, as both the dashboard and publishing statistics will be rebuilt.

Requirements
-------------
- Python 2.7
- python-dev
- python-virtualenv
- pip
- bash
- gcc
- libfreetype6-dev
- libxml2-dev
- libxslt-dev
- lib32z1-dev

Installation and Setup
-----------------------
```
# Get the code
git clone git@github.com:IATI/IATI-Publishing-Statistics.git
cd IATI-Publishing-Statistics

# Set up a virtual environment
virtualenv pyenv
source pyenv/bin/activate

# Install python dependencies using pip
pip install -r requirements.txt
```

After this, run the `setup.sh` script, this relies on `IATI-Registry-Refresher` existing in the same repository as `IATI-Publishing-Statistics`, if you wish to manually set this up, use the following instructions:
```
## ONLY DO THIS IF YOU DON'T WISH TO RUN setup.sh
# Switch to the IATI-Stats directory and create a symlink to your xml files
cd IATI-Stats
ln -s <your xml directory> data

# Set up rulesets, codelists and helper files
cd helpers
git clone https://github.com/IATI/IATI-Rulesets.git
ln -s IATI-Rulesets/rulesets rulesets
ln -s <your ckan metadata directory> ckan
./get_codelist_mapping.sh
./get_codelists.sh
./get_schemas.sh
wget "http://dashboard.iatistandard.org/stats/ckan.json"
wget "https://raw.githubusercontent.com/IATI/IATI-Dashboard/live/registry_id_relationships.csv"
cd ..

# Fetch historical stats files
./get_stats.sh
cd ..

# Switch to the IATI-Dashboard directory and create a symlink to the blacklisted and calculated stats
cd IATI-Dashboard
ln -s ../IATI-Stats/stats-blacklist stats-blacklist
ln -s ../IATI-Stats/outputs stats-calculated
```

Usage
------

To generate new publishing stats, simply run `./generate-publishing-stats.sh`

Alternatively, you may run each step individually
- On `IATI-Registry-Refresher` run `./git.sh`
- On `IATI-Publishing-Statistics/IATI-Stats` run `./git_dashboard.sh`
- On `IATI-Publishing-Statistics/IATI-Dashboard` run `./git.sh`
