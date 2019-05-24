import json
import sys
import csv

writer = csv.writer(sys.stdout, lineterminator='\n')

with open('aggregated.json') as fp:
    aggregated = json.load(fp)
    for line in sorted(aggregated[sys.argv[1]].items()):
        writer.writerow(line)
