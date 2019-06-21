#!/bin/bash
echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Starting publisher stats regeneration"
cd ../IATI-Registry-Refresher
if [ ! -d data ]; then
	echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Cloning IATI-Data-Snapshot"
    git clone git://dashboard.iatistandard.org/IATI-Data-Snapshot.git data
fi
echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Running IATI-Registry-Refresher"
./git.sh > ../logs/$(date +\%Y\%m\%d)-rr.log 2>&1
for i in data/*/; do
    zip -FS -r zips/"`basename $i`.zip" "$i"
done > ../logs/$(date +\%Y\%m\%d)-zips.log 2>&1

echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Activating Virtual environment"
cd ../IATI-Publishing-Statistics
source pyenv/bin/activate

echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Running IATI-Stats"
cd IATI-Stats
./git_dashboard.sh > ../../logs/$(date +\%Y\%m\%d)-stats.log 2>&1

echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Running IATI-Dashboard"
cd ../IATI-Dashboard
./git.sh > ../../logs/$(date +\%Y\%m\%d)-dashboard.log 2>&1
deactivate