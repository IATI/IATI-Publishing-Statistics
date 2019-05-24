import csv
import datetime
import re

def debug(stats, error):
    """ prints debugging information for a given stats object and error """
    print unicode(error)+stats.context 

xsDateRegex = re.compile('(-?[0-9]{4,})-([0-9]{2})-([0-9]{2})')

def iso_date_match(raw_date):
    """Return a datetime object for a given textual ISO date string

    Keyword arguments:
    raw_date -- an ISO date as text
    """
    if raw_date:
        m1 = xsDateRegex.match(raw_date)
        if m1:
            try:
                return datetime.date(*map(int, m1.groups()))
            except ValueError:
                # A ValueError occurs when there is an invalid raw_date, 
                # for example '2015-11-31' or '2015-13-01'
                return None    
        else:
            return None

def iso_date(element):
    """Return a datetime object for a given XML element either i) an 'iso-date' attribute or ii) an iso date as text

    Keyword arguments:
    element -- an XML element containing either i) an 'iso-date' attribute or ii) an iso date as text
    """
    if element is None:
        return None
    raw_date = element.attrib.get('iso-date')
    if not raw_date:
        raw_date = element.text
    return iso_date_match(raw_date)

def transaction_date(transaction):
    """Returns a datetime object for an input transaction object. 
       A transaction-date is preferred, although if not available, returns value/value-date
       Returns None if neither found.

       Input:
         transaction -- etree transaction object
       Returns:
         datetime object or None
    """
    if transaction.find('transaction-date') is not None:
        return iso_date(transaction.find('transaction-date'))
    elif transaction.find('value') is not None:
        return iso_date_match(transaction.find('value').attrib.get('value-date'))

def budget_year(budget):
    """Returns the year of an inputted object (normally a budget).

       Input:
         budget -- etree budget object
       Returns:
         year (integer) or None
    """
    start = iso_date(budget.find('period-start'))
    end = iso_date(budget.find('period-end'))

    if start and end:
        if (end-start).days <= 370:
            if end.month >= 7:
                return end.year
            else:
                return end.year - 1
        else:
            return None
    else:
        return None

def planned_disbursement_year(planned_disbursement):
    start = iso_date(planned_disbursement.find('period-start'))
    end = iso_date(planned_disbursement.find('period-end'))

    if start and end:
        return budget_year(planned_disbursement)
    elif start:
        return start.year
    else:
        return None

def get_registry_id_matches():
    """Returns a dictionary of publishers who have modified their registry ID
    Returns: Dictionary, where the key is the old registry ID, and the corresponding 
             value is the registry ID that data should be mapped to
    NOTE: Any changes to this function should be replicated in:
          https://github.com/IATI/IATI-Dashboard/blob/master/data.py#L143
    """

    # Load registry IDs for publishers who have changed their registry ID
    reader = csv.DictReader(open('helpers/registry_id_relationships.csv', 'rU'), delimiter=',')
    
    # Load this data into a dictonary
    registry_matches = {}
    for row in reader:
        registry_matches[row['previous_registry_id']] = row['current_registry_id']

    return registry_matches
