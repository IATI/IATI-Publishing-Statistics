"""
This is a stats module, you can use it by running (in the parent directory)
python calculate_stats.py --stats-module stats.old loop

Original code written to calculate some specific stats for a poster.
Not suitable for generic use in stats.py due to hardcoded years etc.

"""

from helpers.old.exchange_rates import toUSD
from stats.common.decorators import *
from stats.common import debug
from decimal import Decimal

class ActivityFileStats(object):
    pass

class OrganisationFileStats(object):
    pass

class OrganisationStats(object):
    pass

class AllDataStats(object):
    pass

class PublisherStats(object):
    blank = False

    @returns_numberdict
    def publishers_per_country(self):
        countries = self.aggregated['activities_per_country'].keys()
        return dict((c,1) for c in countries)

    @returns_numberdict
    def publishers_per_organisation_type(self):
        organisation_types = self.aggregated['spend_per_organisation_type'].keys()
        return dict((o,1) for o in organisation_types)

class ActivityStats(object):
    blank = False

    def __get_start_year(self):
        activity_date = self.element.find("activity-date[@type='start-actual']")
        if activity_date is None: activity_date = self.element.find("activity-date[@type='start-planned']")
        if activity_date is not None and activity_date.get('iso-date'):
            try:
                date = datetime.datetime.strptime(activity_date.get('iso-date').strip('Z'), "%Y-%m-%d")
                return int(date.year)
            except ValueError, e:
                debug(self, e)
            except AttributeError, e:
                debug(self, e)

    def __create_decimal(self, s):
        if self.strict:
            return Decimal(s)
        else:
            return Decimal(s.replace(',', '').replace(' ', ''))

    def __value_to_dollars(self, transaction):
        try:
            value = transaction.find('value')
            currency = value.get('currency') or self.element.get('default-currency')
            if currency == 'USD': return self.__create_decimal(value.text)
            try:
                year = datetime.datetime.strptime(value.get('value-date').strip('Z'), "%Y-%m-%d").year
            except AttributeError:
                try:
                    if self.strict: raise AttributeError
                    year = datetime.datetime.strptime(transaction.find('transaction-date').get('iso-date').strip('Z'), "%Y-%m-%d").year
                except AttributeError:
                    debug(self, 'Transaction without date information')
                    return Decimal(0.0)
            if year == 2013: year = 2012
            return toUSD(value=self.__create_decimal(value.text),
                         currency=currency,
                         year=year)
        except Exception, e:
            debug(self, e)
            return Decimal(0.0)
    
    @returns_number
    def spend(self):
        """ Spend is defined as the sum of all transactions that are Disbursements (D) or Expenditure (E) """
        transactions = [ x for x in self.element.findall('transaction') if x.find('transaction-type') is not None and x.find('transaction-type').get('code') in ['D','E'] ]
        return sum(map(self.__value_to_dollars, transactions))

    @returns_numberdict
    def spend_per_year(self):
        return {self.__get_start_year():self.spend()}
    
    @returns_numberdict
    def activities_per_country(self):
        """ Legacy code according to @bjwebb this is not used now """
        if self.__get_start_year() >= 2010:
            countries = self.element.findall('recipient-country')
            regions = self.element.findall('recipient-region')
            if countries is not None:
                return dict((country.get('code'),1) for country in countries)
            elif regions is not None:
                return dict((region.get('code'),1) for region in regions)

    @returns_number
    def activities_no_country(self):
        if len(self.activities_per_country()) == 0:
            return 1

    @returns_numberdict
    def spend_per_country(self):
        if self.__get_start_year() >= 2010:
            country = self.element.find('recipient-country')
            region = self.element.find('recipient-region')
            if country is not None and country.get('code'):
                return {country.get('code'):self.spend()}
            elif region is not None and region.get('code'):
                return {region.get('code'):self.spend()}
            else:
                return {None:self.spend()}
        else:
            return {'pre2010':self.spend()}
    
    @returns_numberdict
    def spend_per_organisation_type(self):
        try:
            transactions = [ x for x in self.element.findall('transaction') if
                x.find('transaction-type') is not None and
                x.find('transaction-type').get('code') in ['D','E'] and
                x.find('transaction-date') is not None and
                datetime.datetime.strptime(x.find('transaction-date').get('iso-date').strip('Z'), "%Y-%m-%d") > datetime.datetime(2012, 6, 30) ]
            spend = sum(map(self.__value_to_dollars, transactions))
            organisationType = self.element.find('reporting-org')
            if organisationType is not None:
                return {organisationType.get('type'):spend}
        except ValueError:
            pass
        except AttributeError, e:
            pass

