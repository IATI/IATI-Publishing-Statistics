#!/bin/bash
echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Starting Stats generation"
echo $GITOUT_DIR
if [ "$GITOUT_DIR" = "" ]; then
    GITOUT_DIR="gitout"
fi
if [ "$COMMIT_SKIP_FILE" = "" ]; then
    COMMIT_SKIP_FILE=$GITOUT_DIR/gitaggregate/activities.json
fi

# Make the all the gitout directories
echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Making gitout directories"
mkdir -p $GITOUT_DIR/logs
mkdir -p $GITOUT_DIR/commits
mkdir -p $GITOUT_DIR/gitaggregate
mkdir -p $GITOUT_DIR/gitaggregate-dated



cd helpers
# Update codelist mapping, codelists and schemas
echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Update codelist mapping"
./get_codelist_mapping.sh
echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Update codelists"
./get_codelists.sh
echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Update schemas"
./get_schemas.sh
# Build a JSON file of metadata for each CKAN publisher, and for each dataset published.
# This is based on the data from the CKAN API
echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Running ckan.py"
python ckan.py
cd ..
echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Copying ckan.json"
cp helpers/ckan.json $GITOUT_DIR


# Clear output directory
echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Clearing output directory"
rm -r out

# Bring the IATI raw data up-to-date
cd data || exit $?
# Checkout automatic, and make sure it is clean and up to date
echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Performing git operations on the data snapshot"
git checkout automatic
git reset --hard
git clean -df
git pull --ff-only


# Create a gitdate file in JSON format. This contains the git hash and date for each data commit
echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Creating gitdate file"
echo '{' > gitdate.json
git log --format="format:%H|%ai" | awk -F '|' '{ print "\""$1"\": \""$2"\"," } ' >> gitdate.json
# Ensure the last line doesn't have a trailing comma
sed -i '$d' gitdate.json
git log --format="format:%H|%ai" | tail -n1 | awk -F '|' '{ print "\""$1"\": \""$2"\"" } ' >> gitdate.json
echo '}' >> gitdate.json
# Perform this dance because piping to ../ behaves differently with symlinks
cd .. || exit $?
echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Move and copy gitdate file"
mv data/gitdate.json .
cp gitdate.json $GITOUT_DIR


# Store current and all commit hashes as variables
cd data || exit $?
# Get the latest commit hash
echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Storing git info as bash variables"
current_hash=`git rev-parse HEAD`
# Get all commit hashes
commits=`git log --format=format:%H`
cd .. || exit $?


# Loop over commits and run stats code
echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Looping over commits"
for commit in $commits; do
    if grep -q $commit $COMMIT_SKIP_FILE; then
        echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Skipping $commit (due to grep conditional)"
    elif [ $GITOUT_SKIP_INCOMMITSDIR ] && [ -d $GITOUT_DIR/commits/$commit ]; then
        echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Skipping $commit (due to git skip conditionals)"
    else
        echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Running stats code for commit: $commit"

        # Get the data to the specified commit
        cd data || exit $?
        echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Checking out commit $commit"
        git checkout $commit
        git clean -df

        commit_date=`git log --format="format:%ai" | head -n 1`
        echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Set commit date as $commit_date"
        cd .. || exit $?

        # Disable this because it doesn't work for date dependent stuff.........
        #mkdir -p $GITOUT_DIR/hash
        #python statsrunner/hashlink.py || exit 1
        # (and also this on the next line: --new)

        # Run the stats commands and save output to log files
        echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Calculating stats (loop) for commit $commit"
        python calculate_stats.py $@ --today "$commit_date" loop > $GITOUT_DIR/logs/${commit}_loop.log || exit 1
        echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Calculating stats (aggregate) for commit $commit"
        python calculate_stats.py $@ --today "$commit_date" aggregate > $GITOUT_DIR/logs/${commit}_aggregate.log || exit 1
        if [ $commit = $current_hash ]; then
		echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Calculating stats (invert) for commit $commit"
    python calculate_stats.py $@ --today "$commit_date" invert > $GITOUT_DIR/logs/${commit}_invert.log
        fi
        #python statsrunner/hashcopy.py || exit 1
        echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Removing output for commit dir: $commit"
        rm -r $GITOUT_DIR/commits/$commit
        mv out $GITOUT_DIR/commits/$commit || exit $?

        echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Running gitaggregate.py for commit: $commit"
        python statsrunner/gitaggregate.py
        echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Running gitaggregate.py dated for commit: $commit"
        python statsrunner/gitaggregate.py dated
        echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Running gitaggregate-publisher.py for commit: $commit"
        python statsrunner/gitaggregate-publisher.py
        echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Running gitaggregate-publisher.py dated for commit: $commit"
        python statsrunner/gitaggregate-publisher.py dated
        # If the commit is the latest commit then, move the resulting stats to the 'current' directory
        if [ ! $commit = $current_hash ]; then
            echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Removing commit dir (based on latest commit logic) for commit: $commit"
            rm -r $GITOUT_DIR/commits/$commit
        else
            cd $GITOUT_DIR || exit $?
            echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Removing current dir for commit: $commit"
            rm -r current
            # Since we're not currently creating symlinks, we can just do a plain move here
            mv commits/$current_hash current
            echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Creating current.tar.gz for commit: $commit"
            tar -czf current.tar.gz current
            cd .. || exit $?
        fi
        if [ "$ALL_COMMITS" = "" ]; then
            echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Breaking out of commit logic for commit: $commit"
            break
        fi
    fi
done

cd $GITOUT_DIR || exit $?
echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Creating compressed file: gitaggregate"
tar -czf gitaggregate.tar.gz gitaggregate
echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Creating compressed file: gitaggregate-dated"
tar -czf gitaggregate-dated.tar.gz gitaggregate-dated
echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Creating compressed file: gitaggregate-publisher"
tar -czf gitaggregate-publisher.tar.gz gitaggregate-publisher
echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Creating compressed file: gitaggregate-publisher-dated"
tar -czf gitaggregate-publisher-dated.tar.gz gitaggregate-publisher-dated
