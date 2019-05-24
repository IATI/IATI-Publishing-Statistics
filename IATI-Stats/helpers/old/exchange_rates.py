import csv
from lxml import etree
from decimal import Decimal

root = etree.parse('helpers/old/country-currency.xml').getroot()

# Source: http://www.oecd.org/dac/stats/Exchange%20rates.xls
exchange_dict = {}
with open('helpers/old/exchange_rates.csv') as fp:
    reader = csv.DictReader(fp)
    for line in reader:
        exchange_dict[line['Country']] = line

#class UnsupportedCurrency(Exception):
#    pass

def toUSD(value, currency, year):
    return value * Decimal(exchange_dict[root.find("*[@ISO='{0}']".format(currency)).get('name')][str(year)])

