mkdir out-ti out-ti-err
for f in data-ti/*; do
    rm -r out/*
    rm -r aggregated/*
    python calculate_stats.py --stats-module stats.transparency_indicator loop --data $f > out-ti-err/`basename $f`_loop
    python calculate_stats.py --stats-module transparency_indicator aggregate > out-ti-err/`basename $f`_aggregate
    mv out/aggregated out-ti/`basename $f`
done
