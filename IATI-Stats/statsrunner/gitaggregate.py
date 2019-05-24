import decimal
import json
import os
import sys
from common import decimal_default

# Set value for the gitout directory
GITOUT_DIR = os.environ.get('GITOUT_DIR') or 'gitout'

# Set bool if the 'dated' argument has been used in calling this script
dated = len(sys.argv) > 1 and sys.argv[1] == 'dated'

git_out_dir = os.path.join(GITOUT_DIR, 'gitaggregate-dated' if dated else 'gitaggregate')

# Exclude some json stats files from being aggregated
# These are typically the largest stats files that would consume large amounts
# of memory/disk space if aggregated over time
whitelisted_stats_files = [
    'activities',
    'activity_files',
    'file_size_bins',
    'file_size',
    'invalidxml',
    'nonstandardroots',
    'organisation_files',
    'publisher_has_org_file',
    'publishers_per_version',
    'publishers',
    'publishers_validation',
    'unique_identifiers',
    'validation',
    'versions',
    'teststat'  # Extra 'stat' added as the test_gitaggregate.py assumes a file with this name is present
]

# Load the reference of commits to dates
if dated:
    gitdates = json.load(open('gitdate.json'))

# Make the gitout directory
try:
    os.makedirs(git_out_dir)
except OSError:
    pass

# Get a list containing the names of the entries in the directory
git_out_files = os.listdir(git_out_dir)

# Loop over each commit in gitout/commits
for commit in os.listdir(os.path.join(GITOUT_DIR, 'commits')):
    print 'Aggregating for commit: {}'.format(commit)

    for fname in os.listdir(os.path.join(GITOUT_DIR, 'commits', commit, 'aggregated')):
        if not fname.endswith('.json'):
            continue

        trimmed_name = fname[:-5]  # remove '.json' from the filename
        # Ignore certain files
        if trimmed_name not in whitelisted_stats_files:
            continue

        print 'Adding to {} for file: {}'.format('gitaggregate-dated' if dated else 'gitaggregate', fname)

        commit_json_fname = os.path.join(GITOUT_DIR, 'commits', commit, 'aggregated', fname)

        # Load the current file conents to memory, or set as an empty dictionary
        if fname in git_out_files:
            # FIXME: This is a possible cause of a memory issue in future, as the size of the aggregate file 
            #        increases each time there is a new commit
            with open(os.path.join(git_out_dir, fname)) as filepath:
                gitaggregate_json = json.load(filepath, parse_float=decimal.Decimal)
        else:
            gitaggregate_json = {}

        # If the commit that we are looping over is not already in the data for this file, then add it to the output
        if commit not in gitaggregate_json:
            with open(commit_json_fname) as commit_filepath:
                commit_gitaggregate_json = json.load(commit_filepath, parse_float=decimal.Decimal)
                if dated:
                    if commit in gitdates:
                        gitaggregate_json[gitdates[commit]] = commit_gitaggregate_json
                else:
                    gitaggregate_json[commit] = commit_gitaggregate_json

            # Write output to a temporary file, then rename
            with open(os.path.join(git_out_dir, trimmed_name + '.json.new'), 'w') as filepath:
                print 'Writing data to {}'.format(trimmed_name)
                json.dump(gitaggregate_json, filepath, sort_keys=True, indent=2, default=decimal_default)
            print 'Renaming file {} to {}'.format(trimmed_name + '.json.new', trimmed_name + '.json')
            os.rename(os.path.join(git_out_dir, trimmed_name + '.json.new'), os.path.join(git_out_dir, trimmed_name + '.json'))
