#!/usr/bin/env bash
# Fetch the two source datasets. Both are openly licensed; we don't vendor them.
set -euo pipefail
cd "$(dirname "$0")"
echo "→ DoBIH (CC BY 4.0)"
curl -sL -o hillcsv.zip "https://www.hill-bagging.co.uk/dobih-downloads/hillcsv.zip"
unzip -oq hillcsv.zip && rm hillcsv.zip
echo "→ OS Complete Trig Archive (OGL)"
mkdir -p trig
curl -sL -o trig.zip "https://www.ordnancesurvey.co.uk/documents/gps/CompleteTrigArchive.zip"
unzip -oq trig.zip -d trig && rm trig.zip
ls -la *.csv trig/*.csv
