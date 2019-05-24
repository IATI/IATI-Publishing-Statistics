set -e
# The above line ensures this scripts stops if any individual command errors

mkdir gitout
for f in ckan gitdate; do
    curl --compress "http://dashboard.iatistandard.org/stats/${f}.json" > gitout/${f}.json
done

mkdir stats-blacklist
cd stats-blacklist
wget "http://dashboard.iatistandard.org/stats-blacklist/current.tar.gz" -O current.tar.gz 
wget "http://dashboard.iatistandard.org/stats-blacklist/gitaggregate.tar.gz" -O gitaggregate.tar.gz
wget "http://dashboard.iatistandard.org/stats-blacklist/gitaggregate-publisher.tar.gz" -O gitaggregate-publisher.tar.gz
wget "http://dashboard.iatistandard.org/stats-blacklist/gitaggregate-dated.tar.gz" -O gitaggregate-dated.tar.gz
wget "http://dashboard.iatistandard.org/stats-blacklist/gitaggregate-publisher-dated.tar.gz" -O gitaggregate-publisher-dated.tar.gz
tar -xvf current.tar.gz
tar -xvf gitaggregate.tar.gz 
tar -xvf gitaggregate.tar.gz
tar -xvf gitaggregate-dated.tar.gz 
tar -xvf gitaggregate-publisher-dated.tar.gz
cd ..

cd gitout
wget "http://dashboard.iatistandard.org/stats/current.tar.gz" -O current.tar.gz
wget "http://dashboard.iatistandard.org/stats/gitaggregate.tar.gz" -O gitaggregate.tar.gz
wget "http://dashboard.iatistandard.org/stats/gitaggregate-publisher.tar.gz" -O gitaggregate-publisher.tar.gz
wget "http://dashboard.iatistandard.org/stats/gitaggregate-dated.tar.gz" -O gitaggregate-dated.tar.gz
wget "http://dashboard.iatistandard.org/stats/gitaggregate-publisher-dated.tar.gz" -O gitaggregate-publisher-dated.tar.gz
tar -xvf current.tar.gz
tar -xvf gitaggregate.tar.gz 
tar -xvf gitaggregate.tar.gz
tar -xvf gitaggregate-dated.tar.gz 
tar -xvf gitaggregate-publisher-dated.tar.gz

