#!/usr/bin/env bash

wget --tries=20 --waitretry=10 --retry-connrefused https://raw.github.com/IATI/IATI-Codelists/version-1.05/mapping.xml -O mapping-1.xml
wget --tries=20 --waitretry=10 --retry-connrefused https://raw.github.com/IATI/IATI-Codelists/version-2.03/mapping.xml -O mapping-2.xml
