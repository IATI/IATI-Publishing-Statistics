#!/usr/bin/env bash

for x in 105 203; do
    i=$(echo $x | head -c 1)
    mkdir -p codelists/$i
    wget --tries=20 --waitretry=10 --retry-connrefused "http://iatistandard.org/$x/codelists/downloads/clv2/json/en/Version.json" -O codelists/$i/Version.json
    wget --tries=20 --waitretry=10 --retry-connrefused "http://iatistandard.org/$x/codelists/downloads/clv2/json/en/ActivityStatus.json" -O codelists/$i/ActivityStatus.json
    wget --tries=20 --waitretry=10 --retry-connrefused "http://iatistandard.org/$x/codelists/downloads/clv2/json/en/Currency.json" -O codelists/$i/Currency.json
    wget --tries=20 --waitretry=10 --retry-connrefused "http://iatistandard.org/$x/codelists/downloads/clv2/json/en/Sector.json" -O codelists/$i/Sector.json
    wget --tries=20 --waitretry=10 --retry-connrefused "http://iatistandard.org/$x/codelists/downloads/clv2/json/en/SectorCategory.json" -O codelists/$i/SectorCategory.json
    wget --tries=20 --waitretry=10 --retry-connrefused "http://iatistandard.org/$x/codelists/downloads/clv2/json/en/DocumentCategory.json" -O codelists/$i/DocumentCategory.json
    wget --tries=20 --waitretry=10 --retry-connrefused "http://iatistandard.org/$x/codelists/downloads/clv2/json/en/AidType.json" -O codelists/$i/AidType.json
    wget --tries=20 --waitretry=10 --retry-connrefused "http://iatistandard.org/$x/codelists/downloads/clv2/json/en/BudgetNotProvided.json" -O codelists/$i/BudgetNotProvided.json
done
