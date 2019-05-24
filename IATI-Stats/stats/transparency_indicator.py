"""
This is a stats module, you can use it by running (in the parent directory)
python calculate_stats.py --stats-module stats.transparency_indicator loop

"""
from stats.common.decorators import returns_number, returns_numberdict, returns_dict, no_aggregation, memoize
from decimal import Decimal
from collections import defaultdict
import re, datetime
import csv 
import copy

from common import *

"""
Errors
InvalidOperation: Invalid literal for Decimal: '5 948.54'
ValueError: day is out of range for month
KeyError: ''
KeyError: 'INR'

"""

reader = csv.reader(open('helpers/transparency_indicator/country_lang_map.csv'), delimiter=';')
country_lang_map = dict((row[0], row[2]) for row in reader)
reader = csv.reader(open('helpers/transparency_indicator/Timeliness_Files_1.2.csv'))
frequency_map = dict((row[0], row[13]) for row in reader)


def aggregate_largest(f):
    class LargestAggregator(object):
        value = 0
        def __add__(self, x):
            try:
                x = int(x)
            except TypeError: x = 0
            except ValueError: x = 0
            if x > self.value:
                self.value = x
            return self
        def __int__(self):
            return self.value
    def wrapper(self, *args, **kwargs): 
        if self.blank:
            return LargestAggregator()
        else:
            return f(self, *args, **kwargs)
    return wrapper


class PublisherStats(object):
    blank = False

    @returns_dict
    def bottom_hierarchy(self):
        h = int(self.aggregated['hierarchy'])
        try:
            out = copy.deepcopy(self.aggregated['by_hierarchy']['' if h==0 else str(h)])
            if '(iati-organisation)' in self.aggregated['by_hierarchy']:
                for k,v in self.aggregated['by_hierarchy']['(iati-organisation)'].items():
                    if not k in out:
                        out[k] = copy.deepcopy(v)
        except KeyError:
            out = {}
        return out

    @returns_dict
    def top_hierarchy(self):
        h = int(self.aggregated['hierarchy'])
        bottom = '' if h==0 else str(h)
        out = {}
        try:
            for hierarchy, data in self.aggregated['by_hierarchy'].items():
                if hierarchy != bottom and hierarchy != '(iati-organisation)':
                    if out != {}: 'Warning, this code does not support >2 hierarchies'
                    out = copy.deepcopy(data)
        except KeyError: pass
        return out
            

    @aggregate_largest
    def timelag(self):
        if (
            (1 if self.aggregated['timelag_months']['2-3'] > 0 else 0) +
            (1 if self.aggregated['timelag_months']['1-2'] > 0 else 0) +
            (1 if self.aggregated['timelag_months']['1'] > 0 else 0)
            ) >= 2:
            return 4
        elif self.aggregated['timelag_months']['3'] > 0:
                return 3
        elif self.aggregated['timelag_months']['6'] > 0:
            return 2
        elif self.aggregated['timelag_months']['12'] > 0:
            return 1
        else:
            return 0

    @aggregate_largest
    def frequency(self):
        frenquency_weightings = {
            'Monthly': 4,
            'Quarterly': 3,
            'Six-monthly': 2,
            'Annually': 1,
            'Beyond one year': 0
        }
        if not self.folder in frequency_map:
            return -1
        else:
            return frenquency_weightings[frequency_map[self.folder]]




class ActivityFileStats(object):
    pass

class GenericStats(object):
    def _transaction_to_dollars(self, transaction, start_date):
        conversion_lookup = {
            'USD': (1,1),
            'AUD':	('0.966',	'1.092'),
            'CAD':	('0.999',	'1.039'),
            'CLP':	('485.984',	'506.922'),
            'CZK':	('19.538',	'19.519'),
            'DKK':	('5.79',	'5.631'),
            'JPY':	('79.814',	'98.923'),
            'CHF':	('0.938',	'0.932'),
            'GBP':	('0.631',	'0.645'),
            'EUR':	('0.778',	'0.755'),
            'XDR':	('0.632',	'0.66'),
            'ZAR':	('8.21',	'9.991') }
        value = transaction.find('value')
        currency = value.attrib.get('currency') or self.element.attrib.get('default-currency')
        conversion = conversion_lookup[currency][0 if start_date == datetime.date(2012,1,1) else 1]
        return Decimal(value.text) / Decimal(conversion)

class ActivityStats(GenericStats):
    blank = False

    @no_aggregation
    def iati_identifier(self):
        try:
            return self.element.find('iati-identifier').text
        except AttributeError:
            return None

    @aggregate_largest
    def hierarchy(self):
        return self.element.attrib.get('hierarchy') or ''

    @returns_numberdict
    def hierarchies(self):
        return {self.element.attrib.get('hierarchy'):1}

    def _oda_test(self, transaction):
        default_flow_type = self.element.xpath('default-flow-type/@code')
        flow_type = transaction.xpath('flow-type/@code')
        return '10' in default_flow_type or '10' in flow_type or (len(default_flow_type) == 0 and len(flow_type) == 0)

    @memoize
    def _oda_transactions(self):
        return filter(self._oda_test, self.element.findall('transaction'))

    def _coverage_oda(self, start_date, end_date, code_condition=lambda x: x  in ['D','E']):
        def date_conditions(date):
            return date and date >= start_date and date < end_date
        return sum([ self._transaction_to_dollars(x, start_date) for x in self._oda_transactions() if code_condition(x.find('transaction-type').attrib.get('code'))  and date_conditions(transaction_date(x)) ])
    
    def _coverage_all(self, start_date, end_date, code_condition=lambda x: x  in ['D','E']):
        def date_conditions(date):
            return date and date >= start_date and date < end_date
        return sum([ self._transaction_to_dollars(x, start_date) for x in self.element.findall('transaction') if code_condition(x.find('transaction-type').attrib.get('code'))  and date_conditions(transaction_date(x)) ])

    @returns_number
    def coverage_A(self):
        return self._coverage_oda(datetime.date(2012,1,1), datetime.date(2013,1,1))

    @returns_number
    def coverage_B(self):
        return self._coverage_oda(datetime.date(2012,10,1), datetime.date(2013,10,1))

    @returns_number
    def coverage_C(self):
        return self._coverage_all(datetime.date(2012,1,1), datetime.date(2013,1,1))

    @returns_number
    def coverage_D(self):
        return self._coverage_all(datetime.date(2012,10,1), datetime.date(2013,10,1))

    @returns_number
    def coverage_A_all_transaction_types(self):
        return self._coverage_oda(datetime.date(2012,1,1), datetime.date(2013,1,1), lambda x: True)

    @returns_number
    def coverage_B_all_transaction_types(self):
        return self._coverage_oda(datetime.date(2012,10,1), datetime.date(2013,10,1), lambda x: True)

    @returns_number
    def coverage_C_all_transaction_types(self):
        return self._coverage_all(datetime.date(2012,1,1), datetime.date(2013,1,1), lambda x: True)

    @returns_number
    def coverage_D_all_transaction_types(self):
        return self._coverage_all(datetime.date(2012,10,1), datetime.date(2013,10,1), lambda x: True)

    @returns_numberdict
    def timelag_months(self):
        one_month_ago = datetime.date(2014, 1, 1)
        two_months_ago = datetime.date(2013, 12, 1)
        three_months_ago = datetime.date(2013, 11, 1)
        six_months_ago = datetime.date(2013, 8, 1)
        twelve_months_ago = datetime.date(2012, 2, 1)
        dates = [ transaction_date(x) for x in self.element.findall('transaction') ]
        return {
            '1':   len(filter(lambda x: x and x>one_month_ago, dates)),
            '1-2': len(filter(lambda x: x and x>two_months_ago and x<one_month_ago, dates)),
            '2-3': len(filter(lambda x: x and x>three_months_ago and x<two_months_ago, dates)),
            '3': len(filter(lambda x: x and x>three_months_ago, dates)),
            '6':   len(filter(lambda x: x and x>six_months_ago, dates)),
            '12':  len(filter(lambda x: x and x>twelve_months_ago, dates))
        }

    @memoize
    def _start_date(self):
        try:
            return iso_date(self.element.xpath("activity-date[@type='start-actual']")[0])
        except IndexError:
            try:
                return iso_date(self.element.xpath("activity-date[@type='start-planned']")[0])
            except IndexError:
                return None

    def _end_date(self):
        try:
            return iso_date(self.element.xpath("activity-date[@type='end-actual']")[0])
        except IndexError:
            try:
                return iso_date(self.element.xpath("activity-date[@type='end-planned']")[0])
            except IndexError:
                return None

    @memoize
    def _current_activity(self):
        return (self.element.find('activity-status') is None or self.element.find('activity-status').text != '5') and (not self._end_date() or self._end_date() > datetime.date(2011,12,31))

    @returns_number
    def current_activities(self):
        return 1 if self._current_activity() else 0

    @returns_numberdict
    def current_activity_elements(self):
        if not self._current_activity():
            return

        if self.element.find('reporting-org').attrib.get('ref') in ['CA-3']:
            endorser_langs = ['en', 'fr']
        elif self.element.find('reporting-org').attrib.get('ref') in ['ES-5', '50']:
            endorser_langs = ['es']
        elif self.element.find('reporting-org').attrib.get('ref') in ['IADB']:
            endorser_langs = ['es','en']
        else:
            endorser_langs = ['en']

        try:
            langs = [ country_lang_map.get(x.attrib.get('code')) for x in self.element.findall('recipient-country') ]
            langs = list(set(filter(lambda x: x!='other' and x!=None and x not in endorser_langs, langs)))
        except AttributeError: langs = []

        elements = {
            1:  'reporting-org',
            2:  'iati-identifier',
            3:  'other-identifier',
            4:  'title',
            5:  ['title[@xml:lang="{0}" or ../@xml:lang="{0}"]'.format(lang) for lang in langs],
            6:  'description',
            7:  ['description[@xml:lang="{0}" or ../@xml:lang="{0}"]'.format(lang) for lang in langs],
            8:  'activity-status',
            9:  self._start_date,
            10: self._end_date,
            11: 'contact-info',
            12: 'participating-org[@role="Funding"]',
            13: 'participating-org[@role="Extending"]',
            14: 'participating-org[@role="Implementing"]',
            15: 'participating-org[@role="Accountable"]',
            16: 'recipient-country|recipient-region',
            17: 'location',
            18: 'sector[@vocabulary="DAC" or @vocabulary="DAC-3" or @vocabulary="" or not(@vocabulary)]',
            19: 'sector[@vocabulary!="DAC" and @vocabulary!="DAC-3" and @vocabulary!=""]',
            20: 'policy-marker',
            21: 'collaboration-type',
            22: 'default-flow-type|transaction/flow-type',
            23: 'default-finance-type|transaction/finance-type',
            24: 'default-aid-type|transaction/aid-type',
            25: 'default-tied-status|transaction/tied-status',
            26: 'budget',
            27: 'planned-disbursement',
            28: 'capital-spend',
            29: 'country-budget-items',
            30: 'transaction/transaction-type[@code="C"]',
            31: 'transaction/transaction-type[@code="D" or @code="E"]',
            32: 'transaction/transaction-type[@code="IF"]',
            33: lambda: self.element.xpath('transaction/transaction-type[@code="IR" or @code="LR"]') if len(self.element.xpath('transaction[starts-with(finance-type/@code, "4") and string-length(finance-type/@code) = 3]')) or self.element.xpath('starts-with(default-finance-type/@code, "4") and string-length(default-finance-type/@code) = 3') else True,
            34: 'document-link',
            35: 'activity-website',
            36: 'related-activity',
            37: 'conditions/@attached',
            38: 'conditions/condition',
            39: 'result',
            'lang-denominator': lambda: len(langs) if len(langs) else None
            }
        def test_exists(element):
            if callable(element):
                if element() is None: return 0
                else: return 1
            elif type(element) == list:
                return 0 if len(element)==0 or 0 in map(test_exists, element) else 1
            else:
                if len(self.element.xpath(element)) >=1: return 1
                else: return 0
        return dict((str(n).zfill(2), test_exists(e)) for n,e in elements.items())
        

    def _cpa(self, transaction=None):
        sectors = set() # FIXME
        aid_types = set()
        flow_types = set()
        finance_types = set()
        regions = set()
        e = self.element
        return not(
            ( (len(e.xpath('recipient-country/@code')) == 0 or '' in e.xpath('recipient-country/@code')) and (len(e.xpath('recipient-region/@code')) == 0 or '998' in e.xpath('recipient-region/@code') or '' in e.xpath('recipient-region/@code')) ) or
            len(sectors.intersection(e.xpath('sector/@code'))) > 0 or
            len(aid_types.intersection(e.xpath('default-aid-type/@code'))) > 0 or
            len(flow_types.intersection(e.xpath('default-flow-type/@code'))) > 0 or
            len(finance_types.intersection(e.xpath('default-finance-type/@code'))) > 0 or
            len(finance_types.intersection(e.xpath('recipient-region/@code'))) > 0 or
            (transaction is not None and
                (len(aid_types.intersection(transaction.xpath('aid-type/@code'))) > 0 or
                len(flow_types.intersection(transaction.xpath('flow-type/@code'))) > 0 or
                len(finance_types.intersection(transaction.xpath('finance-type/@code'))) > 0)))


    @returns_number
    def coverage_numerator(self):
        start_date = datetime.date(2012,1,1)
        end_date = datetime.date(2013,1,1)
        transactions = filter(self._cpa, self.element.findall('transaction'))
        def date_conditions(date):
            return date and date >= start_date and date < end_date
        return sum([ Decimal(x.find('value').text) for x in transactions if x.find('transaction-type').attrib.get('code') in ['D','E']  and date_conditions(transaction_date(x)) ])

    @returns_numberdict
    def forward_looking_activity(self):
        if not self._cpa():
            return {}
        out = defaultdict(int)
        budgets = self.element.findall('budget')
        if len(budgets):
            for budget in budgets:
                out[budget_year(budget)] += self._transaction_to_dollars(budget, datetime.date.today())
        else:
            for planned_disbursement in self.element.findall('planned-disbursement'):
                out[budget_year(planned_disbursement)] += self._transaction_to_dollars(planned_disbursement, datetime.date.today())
        return out

class OrganisationFileStats(object):
    pass

class OrganisationStats(GenericStats):
    blank = False

    @aggregate_largest
    def hierarchy(self):
        return '(iati-organisation)'

    @returns_numberdict
    def forward_looking_aggregate(self):
        out = defaultdict(Decimal)
        budgets = self.element.findall('recipient-country-budget')
        for budget in budgets:
            out[budget_year(budget)] += self._transaction_to_dollars(budget, datetime.date.today())
        return out

class AllDataStats(object):
    pass

