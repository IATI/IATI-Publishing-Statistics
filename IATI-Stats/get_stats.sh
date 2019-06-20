set -e
# The above line ensures this scripts stops if any individual command errors

if [ ! -d outputs ]; then
	mkdir outputs
fi
for f in ckan gitdate; do
    curl --compressed "http://dashboard.iatistandard.org/stats/${f}.json" > outputs/${f}.json
done

if [ ! -d stats-blacklist ]; then
	mkdir stats-blacklist
fi
cd stats-blacklist
wget "http://dashboard.iatistandard.org/stats-blacklist/current.tar.gz" -O current.tar.gz 
wget "http://dashboard.iatistandard.org/stats-blacklist/gitaggregate.tar.gz" -O gitaggregate.tar.gz
wget "http://dashboard.iatistandard.org/stats-blacklist/gitaggregate-publisher.tar.gz" -O gitaggregate-publisher.tar.gz
wget "http://dashboard.iatistandard.org/stats-blacklist/gitaggregate-dated.tar.gz" -O gitaggregate-dated.tar.gz
wget "http://dashboard.iatistandard.org/stats-blacklist/gitaggregate-publisher-dated.tar.gz" -O gitaggregate-publisher-dated.tar.gz
tar -xvzf current.tar.gz
tar -xvzf gitaggregate.tar.gz 
tar -xvzf gitaggregate-publisher.tar.gz
tar -xvzf gitaggregate-dated.tar.gz 
tar -xvzf gitaggregate-publisher-dated.tar.gz
cd ..

cd outputs
wget "http://dashboard.iatistandard.org/stats/current.tar.gz" -O current.tar.gz
wget "http://dashboard.iatistandard.org/stats/gitaggregate.tar.gz" -O gitaggregate.tar.gz
wget "http://dashboard.iatistandard.org/stats/gitaggregate-publisher.tar.gz" -O gitaggregate-publisher.tar.gz
wget "http://dashboard.iatistandard.org/stats/gitaggregate-dated.tar.gz" -O gitaggregate-dated.tar.gz
wget "http://dashboard.iatistandard.org/stats/gitaggregate-publisher-dated.tar.gz" -O gitaggregate-publisher-dated.tar.gz
tar -xvzf current.tar.gz
tar -xvzf gitaggregate.tar.gz 
tar -xvzf gitaggregate-publisher.tar.gz
tar -xvzf gitaggregate-dated.tar.gz 
tar -xvzf gitaggregate-publisher-dated.tar.gz
