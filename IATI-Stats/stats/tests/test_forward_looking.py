import datetime
from lxml import etree
import pytest

from stats.common import budget_year
from stats.dashboard import ActivityStats
from test_comprehensiveness import MockActivityStats


def test_forwardlooking_is_current():
    activity_stats = ActivityStats()

    # If there are no end dates, the activity is current
    activity_stats.element = etree.fromstring('''<iati-activity>
    </iati-activity>''')
    assert activity_stats._forwardlooking_is_current(9990)
    activity_stats.element = etree.fromstring('''<iati-activity>
        <activity-date iso-date="9980-01-01" type="start-planned" />
        <activity-date iso-date="9980-01-01" type="start-actual" />
    </iati-activity>''')
    assert activity_stats._forwardlooking_is_current(9990)

    # If there is an end date before the given year, it's not current
    activity_stats.element = etree.fromstring('''<iati-activity>
        <activity-date iso-date="9980-01-01" type="end-planned" />
    </iati-activity>''')
    assert not activity_stats._forwardlooking_is_current(9990)
    activity_stats.element = etree.fromstring('''<iati-activity>
        <activity-date iso-date="9980-01-01" type="end-actual" />
    </iati-activity>''')
    assert not activity_stats._forwardlooking_is_current(9990)

    # If there is an end date on or after the given year, it is current
    activity_stats.element = etree.fromstring('''<iati-activity>
        <activity-date iso-date="9990-01-01" type="end-planned" />
    </iati-activity>''')
    assert activity_stats._forwardlooking_is_current(9990)
    activity_stats.element = etree.fromstring('''<iati-activity>
        <activity-date iso-date="9990-01-01" type="end-actual" />
    </iati-activity>''')
    assert activity_stats._forwardlooking_is_current(9990)
    activity_stats.element = etree.fromstring('''<iati-activity>
        <activity-date iso-date="9980-01-01" type="end-planned" />
        <activity-date iso-date="9990-01-01" type="end-actual" />
    </iati-activity>''')
    assert activity_stats._forwardlooking_is_current(9990)


def wrap_activity(activity):
    return etree.fromstring('<iati-activities version="2.01">{}</iati-activities>'.format(activity)).find('iati-activity')


def test_forwardlooking_is_current_2xx():
    activity_stats = ActivityStats()

    # If there are no end dates, the activity is current
    activity_stats.element = wrap_activity('''<iati-activity>
    </iati-activity>''')
    assert activity_stats._forwardlooking_is_current(9990)
    activity_stats.element = wrap_activity('''<iati-activity>
        <activity-date iso-date="9980-01-01" type="1" />
        <activity-date iso-date="9980-01-01" type="2" />
    </iati-activity>''')
    assert activity_stats._forwardlooking_is_current(9990)

    # If there is an end date before the given year, it's not current
    activity_stats.element = wrap_activity('''<iati-activity>
        <activity-date iso-date="9980-01-01" type="3" />
    </iati-activity>''')
    assert not activity_stats._forwardlooking_is_current(9990)
    activity_stats.element = wrap_activity('''<iati-activity>
        <activity-date iso-date="9980-01-01" type="4" />
    </iati-activity>''')
    assert not activity_stats._forwardlooking_is_current(9990)

    # If there is an end date on or after the given year, it is current
    activity_stats.element = wrap_activity('''<iati-activity>
        <activity-date iso-date="9990-01-01" type="3" />
    </iati-activity>''')
    assert activity_stats._forwardlooking_is_current(9990)
    activity_stats.element = wrap_activity('''<iati-activity>
        <activity-date iso-date="9990-01-01" type="4" />
    </iati-activity>''')
    assert activity_stats._forwardlooking_is_current(9990)
    activity_stats.element = wrap_activity('''<iati-activity>
        <activity-date iso-date="9980-01-01" type="3" />
        <activity-date iso-date="9990-01-01" type="4" />
    </iati-activity>''')
    assert activity_stats._forwardlooking_is_current(9990)


@pytest.mark.parametrize('major_version', ['1', '2'])
@pytest.mark.parametrize('year', [9980, 9981, 9982])
def test_forwardlooking_activities_with_budgets_true(major_version, year):
    date_code_runs = datetime.date(year, 1, 1)
    activity_stats = MockActivityStats(major_version)
    # Activity with budgets for each year of operation
    activity_stats.element = etree.fromstring('''
        <iati-activity>
            <activity-date iso-date="9980-01-01" type="start-planned" />
            <activity-date iso-date="9982-12-31" type="end-planned" />
            <budget type="1">
               <period-start iso-date="9980-01-01" />
               <period-end iso-date="9980-12-31" />
               <value currency="EUR" value-date="9980-01-01">1000</value>
            </budget>
            <budget type="1">
               <period-start iso-date="9981-01-01" />
               <period-end iso-date="9981-12-31" />
               <value currency="EUR" value-date="9981-01-01">1000</value>
            </budget>
            <budget type="1">
               <period-start iso-date="9982-01-01" />
               <period-end iso-date="9982-12-31" />
               <value currency="EUR" value-date="9982-01-01">1000</value>
            </budget>
        </iati-activity>
    ''' if major_version == '1' else '''
        <iati-activity>
            <activity-date iso-date="9980-01-01" type="1" />
            <activity-date iso-date="9982-12-31" type="3" />
            <budget type="1">
               <period-start iso-date="9980-01-01" />
               <period-end iso-date="9980-12-31" />
               <value currency="EUR" value-date="9980-01-01">1000</value>
            </budget>
            <budget type="1">
               <period-start iso-date="9981-01-01" />
               <period-end iso-date="9981-12-31" />
               <value currency="EUR" value-date="9981-01-01">1000</value>
            </budget>
            <budget type="1">
               <period-start iso-date="9982-01-01" />
               <period-end iso-date="9982-12-31" />
               <value currency="EUR" value-date="9982-01-01">1000</value>
            </budget>
        </iati-activity>
    ''')
    assert activity_stats.forwardlooking_activities_with_budgets(date_code_runs)[year]


@pytest.mark.parametrize('major_version', ['1', '2'])
@pytest.mark.parametrize('year', [9980, 9981, 9982])
def test_forwardlooking_activities_with_budgets_false(major_version, year):
    date_code_runs = datetime.date(year, 1, 1)
    activity_stats = MockActivityStats(major_version)
    # Activity with no budgets for any year of operation
    activity_stats.element = etree.fromstring('''
        <iati-activity>
            <activity-date iso-date="9980-01-01" type="start-planned" />
            <activity-date iso-date="9983-12-31" type="end-planned" />
        </iati-activity>
    ''' if major_version == '1' else '''
        <iati-activity>
            <activity-date iso-date="9980-01-01" type="1" />
            <activity-date iso-date="9983-12-31" type="3" />
        </iati-activity>
    ''')
    assert activity_stats.forwardlooking_activities_with_budgets(date_code_runs)[year] == 0

    date_code_runs = datetime.date(year, 1, 1)
    # Activity ends within six months, regardless that a budget is declared for the full year
    activity_stats.element = etree.fromstring('''
        <iati-activity>
            <activity-date iso-date="9980-01-01" type="start-planned" />
            <activity-date iso-date="9980-05-31" type="end-planned" />
            <budget type="1">
               <period-start iso-date="9980-01-01" />
               <period-end iso-date="9980-12-31" />
               <value currency="EUR" value-date="9980-01-01">1000</value>
            </budget>
        </iati-activity>
    ''' if major_version == '1' else '''
        <iati-activity>
            <activity-date iso-date="9980-01-01" type="1" />
            <activity-date iso-date="9980-05-31" type="3" />
            <budget type="1">
               <period-start iso-date="9980-01-01" />
               <period-end iso-date="9980-12-31" />
               <value currency="EUR" value-date="9980-01-01">1000</value>
            </budget>
        </iati-activity>
    ''')
    assert activity_stats.forwardlooking_activities_with_budgets(date_code_runs)[year] == 0


@pytest.mark.parametrize('major_version', ['1', '2'])
def test_forwardlooking_activities_with_budgets_ends_in_six_months(major_version):
    activity_stats = MockActivityStats(major_version)
    # Activity ends in one year and six months of 9980-01-01, regardless that a budget is declared for both full years
    date_code_runs = datetime.date(9980, 1, 1)
    activity_stats.element = etree.fromstring('''
        <iati-activity>
            <activity-date iso-date="9980-01-01" type="start-planned" />
            <activity-date iso-date="9981-05-31" type="end-planned" />
            <budget type="1">
               <period-start iso-date="9980-01-01" />
               <period-end iso-date="9980-12-31" />
               <value currency="EUR" value-date="9980-01-01">1000</value>
            </budget>
            <budget type="1">
               <period-start iso-date="9981-01-01" />
               <period-end iso-date="9981-12-31" />
               <value currency="EUR" value-date="9981-01-01">1000</value>
            </budget>
        </iati-activity>
    ''' if major_version == '1' else '''
        <iati-activity>
            <activity-date iso-date="9980-01-01" type="1" />
            <activity-date iso-date="9981-05-31" type="3" />
            <budget type="1">
               <period-start iso-date="9980-01-01" />
               <period-end iso-date="9980-12-31" />
               <value currency="EUR" value-date="9980-01-01">1000</value>
            </budget>
            <budget type="1">
               <period-start iso-date="9981-01-01" />
               <period-end iso-date="9981-12-31" />
               <value currency="EUR" value-date="9981-01-01">1000</value>
            </budget>
        </iati-activity>
    ''')
    assert activity_stats.forwardlooking_activities_with_budgets(date_code_runs)[9980] == 1
    assert activity_stats.forwardlooking_activities_with_budgets(date_code_runs)[9981] == 1
    assert activity_stats.forwardlooking_activities_with_budgets(date_code_runs)[9982] == 0


@pytest.mark.parametrize('major_version', ['1', '2'])
def test_get_ratio_commitments_disbursements(major_version):
    # Using expected data
    activity_stats = MockActivityStats(major_version)
    activity_stats.element = etree.fromstring('''
        <iati-activity>
            <transaction>
                <transaction-type code="C"/>
                <value currency="EUR" value-date="2012-10-24">100</value>
                <transaction-date iso-date="2012-10-24" />
            </transaction>
            <transaction>
                <transaction-type code="D"/>
                <value currency="EUR" value-date="2012-10-24">50</value>
                <transaction-date iso-date="2012-10-24" />
            </transaction>
            <transaction>
                <transaction-type code="D"/>
                <value currency="EUR" value-date="2013-10-24">50</value>
                <transaction-date iso-date="2013-10-24" />
            </transaction>
        </iati-activity>
    ''' if major_version == '1' else '''
        <iati-activity>
            <transaction>
                <transaction-type code="2"/>
                <value currency="EUR" value-date="2012-10-24">100</value>
                <transaction-date iso-date="2012-10-24" />
            </transaction>
            <transaction>
                <transaction-type code="3"/>
                <value currency="EUR" value-date="2012-10-24">50</value>
                <transaction-date iso-date="2012-10-24" />
            </transaction>
            <transaction>
                <transaction-type code="3"/>
                <value currency="EUR" value-date="2013-10-24">50</value>
                <transaction-date iso-date="2013-10-24" />
            </transaction>
        </iati-activity>
    ''')
    assert activity_stats._get_ratio_commitments_disbursements(2012) == 0.5

    # Missing transaction date, value and currency
    activity_stats = MockActivityStats(major_version)
    activity_stats.element = etree.fromstring('''
        <iati-activity>
            <transaction>
                <transaction-type code="C"/>
            </transaction>
            <transaction>
                <transaction-type code="D"/>
            </transaction>
        </iati-activity>
    ''' if major_version == '1' else '''
        <iati-activity>
            <transaction>
                <transaction-type code="2"/>
            </transaction>
            <transaction>
                <transaction-type code="3"/>
            </transaction>
        </iati-activity>
    ''')
    assert activity_stats._get_ratio_commitments_disbursements(2012) == None
