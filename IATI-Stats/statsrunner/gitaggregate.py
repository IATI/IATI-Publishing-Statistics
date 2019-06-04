import decimal
import json
import os
from common import decimal_default

# Set value for the gitout directory
GITOUT_DIR = os.environ.get('GITOUT_DIR') or 'outputs'

git_out_dir = os.path.join(GITOUT_DIR, 'gitaggregate')

# Exclude some json stats files from being aggregated
# These are typically the largest stats files that would consume large amounts
# of memory/disk space if aggregated over time
whitelisted_stats_files = [
    'activities',
]

# Make the gitout directory
try:
    os.makedirs(git_out_dir)
except OSError:
    pass

# Get a list containing the names of the entries in the directory
git_out_files = os.listdir(git_out_dir)

for fname in os.listdir(os.path.join(GITOUT_DIR, 'aggregated')):
    if not fname.endswith('.json'):
        continue

    trimmed_name = fname[:-5]  # remove '.json' from the filename
    # Ignore certain files
    if trimmed_name not in whitelisted_stats_files:
        continue

    print 'Adding to {} for file: {}'.format('gitaggregate', fname)

    commit_json_fname = os.path.join(GITOUT_DIR, 'aggregated', fname)

    # Load the current file conents to memory, or set as an empty dictionary
    if fname in git_out_files:
        # FIXME: This is a possible cause of a memory issue in future, as the size of the aggregate file 
        #        increases each time there is a new commit
        with open(os.path.join(git_out_dir, fname)) as filepath:
            gitaggregate_json = json.load(filepath, parse_float=decimal.Decimal)
    else:
        gitaggregate_json = {}

    with open(commit_json_fname) as commit_filepath:
        commit_gitaggregate_json = json.load(commit_filepath, parse_float=decimal.Decimal)
        gitaggregate_json = commit_gitaggregate_json

    # Write output to a temporary file, then rename
    with open(os.path.join(git_out_dir, trimmed_name + '.json.new'), 'w') as filepath:
        print 'Writing data to {}'.format(trimmed_name)
        json.dump(gitaggregate_json, filepath, sort_keys=True, indent=2, default=decimal_default)
    print 'Renaming file {} to {}'.format(trimmed_name + '.json.new', trimmed_name + '.json')
    os.rename(os.path.join(git_out_dir, trimmed_name + '.json.new'), os.path.join(git_out_dir, trimmed_name + '.json'))
