# Calculate allt the stats necessary for the dashboard.
# Currently this this is the activity blacklist, and the main dashboard stats,
# which are used indepently by the dashboard.
# However, the plan is to have the latter stats run depend on the former:
# https://github.com/IATI/IATI-Dashboard/issues/223
echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Starting Stats generation"
echo "========="

echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Running general stats"
echo "========="
GITOUT_SKIP_INCOMMITSDIR=1 ./git.sh --stats-module stats.dashboard $@
