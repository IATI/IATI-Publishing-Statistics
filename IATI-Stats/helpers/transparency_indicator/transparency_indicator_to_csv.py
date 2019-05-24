import csv, os, json

coverage = csv.writer(open('out-ti-csv/1-coverage.csv','w'))
coverage.writerow(['endorser','A','B','C','D','all A','all B','all C','all D'])
timelag = csv.writer(open('out-ti-csv/2-timelag.csv','w'))
timelag.writerow(['endorser','frequency','timelag'])
detail = csv.writer(open('out-ti-csv/3-detail.csv','w'))
detail_top = csv.writer(open('out-ti-csv/3a-detail-top.csv','w'))
detail_columns = [ unicode(x).zfill(2) for x in range(1,40) ] + [ 'lang-denominator' ]
detail.writerow(['endorser','activities'] + detail_columns)
detail_top.writerow(['endorser','activities'] + detail_columns)
forward = csv.writer(open('out-ti-csv/4-forward-looking.csv','w'))
forward.writerow(['endorser','numerator','2013 Agg','2013 Act','2014 Agg','2014 Act','2015 Agg','2015 Act','2016 Agg', '2016 Act'])

"""
Note that the below code no longer works due to the splitting of JSON files, and the removal of by_hierarchy.

"""

#for endorser in sorted(os.listdir('out-ti')):
for endorser in sorted(os.listdir('aggregated-publisher')):
    if not endorser.endswith('.json'): continue
    endorser_name = endorser[:-5]
    aggregated = json.load(open(os.path.join('aggregated-publisher', endorser)))
    #if endorser_name == 'irishaid': continue
    if not aggregated['bottom_hierarchy']:
        continue
    coverage.writerow([endorser_name,
        aggregated['bottom_hierarchy']['coverage_A'],
        aggregated['bottom_hierarchy']['coverage_B'],
        aggregated['bottom_hierarchy']['coverage_C'],
        aggregated['bottom_hierarchy']['coverage_D'],
        aggregated['bottom_hierarchy']['coverage_A_all_transaction_types'],
        aggregated['bottom_hierarchy']['coverage_B_all_transaction_types'],
        aggregated['bottom_hierarchy']['coverage_C_all_transaction_types'],
        aggregated['bottom_hierarchy']['coverage_D_all_transaction_types'],
        ])
    timelag.writerow([endorser_name,aggregated['frequency'],aggregated['timelag']])
    detail.writerow([endorser_name,aggregated['bottom_hierarchy']['current_activities']]+[aggregated['bottom_hierarchy']['current_activity_elements'].get(x) for x in detail_columns])
    if 'top_hierarchy' in aggregated and aggregated['top_hierarchy'] != {}:
        detail_top.writerow([endorser_name,aggregated['top_hierarchy']['current_activities']]+[aggregated['top_hierarchy']['current_activity_elements'].get(x) for x in detail_columns])
    forward.writerow([endorser_name,
        aggregated['bottom_hierarchy']['coverage_numerator'],
        aggregated['forward_looking_aggregate'].get('2013') or 0,
        aggregated['bottom_hierarchy']['forward_looking_activity'].get('2013') or 0,
        aggregated['forward_looking_aggregate'].get('2014') or 0,
        aggregated['bottom_hierarchy']['forward_looking_activity'].get('2014') or 0,
        aggregated['forward_looking_aggregate'].get('2015') or 0,
        aggregated['bottom_hierarchy']['forward_looking_activity'].get('2015') or 0,
        aggregated['forward_looking_aggregate'].get('2016') or 0,
        aggregated['bottom_hierarchy']['forward_looking_activity'].get('2016') or 0
        ])

