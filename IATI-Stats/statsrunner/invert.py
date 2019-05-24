import json
import os, sys
from collections import defaultdict

def invert_dir(basedirname, out_filename, output_dir):
    """
    This 'inverts' the aggregated json files produced by aggregate.py
    ie. it creates a json file of the stats grouped by value, and then by
    publisher.

    """
    out = {}

    for dirname, dirs, files in os.walk(os.path.join(output_dir, basedirname), followlinks=True):
        parent_folder = os.path.basename(dirname)
        for f in files:
            with open(os.path.join(dirname, f)) as fp:
                stats_name = f[:-5]
                stats_values = json.load(fp)
                if type(stats_values) == dict:
                    if not stats_name in out:
                        out[stats_name] = defaultdict(dict)

                    for k,v in stats_values.items():
                        if type(v) == dict:
                            if not k in out[stats_name]:
                                out[stats_name][k] = defaultdict(dict)
                            for k2,v2 in v.items():
                                out[stats_name][k][k2][parent_folder] = v2
                        else:
                            out[stats_name][k][parent_folder] = v

                elif type(stats_values) == int:
                    if not stats_name in out:
                        out[stats_name] = defaultdict(int)

                    out[stats_name][parent_folder] += stats_values

    for statname, inverted in out.items():
        try:
            os.mkdir(os.path.join(output_dir, out_filename))
        except OSError: pass
        with open(os.path.join(output_dir, out_filename, statname+'.json'), 'w') as fp:
            json.dump(inverted, fp, sort_keys=True, indent=2)

def invert(args):
    for dirname in ['inverted-publisher', 'inverted-file', 'inverted-file-publisher']:
        try:
            os.mkdir(os.path.join(args.output, dirname))
        except OSError: pass
    invert_dir('aggregated-publisher', 'inverted-publisher', args.output)
    invert_dir('aggregated-file', 'inverted-file', args.output)
    for folder in os.listdir(os.path.join(args.output, 'aggregated-file')):
        try:
            os.mkdir(os.path.join(args.output, 'inverted-file-publisher', folder))
        except OSError: pass
        invert_dir(os.path.join('aggregated-file', folder), os.path.join('inverted-file-publisher', folder), args.output)

