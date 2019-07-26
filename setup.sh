#!/bin/bash
echo "Setting up IATI-Stats"
cd IATI-Stats
ln -s ../../IATI-Registry-Refresher/data data

echo "Setting up and running helpers"
cd helpers
git clone https://github.com/IATI/IATI-Rulesets.git
ln -s IATI-Rulesets/rulesets rulesets
ln -s ../../../IATI-Registry-Refresher/ckan ckan
./get_codelist_mapping.sh
./get_codelists.sh
./get_schemas.sh
wget "http://dashboard.iatistandard.org/stats/ckan.json"
wget "https://raw.githubusercontent.com/IATI/IATI-Dashboard/live/registry_id_relationships.csv"
cd ..

echo "Getting historical stats"
./get_stats.sh

echo "Setting up IATI-Dashboard"
cd ../IATI-Dashboard
ln -s ../IATI-Stats/stats-blacklist stats-blacklist
ln -s ../IATI-Stats/outputs stats-calculated

echo "Setup Complete"