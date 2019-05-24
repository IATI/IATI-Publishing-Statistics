# coding=utf-8

from lxml import etree
import datetime
import pytest

from stats.dashboard import ActivityStats

class MockActivityStats(ActivityStats):
    def __init__(self, major_version):
        self.major_version = major_version
        return super(MockActivityStats, self).__init__()

    def _major_version(self):
        return self.major_version

@pytest.mark.parametrize('major_version', ['1', '2'])
def test_comprehensiveness_is_current(major_version):
    activity_stats = MockActivityStats(major_version)
    activity_stats.today = datetime.date(9990, 6, 1)

    activity_stats.element = etree.fromstring('''
        <iati-activity>
            <activity-status code="2"/>
        </iati-activity>
    ''')
    assert activity_stats._comprehensiveness_is_current()

    activity_stats = MockActivityStats(major_version)
    activity_stats.today = datetime.date(9990, 6, 1)
    activity_stats.element = etree.fromstring('''
        <iati-activity>
            <activity-status code="3"/>
        </iati-activity>
    ''')
    assert not activity_stats._comprehensiveness_is_current()

    activity_stats = MockActivityStats(major_version)
    activity_stats.today = datetime.date(9990, 6, 1)
    activity_stats.element = etree.fromstring('''
        <iati-activity>
        </iati-activity>
    ''')
    assert not activity_stats._comprehensiveness_is_current()


    def end_planned_date(datestring):
        """
        Create an activity_stats element with a specified 'end-planned' date.
        Also sets the current date to 9990-06-01

        Args:
            datestring (str): An ISO date to be used as the 'end-planned' date for the activity_stats element to be returned.
        """
        activity_stats = MockActivityStats(major_version)
        activity_stats.today = datetime.date(9990, 6, 1)
        activity_stats.element = etree.fromstring('''
            <iati-activity>
                <activity-date type="{}" iso-date="{}"/>
            </iati-activity>
        '''.format('end-planned' if major_version == '1' else '3', datestring))
        return activity_stats

    # Any planned end dates before the current date should not be calculated as current
    activity_stats = end_planned_date('9989-06-01')
    assert not activity_stats._comprehensiveness_is_current()
    activity_stats = end_planned_date('9989-12-31')
    assert not activity_stats._comprehensiveness_is_current()
    activity_stats = end_planned_date('9990-01-01')
    assert not activity_stats._comprehensiveness_is_current()

    # Any end dates greater than the current date should be calculated as current
    activity_stats = end_planned_date('9990-06-01')
    assert activity_stats._comprehensiveness_is_current()
    activity_stats = end_planned_date('9990-06-02')
    assert activity_stats._comprehensiveness_is_current()
    activity_stats = end_planned_date('9991-06-01')
    assert activity_stats._comprehensiveness_is_current()


    def datetype(typestring):
        """
        Create an activity_stats element with a specified 'activity-date/@type' value and corresponding
        date of 9989-06-01.  Also sets the current date to 9990-06-01

        Keyword arguments:
        typestring -- An 'activity-date/@type' value for the activity_stats element to be returned.
        """
        activity_stats = MockActivityStats(major_version)
        activity_stats.today = datetime.date(9990, 6, 1)
        activity_stats.element = etree.fromstring('''
            <iati-activity>
                <activity-date type="{}" iso-date="9989-06-01"/>
            </iati-activity>
        '''.format(typestring))
        return activity_stats

    # Ignore start dates in computation to determine if an activity is current
    activity_stats = datetype('start-planned' if major_version == '1' else '1')
    assert not activity_stats._comprehensiveness_is_current()
    activity_stats = datetype('start-actual' if major_version == '1' else '2')
    assert not activity_stats._comprehensiveness_is_current()

    # But use all end dates in computation to determine if an activity is current
    activity_stats = datetype('end-planned' if major_version == '1' else '3')
    assert not activity_stats._comprehensiveness_is_current()
    activity_stats = datetype('end-actual' if major_version == '1' else '4')
    assert activity_stats._comprehensiveness_is_current()

    # If there are two end dates, 'end-planned' must be in the future, for the activity to be counted as current
    activity_stats = MockActivityStats(major_version)
    activity_stats.today = datetime.date(9990, 6, 1)
    activity_stats.element = etree.fromstring('''
        <iati-activity>
            <activity-date type="end-planned" iso-date="9989-06-01"/>
            <activity-date type="end-actual" iso-date="9990-12-31"/>
        </iati-activity>
    ''' if major_version == '1' else '''
        <iati-activity>
            <activity-date type="3" iso-date="9989-06-01"/>
            <activity-date type="4" iso-date="9990-12-31"/>
        </iati-activity>
    ''')
    assert not activity_stats._comprehensiveness_is_current()

    # Activity status should take priority over activity date
    activity_stats = MockActivityStats(major_version)
    activity_stats.today = datetime.date(9990, 6, 1)
    activity_stats.element = etree.fromstring('''
        <iati-activity>
            <activity-status code="2"/>
            <activity-date type="{}" iso-date="9990-12-31"/>
        </iati-activity>
    '''.format('end-actual' if major_version == '1' else '4'))
    assert activity_stats._comprehensiveness_is_current()

    activity_stats = MockActivityStats(major_version)
    activity_stats.today = datetime.date(9990, 6, 1)
    activity_stats.element = etree.fromstring('''
        <iati-activity>
            <activity-status code="4"/>
            <activity-date type="{}" iso-date="9990-06-01"/>
        </iati-activity>
    '''.format('end-actual' if major_version == '1' else '4'))
    assert activity_stats._comprehensiveness_is_current()


@pytest.mark.parametrize('major_version', ['1', '2'])
def test_comprehensiveness_empty(major_version):
    activity_stats = MockActivityStats(major_version)
    activity_stats.today = datetime.date(9990, 6, 1)
    activity_stats.element = etree.fromstring('''
        <iati-activity>
            <iati-identifier></iati-identifier>
            <reporting-org></reporting-org>
            <title/>
            <description/>
            <activity-status code="2"/>
            <transaction>
                <transaction-type/>
            </transaction>
            <transaction>
            <!-- provider-activity-id only on one transaction should get no points -->
                <provider-org provider-activity-id="AAA"/>
                <transaction-type code="IF"/>
            </transaction>
            <transaction>
                <transaction-type code="IF"/>
            </transaction>
        </iati-activity>
    ''')
    assert activity_stats.comprehensiveness() == {
        'version': 0,
        'reporting-org': 0,
        'iati-identifier': 0,
        'participating-org': 0,
        'title': 0,
        'description': 0,
        'activity-status': 1,
        'activity-date': 0,
        'sector': 0,
        'country_or_region': 0,
        'transaction_commitment': 0,
        'transaction_spend': 0,
        'transaction_currency': 0,
        'transaction_traceability': 0,
        'budget': 0,
        'budget_not_provided': 0,
        'contact-info': 0,
        'location': 0,
        'location_point_pos': 0,
        'sector_dac': 0,
        'capital-spend': 0,
        'document-link': 0,
        'activity-website': 0,
        'recipient_language': 0,
        'conditions_attached': 0,
        'result_indicator': 0,
        'aid_type': 0
    }


@pytest.mark.parametrize('major_version', ['1','2'])
def test_comprehensiveness_full(major_version):
    activity_stats = MockActivityStats(major_version)
    activity_stats.today = datetime.date(9990, 6, 1)
    root = etree.fromstring('''
        <iati-activities version="1.05">
            <iati-activity xml:lang="en">
                <reporting-org ref="AA-AAA">Reporting ORG Name</reporting-org>
                <iati-identifier>AA-AAA-1</iati-identifier>
                <participating-org/>
                <title>A title</title>
                <description>A description</description>
                <activity-status code="2"/>
                <activity-date type="start-actual" iso-date="9989-05-01" />
                <sector vocabulary="DAC"/>
                <recipient-country code="AI"/>
                <default-aid-type code="A01" />
                <transaction>
                    <transaction-type code="C"/>
                    <value currency="" value-date="2014-01-01"/>
                </transaction>
                <transaction>
                    <transaction-type code="E"/>
                    <value currency="" value-date="2014-01-01"/>
                </transaction>
                <transaction>
                    <provider-org provider-activity-id="AAA"/>
                    <transaction-type code="IF"/>
                    <value currency="" value-date="2014-01-01"/>
                </transaction>
                <budget/>
                <contact-info>
                    <email>test@example.org</email>
                </contact-info>
                <location>
                    <point srsName="http://www.opengis.net/def/crs/EPSG/0/4326">
                        <pos>31.616944 65.716944</pos>
                    </point>
                </location>
                <capital-spend percentage=""/>
                <document-link/>
                <activity-website/>
                <conditions attached="0"/>
                <result>
                    <indicator/>
                </result>
            </iati-activity>
        </iati-activities>
    ''' if major_version == '1' else '''
        <iati-activities version="2.01">
            <iati-activity xml:lang="en">
                <reporting-org ref="AA-AAA">
                    <narrative>Reporting ORG Name</narrative>
                </reporting-org>
                <iati-identifier>AA-AAA-1</iati-identifier>
                <participating-org/>
                <title>
                    <narrative>A title</narrative>
                </title>
                <description>
                    <narrative>A description</narrative>
                </description>
                <activity-status code="2"/>
                <activity-date type="2" iso-date="9989-05-01" />
                <sector vocabulary="1"/>
                <recipient-country code="AI"/>
                <default-aid-type code="A01" />
                <transaction>
                    <transaction-type code="2"/><!-- Commitment -->
                    <value currency="" value-date="2014-01-01"/>
                </transaction>
                <transaction>
                    <transaction-type code="3"/><!-- Expenditure -->
                    <value currency="" value-date="2014-01-01"/>
                </transaction>
                <transaction>
                    <provider-org provider-activity-id="AAA"/>
                    <transaction-type code="1"/><!-- Incoming Funds -->
                    <value currency="" value-date="2014-01-01"/>
                </transaction>
                <budget/>
                <contact-info>
                    <email>test@example.org</email>
                </contact-info>
                <location>
                    <point srsName="http://www.opengis.net/def/crs/EPSG/0/4326">
                        <pos>31.616944 65.716944</pos>
                    </point>
                </location>
                <capital-spend percentage=""/>
                <document-link/>
                <document-link>
                    <!-- Activity website -->
                    <category code="A12" />
                </document-link>
                <conditions attached="0"/>
                <result>
                    <indicator/>
                </result>
            </iati-activity>
        </iati-activities>
    ''')
    activity_stats.element = root.find('iati-activity')
    assert all(type(x) == int for x in activity_stats.comprehensiveness().values())
    assert activity_stats.comprehensiveness() == {
        'version': 1,
        'reporting-org': 1,
        'iati-identifier': 1,
        'participating-org': 1,
        'title': 1,
        'description': 1,
        'activity-status': 1,
        'activity-date': 1,
        'sector': 1,
        'country_or_region': 1,
        'transaction_commitment': 1,
        'transaction_spend': 1,
        'transaction_currency': 1,
        'transaction_traceability': 1,
        'budget': 1,
        'budget_not_provided': 0,
        'contact-info': 1,
        'location': 1,
        'location_point_pos': 1,
        'sector_dac': 1,
        'capital-spend': 1,
        'document-link': 1,
        'activity-website': 1,
        'recipient_language': 1,
        'conditions_attached': 1,
        'result_indicator': 1,
        'aid_type': 1
    }

    # Check recipient-region independently
    activity_stats.element = etree.fromstring('''
        <iati-activity>
            <transaction>
                <recipient-region/>
            </transaction>
        </iati-activity>
    ''')
    comprehensiveness = activity_stats.comprehensiveness()
    assert comprehensiveness['country_or_region'] == 1


@pytest.mark.parametrize('major_version', ['1', '2'])
def test_comprehensiveness_other_passes(major_version):
    activity_stats = MockActivityStats(major_version)
    activity_stats.today = datetime.date(9990, 6, 1)
    root = etree.fromstring('''
        <iati-activities>
            <iati-activity default-currency="">
            <!-- default currency can be used instead of at transaction level -->
                <activity-status code="2"/>
                <activity-date type="start-planned" iso-date="9989-05-01" />
                <transaction>
                    <transaction-type code="D"/>
                    <value value-date="2014-01-01"/>
                    <aid-type code="A01" />
                </transaction>
            </iati-activity>
        </iati-activities>
    ''' if major_version == '1' else '''
        <iati-activities>
            <iati-activity default-currency="">
            <!-- default currency can be used instead of at transaction level -->
                <activity-status code="2"/>
                <activity-date type="1" iso-date="9989-05-01" />
                <transaction>
                    <transaction-type code="3"/><!-- Disbursement -->
                    <value value-date="2014-01-01"/>
                    <aid-type code="A01" />
                </transaction>
            </iati-activity>
        </iati-activities>
    ''')
    activity_stats.element = root.find('iati-activity')
    assert all(type(x) == int for x in activity_stats.comprehensiveness().values())
    assert activity_stats.comprehensiveness() == {
        'version': 0,
        'reporting-org': 0,
        'iati-identifier': 0,
        'participating-org': 0,
        'title': 0,
        'description': 0,
        'activity-status': 1,
        'activity-date': 1,
        'sector': 0,
        'country_or_region': 0,
        'transaction_commitment': 0,
        'transaction_spend': 1,
        'transaction_currency': 1,
        'transaction_traceability': 0,
        'budget': 0,
        'budget_not_provided': 0,
        'contact-info': 0,
        'location': 0,
        'location_point_pos': 0,
        'sector_dac': 0,
        'capital-spend': 0,
        'document-link': 0,
        'activity-website': 0,
        'recipient_language': 0,
        'conditions_attached': 0,
        'result_indicator': 0,
        'aid_type': 1
    }


@pytest.mark.parametrize('major_version', ['1', '2'])
def test_comprehensiveness_location_other_passes(major_version):
    activity_stats = MockActivityStats(major_version)
    activity_stats.today = datetime.date(9990, 6, 1)
    activity_stats.element = etree.fromstring('''
        <iati-activity default-currency="">
            <activity-status code="2"/>
            <location>
                <name>Name</name>
            </location>
        </iati-activity>
    ''')
    assert activity_stats.comprehensiveness()['location'] == 1
    assert activity_stats.comprehensiveness()['location_point_pos'] == 0

    activity_stats = MockActivityStats(major_version)
    activity_stats.today = datetime.date(9990, 6, 1)
    activity_stats.element = etree.fromstring('''
        <iati-activity default-currency="">
            <activity-status code="2"/>
            <location>
                <description>Name</description>
            </location>
        </iati-activity>
    ''')
    assert activity_stats.comprehensiveness()['location'] == 1
    assert activity_stats.comprehensiveness()['location_point_pos'] == 0

    activity_stats = MockActivityStats(major_version)
    activity_stats.today = datetime.date(9990, 6, 1)
    activity_stats.element = etree.fromstring('''
        <iati-activity default-currency="">
            <activity-status code="2"/>
            <location>
                <location-administrative>Name</location-administrative>
            </location>
        </iati-activity>
    ''')
    assert activity_stats.comprehensiveness()['location'] == 1
    assert activity_stats.comprehensiveness()['location_point_pos'] == 0


@pytest.mark.parametrize('major_version', ['1', '2'])
def test_comprehensiveness_recipient_language_passes(major_version):
    # Set one and only one recipient-country
    # Country code "AI" has valid language code "en" in helpers/transparency_indicator/country_lang_map.csv

    activity_stats = MockActivityStats(major_version)
    activity_stats.today = datetime.date(9990, 6, 1)
    activity_stats.element = etree.fromstring('''
        <iati-activity>
            <title xml:lang="en">Activity title</title>
            <description type="1" xml:lang="en">
                General activity description text.  Long description of the activity with
                no particular structure.
            </description>
            <activity-status code="2"/>
            <recipient-country code="AI"/>
        </iati-activity>
    ''' if major_version == '1' else '''
        <iati-activity>
            <title>
                <narrative xml:lang="en">Activity title</narrative>
            </title>
            <description type="1">
                <narrative xml:lang="en">
                    General activity description text.  Long description of the activity with
                    no particular structure.
                </narrative>
            </description>
            <activity-status code="2"/>
            <recipient-country code="AI"/>
        </iati-activity>
    ''')
    assert activity_stats.comprehensiveness()['recipient_language'] == 1

    activity_stats = MockActivityStats(major_version)
    activity_stats.today = datetime.date(9990, 6, 1)
    activity_stats.element = etree.fromstring('''
        <iati-activity>
            <title xml:lang="en">Activity title</title>
            <description type="1" xml:lang="en">
                General activity description text.  Long description of the activity with
                no particular structure.
            </description>
            <recipient-country code="AI"/>
            <activity-status code="2"/>
        </iati-activity>
    ''' if major_version == '1' else '''
        <iati-activity>
            <title>
                <narrative xml:lang="en">Activity title</narrative>
                <narrative xml:lang="fr">Titre de l'activité</narrative>
            </title>
            <description type="1">
                <narrative xml:lang="en">
                    General activity description text.  Long description of the activity with
                    no particular structure.
                </narrative>
                <narrative xml:lang="fr">
                    Activité générale du texte de description. Longue description de l'activité
                    sans structure particulière.
                </narrative>
            </description>
            <activity-status code="2"/>
            <recipient-country code="AI"/>
        </iati-activity>
    ''')
    assert activity_stats.comprehensiveness()['recipient_language'] == 1


@pytest.mark.parametrize('major_version', ['1', '2'])
def test_comprehensiveness_recipient_language_fails(major_version):
    # Set one and only one recipient-country
    # Country code "AI" has valid language code "en" in helpers/transparency_indicator/country_lang_map.csv
    activity_stats = MockActivityStats(major_version)
    activity_stats.today = datetime.date(9990, 6, 1)
    activity_stats.element = etree.fromstring('''
        <iati-activity>
            <title>Activity title</title>
            <description type="1">
                General activity description text.  Long description of the activity with
                no particular structure.
            </description>
            <activity-status code="2"/>
            <recipient-country code="AI"/>
        </iati-activity>
    ''' if major_version == '1' else '''
        <iati-activity>
            <title>
                <narrative>Activity title</narrative>
            </title>
            <description type="1">
                <narrative>
                    General activity description text.  Long description of the activity with
                    no particular structure.
                </narrative>
            </description>
            <activity-status code="2"/>
            <recipient-country code="AI"/>
        </iati-activity>
    ''')
    assert activity_stats.comprehensiveness()['recipient_language'] == 0

    activity_stats = MockActivityStats(major_version)
    activity_stats.today = datetime.date(9990, 6, 1)
    activity_stats.element = etree.fromstring('''
        <iati-activity>
            <title xml:lang="fr">Titre de l'activité</title>
            <description type="1" xml:lang="fr">
                Activité générale du texte de description. Longue description de l'activité
                sans structure particulière.
            </description>
            <activity-status code="2"/>
            <recipient-country code="AI"/>
        </iati-activity>
    ''' if major_version == '1' else '''
        <iati-activity>
            <title>
                <narrative xml:lang="fr">Titre de l'activité</narrative>
            </title>
            <description type="1">
                <narrative xml:lang="fr">
                    Activité générale du texte de description. Longue description de l'activité
                    sans structure particulière.
                </narrative>
            </description>
            <activity-status code="2"/>
            <recipient-country code="AI"/>
        </iati-activity>
    ''')
    assert activity_stats.comprehensiveness()['recipient_language'] == 0


@pytest.mark.parametrize('major_version', ['1', '2'])
def test_comprehensiveness_recipient_language_fails_mulitple_countries(major_version):
    # Set more than one recipient-country

    activity_stats = MockActivityStats(major_version)
    activity_stats.today = datetime.date(9990, 6, 1)
    activity_stats.element = etree.fromstring('''
        <iati-activity>
            <title xml:lang="en">Activity title</title>
            <description type="1" xml:lang="en">
                General activity description text.  Long description of the activity with
                no particular structure.
            </description>
            <activity-status code="2"/>
            <recipient-country code="AF" percentage="50" />
            <recipient-country code="AI" percentage="50" />
        </iati-activity>
    ''' if major_version == '1' else '''
        <iati-activity>
            <title>
                <narrative xml:lang="en">Activity title</narrative>
            </title>
            <description type="1">
                <narrative xml:lang="en">
                    General activity description text.  Long description of the activity with
                    no particular structure.
                </narrative>
            </description>
            <activity-status code="2"/>
            <recipient-country code="AF" percentage="50" />
            <recipient-country code="AI" percentage="50" />
        </iati-activity>
    ''')
    assert activity_stats.comprehensiveness()['recipient_language'] == 0


@pytest.mark.parametrize('major_version', ['1', '2'])
def test_comprehensiveness_sector_other_passes(major_version):
    activity_stats = MockActivityStats(major_version)
    activity_stats.today = datetime.date(9990, 6, 1)
    activity_stats.element = etree.fromstring('''
        <iati-activity default-currency="">
            <activity-status code="2"/>
            <sector/>
        </iati-activity>
    ''')
    assert activity_stats.comprehensiveness()['sector'] == 1
    assert activity_stats.comprehensiveness()['sector_dac'] == 1

    activity_stats = MockActivityStats(major_version)
    activity_stats.today = datetime.date(9990, 6, 1)
    activity_stats.element = etree.fromstring('''
        <iati-activity default-currency="">
            <activity-status code="2"/>
            <sector vocabulary="test"/>
        </iati-activity>
    ''')
    assert activity_stats.comprehensiveness()['sector'] == 1
    assert activity_stats.comprehensiveness()['sector_dac'] == 0

    activity_stats = MockActivityStats(major_version)
    activity_stats.today = datetime.date(9990, 6, 1)
    activity_stats.element = etree.fromstring('''
        <iati-activity default-currency="">
            <activity-status code="2"/>
            <sector vocabulary="{}"/>
        </iati-activity>
    '''.format('DAC' if major_version == '1' else '1'))
    assert activity_stats.comprehensiveness()['sector'] == 1
    assert activity_stats.comprehensiveness()['sector_dac'] == 1

    activity_stats = MockActivityStats(major_version)
    activity_stats.today = datetime.date(9990, 6, 1)
    activity_stats.element = etree.fromstring('''
        <iati-activity default-currency="">
            <activity-status code="2"/>
            <sector vocabulary="{}"/>
        </iati-activity>
    '''.format('DAC-3' if major_version == '1' else '2'))
    assert activity_stats.comprehensiveness()['sector'] == 1
    assert activity_stats.comprehensiveness()['sector_dac'] == 1


@pytest.mark.parametrize('major_version', ['1', '2'])
@pytest.mark.parametrize('key', [
    'version', 'participating-org', 'activity-status',
    'activity-date', 'sector', 'country_or_region',
    'transaction_commitment', 'transaction_currency',
    'budget',
    'location_point_pos', 'sector_dac', 'document-link', 'activity-website',
    'aid_type'
    # iati_identifier is exluded as it does not validate for v1.xx data as a special case: https://github.com/IATI/IATI-Dashboard/issues/399
])
def test_comprehensiveness_with_validation(key, major_version):
    activity_stats_not_valid = MockActivityStats(major_version)
    activity_stats_not_valid.today = datetime.date(2014, 1, 1)
    root_not_valid = etree.fromstring('''
        <iati-activities version="9.99">
            <iati-activity>
                <reporting-org ref="BBB"/>
                <iati-identifier>AAA-1</iati-identifier>
                <participating-org role="Implementing"/>
                <activity-status />
                <activity-date iso-date="9990-05-01" />
                <!-- Must have at least one activity-date of type start-planned or start-actual with valid date -->
                <activity-date type="end-planned" iso-date="2014-01-01" />
                <activity-date type="start-planned" iso-date="2014-0101" />
                <sector vocabulary="DAC" percentage="100" code="a" />
                <sector vocabulary="DAC" percentage="100" code="b" />
                <sector vocabulary="DAC-3" percentage="100" code="a" />
                <sector vocabulary="DAC-3" percentage="100" code="b" />
                <sector vocabulary="RO" percentage="100" />
                <sector vocabulary="RO" percentage="100" />
                <recipient-country percentage="100"/>
                <recipient-region percentage="100"/>
                <default-aid-type code="non-valid-code" />
                <transaction>
                    <transaction-type code="C"/>
                    <value value-date="" currency=""/>
                </transaction>
                <transaction>
                    <transaction-type code="D"/>
                    <value value-date="" currency=""/>
                </transaction>
                <budget/>
                <location>
                    <point>
                        <pos>1.5,2</pos>
                    </point>
                </location>
                <document-link url="">
                    <category code="" />
                </document-link>
                <activity-website>notaurl</activity-website>
            </iati-activity>
        </iati-activities>
    ''' if major_version == '1' else '''
        <iati-activities version="9.99">
            <iati-activity>
                <reporting-org ref="BBB"/>
                <iati-identifier>AAA-1</iati-identifier>
                <participating-org role="4"/><!-- Implementing -->
                <activity-status />
                <activity-date iso-date="9990-05-01" />
                <!-- Must have at least one activity-date of type start-planned or start-actual with valid date -->
                <activity-date type="3" iso-date="2014-01-01" />
                <activity-date type="1" iso-date="2014-0101" />
                <sector vocabulary="1" percentage="100" code="a" />
                <sector vocabulary="1" percentage="100" code="b" />
                <sector vocabulary="2" percentage="100" code="a" />
                <sector vocabulary="2" percentage="100" code="b" />
                <sector vocabulary="99" percentage="100" />
                <sector vocabulary="99" percentage="100" />
                <recipient-country percentage="100"/>
                <recipient-region percentage="100"/>
                <default-aid-type code="non-valid-code" />
                <transaction>
                    <transaction-type code="2"/>
                    <value value-date="" currency=""/>
                </transaction>
                <transaction>
                    <transaction-type code="3"/>
                    <value value-date="" currency=""/>
                </transaction>
                <budget/>
                <location>
                    <point>
                        <pos>1.5,2</pos>
                    </point>
                </location>
                <document-link url="">
                    <category code="" />
                </document-link>
                <document-link url="">
                    <category code="A12" />
                </document-link>
                <activity-website>notaurl</activity-website>
            </iati-activity>
        </iati-activities>
    ''')
    activity_stats_not_valid.element = root_not_valid.find('iati-activity')
    activity_stats_valid = MockActivityStats(major_version)
    activity_stats_valid.today = datetime.date(2014, 1, 1)
    root_valid = etree.fromstring('''
        <iati-activities version="1.04">
            <iati-activity>
                <reporting-org ref="AAA"/>
                <iati-identifier>AAA-1</iati-identifier>
                <participating-org role="Funding"/>
                <activity-status code="2" />
                <!-- Must have at least one activity-date in the past year (if 'end-actual') or in the future (if type 'end-planned') -->
                <activity-date iso-date="2014-01-01" type="start-planned" />
                <activity-date iso-date="2015-06-01" type="end-planned" />
                <sector vocabulary="DAC" percentage="50" code="11220" />
                <sector vocabulary="DAC" percentage="50" code="11240" />
                <sector vocabulary="DAC-3" percentage="50" code="111" />
                <sector vocabulary="DAC-3" percentage="50" code="112" />
                <sector vocabulary="RO" percentage="51" />
                <sector vocabulary="RO" percentage="49" />
                <recipient-country percentage="44.5"/>
                <recipient-region percentage="55.5"/>
                <default-aid-type code="A01" />
                <transaction>
                    <transaction-type code="C"/>
                    <value value-date="2014-01-01" currency="GBP">1.0</value>
                    <transaction-date iso-date="2014-01-01" />
                </transaction>
                <transaction>
                    <transaction-type code="D"/>
                    <value value-date="2014-01-01" currency="GBP">1.0</value>
                    <transaction-date iso-date="2014-01-01" />
                </transaction>
                <budget>
                    <period-start iso-date="2014-01-01"/>
                    <period-end iso-date="2014-01-02"/>
                    <value value-date="2014-01-01">1.0</value>
                </budget>
                <location>
                    <point>
                        <pos>1.5 2</pos>
                    </point>
                </location>
                <document-link url="http://example.org/">
                    <category code="A01" />
                </document-link>
                <activity-website>http://example.org/</activity-website>
            </iati-activity>
        </iati-activities>
    ''' if major_version == '1' else '''
        <iati-activities version="2.01">
            <iati-activity>
                <reporting-org ref="AAA"/>
                <iati-identifier>AAA-1</iati-identifier>
                <participating-org role="1"/><!-- Funding -->
                <activity-status code="2" />
                <!-- Must have at least one activity-date in the past year (if '4') or in the future (if type '3') -->
                <activity-date iso-date="2014-01-01" type="1" />
                <activity-date iso-date="2015-06-01" type="3" />
                <sector vocabulary="1" percentage="50" code="11220" />
                <sector vocabulary="1" percentage="50" code="11240" />
                <sector vocabulary="2" percentage="50" code="111" />
                <sector vocabulary="2" percentage="50" code="112" />
                <sector vocabulary="99" percentage="51" />
                <sector vocabulary="99" percentage="49" />
                <recipient-country percentage="44.5"/>
                <recipient-region percentage="55.5"/>
                <default-aid-type code="A01" />
                <transaction>
                    <transaction-type code="2"/>
                    <value value-date="2014-01-01" currency="GBP">1.0</value>
                    <transaction-date iso-date="2014-01-01" />
                </transaction>
                <transaction>
                    <transaction-type code="3"/>
                    <value value-date="2014-01-01" currency="GBP">1.0</value>
                    <transaction-date iso-date="2014-01-01" />
                </transaction>
                <budget>
                    <period-start iso-date="2014-01-01"/>
                    <period-end iso-date="2014-01-02"/>
                    <value value-date="2014-01-01">1.0</value>
                </budget>
                <location>
                    <point>
                        <pos>1.5 2</pos>
                    </point>
                </location>
                <document-link url="http://example.org/">
                    <category code="A01" />
                </document-link>
                <document-link url="http://example.org/">
                    <category code="A12" />
                </document-link>
            </iati-activity>
        </iati-activities>
    ''')
    activity_stats_valid.element = root_valid.find('iati-activity')
    comprehensiveness = activity_stats_not_valid.comprehensiveness()
    not_valid = activity_stats_not_valid.comprehensiveness_with_validation()
    valid = activity_stats_valid.comprehensiveness_with_validation()
    assert comprehensiveness[key] == 1
    assert not_valid[key] == 0
    assert valid[key] == 1


@pytest.mark.parametrize('major_version', ['1', '2'])
def test_comprehensiveness_with_validation_transaction_spend(major_version):
    key = 'transaction_spend'
    activity_stats = MockActivityStats(major_version)
    activity_stats.today = datetime.date(9990, 6, 1)
    root = etree.fromstring('''
        <iati-activities>
            <iati-activity>
                <activity-status code="2"/>
                <activity-date type="start-planned" iso-date="9989-05-01" />
                <transaction>
                    <transaction-type code="D"/>
                    <value value-date="" currency=""/>
                </transaction>
            </iati-activity>
        </iati-activities>
    ''' if major_version == '1' else '''
        <iati-activities>
            <iati-activity>
                <activity-status code="2"/>
                <activity-date type="1" iso-date="9989-05-01" />
                <transaction>
                    <transaction-type code="3"/>
                    <value value-date="" currency=""/>
                </transaction>
            </iati-activity>
        </iati-activities>
    ''')
    activity_stats.element = root.find('iati-activity')
    activity_stats_valid = MockActivityStats(major_version)
    activity_stats_valid.today = datetime.date(9990, 6, 1)
    root_valid = etree.fromstring('''
        <iati-activities>
            <iati-activity>
                <activity-status code="2"/>
                <activity-date type="start-planned" iso-date="9989-05-01" />
                <transaction>
                    <transaction-type code="D"/>
                    <value value-date="2014-01-01" currency="GBP">1.0</value>
                    <transaction-date iso-date="2014-01-01" />
                </transaction>
            </iati-activity>
        </iati-activities>
    ''' if major_version == '1' else '''
        <iati-activities>
            <iati-activity>
                <activity-status code="2"/>
                <activity-date type="1" iso-date="9989-05-01" />
                <transaction>
                    <transaction-type code="3"/>
                    <value value-date="2014-01-01" currency="GBP">1.0</value>
                    <transaction-date iso-date="2014-01-01" />
                </transaction>
            </iati-activity>
        </iati-activities>
    ''')
    activity_stats_valid.element = root_valid.find('iati-activity')
    comprehensiveness = activity_stats.comprehensiveness()
    print(activity_stats._comprehensiveness_bools())
    not_valid = activity_stats.comprehensiveness_with_validation()
    valid = activity_stats_valid.comprehensiveness_with_validation()
    assert comprehensiveness[key] == 1
    assert not_valid[key] == 0
    assert valid[key] == 1


@pytest.mark.parametrize('major_version', ['1', '2'])
def test_valid_single_recipient_country(major_version):
    activity_stats = MockActivityStats(major_version)
    activity_stats.element = etree.fromstring('''
        <iati-activity>
            <activity-status code="2"/>
            <recipient-country/>
        </iati-activity>
    ''')
    assert activity_stats.comprehensiveness_with_validation()['country_or_region'] == 1

    activity_stats = MockActivityStats(major_version)
    activity_stats.element = etree.fromstring('''
        <iati-activity>
            <activity-status code="2"/>
            <recipient-region/>
        </iati-activity>
    ''')
    assert activity_stats.comprehensiveness_with_validation()['country_or_region'] == 1


@pytest.mark.parametrize('major_version', ['1', '2'])
def test_aid_type_passes(major_version):
    activity_stats = MockActivityStats(major_version)
    activity_stats.element = etree.fromstring('''
        <iati-activity>
            <activity-status code="2"/>
            <default-aid-type code="A01" />
        </iati-activity>
    ''')
    assert activity_stats.comprehensiveness()['aid_type'] == 1

    activity_stats = MockActivityStats(major_version)
    activity_stats.element = etree.fromstring('''
        <iati-activity>
            <activity-status code="2"/>
            <transaction>
                <aid-type code="A01" />
            </transaction>
            <transaction>
                <aid-type code="B01" />
            </transaction>
        </iati-activity>
    ''')
    assert activity_stats.comprehensiveness()['aid_type'] == 1


@pytest.mark.parametrize('major_version', ['1', '2'])
def test_aid_type_fails(major_version):
    activity_stats = MockActivityStats(major_version)
    activity_stats.element = etree.fromstring('''
        <iati-activity>
            <activity-status code="2"/>
            <transaction>
                <aid-type code="A01" />
            </transaction>
            <transaction>

            </transaction>
        </iati-activity>
    ''')
    assert activity_stats.comprehensiveness()['aid_type'] == 0


@pytest.mark.parametrize('major_version', ['1', '2'])
def test_aid_type_valid(major_version):
    activity_stats = MockActivityStats(major_version)
    activity_stats.element = etree.fromstring('''
        <iati-activity>
            <activity-status code="2"/>
            <default-aid-type code="A01" />
        </iati-activity>
    ''')
    assert activity_stats.comprehensiveness_with_validation()['aid_type'] == 1

    activity_stats = MockActivityStats(major_version)
    activity_stats.element = etree.fromstring('''
        <iati-activity>
            <activity-status code="2"/>
            <default-aid-type code="non-valid-code" />
            <transaction>
                <aid-type code="A01" />
            </transaction>
            <transaction>
                <aid-type code="B01" />
            </transaction>
        </iati-activity>
    ''')
    assert activity_stats.comprehensiveness_with_validation()['aid_type'] == 1


@pytest.mark.parametrize('major_version', ['1', '2'])
def test_aid_type_not_valid(major_version):
    activity_stats = MockActivityStats(major_version)
    activity_stats.element = etree.fromstring('''
        <iati-activity>
            <activity-status code="2"/>
            <default-aid-type code="non-valid-code" />
        </iati-activity>
    ''')
    assert activity_stats.comprehensiveness_with_validation()['aid_type'] == 0

    activity_stats = MockActivityStats(major_version)
    activity_stats.element = etree.fromstring('''
        <iati-activity>
            <activity-status code="2"/>
            <transaction>
                <aid-type code="A01" />
            </transaction>
            <transaction>
                <aid-type code="non-valid-code" />
            </transaction>
        </iati-activity>
    ''')
    assert activity_stats.comprehensiveness_with_validation()['aid_type'] == 0

    activity_stats = MockActivityStats(major_version)
    activity_stats.element = etree.fromstring('''
        <iati-activity>
            <activity-status code="2"/>
            <transaction>

            </transaction>
            <transaction>

            </transaction>
        </iati-activity>
    ''')
    assert activity_stats.comprehensiveness_with_validation()['aid_type'] == 0


# Note v1.xx data gets an automatic pass for iati_identifier as a special case: https://github.com/IATI/IATI-Dashboard/issues/399
def test_iati_identifier_valid_v1_passes():
    activity_stats = MockActivityStats('1')
    activity_stats.element = etree.fromstring('''
        <iati-activity>
            <reporting-org ref="AA-AAA">Reporting ORG Name</reporting-org>
            <iati-identifier>AA-AAA-1</iati-identifier>
            <activity-status code="2"/>
        </iati-activity>
    ''')
    assert activity_stats.comprehensiveness_with_validation()['iati-identifier'] == 1

    activity_stats = MockActivityStats('1')
    activity_stats.element = etree.fromstring('''
        <iati-activity>
            <reporting-org ref="AA-AAA">Reporting ORG Name</reporting-org>
            <iati-identifier>NOT-PREFIXED-WITH-REPORTING-ORG_AA-AAA-1</iati-identifier>
            <activity-status code="2"/>
        </iati-activity>
    ''')
    assert activity_stats.comprehensiveness_with_validation()['iati-identifier'] == 1


def test_iati_identifier_valid_v2_passes():
    activity_stats = MockActivityStats('2')
    activity_stats.element = etree.fromstring('''
        <iati-activity>
            <reporting-org ref="AA-AAA">
                <narrative>Reporting ORG Name</narrative>
            </reporting-org>
            <iati-identifier>AA-AAA-1</iati-identifier>
            <activity-status code="2"/>
        </iati-activity>
    ''')
    assert activity_stats.comprehensiveness_with_validation()['iati-identifier'] == 1

    activity_stats = MockActivityStats('2')
    activity_stats.element = etree.fromstring('''
        <iati-activity>
            <reporting-org ref="BB-BBB">
                <narrative>A new reporting org name (BB-BBB)</narrative>
            </reporting-org>
            <iati-identifier>AA-AAA-1</iati-identifier>
            <other-identifier ref="AA-AAA" type="B1">
                <owner-org ref="BB-BBB">
                    <narrative>Reporting org name (who previously were known as AA-AAA)</narrative>
                </owner-org>
            </other-identifier>
            <activity-status code="2"/>
        </iati-activity>
    ''')
    assert activity_stats.comprehensiveness_with_validation()['iati-identifier'] == 1


def test_iati_identifier_valid_v2_fails():
    activity_stats = MockActivityStats('2')
    activity_stats.element = etree.fromstring('''
        <iati-activity>
            <reporting-org ref="BB-BBB">
                <narrative>Reporting ORG Name</narrative>
            </reporting-org>
            <iati-identifier>AA-AAA-1</iati-identifier>
            <activity-status code="2"/>
        </iati-activity>
    ''')
    assert activity_stats.comprehensiveness_with_validation()['iati-identifier'] == 0

    activity_stats = MockActivityStats('2')
    activity_stats.element = etree.fromstring('''
        <iati-activity>
            <reporting-org ref="BB-BBB">
                <narrative>A new reporting org name (BB-BBB)</narrative>
            </reporting-org>
            <iati-identifier>AA-AAA-1</iati-identifier>
            <other-identifier ref="AA-AAA" type="A1"><!-- @type set, but not of value 'B1'-->
            </other-identifier>
            <activity-status code="2"/>
        </iati-activity>
    ''')
    assert activity_stats.comprehensiveness_with_validation()['iati-identifier'] == 0


@pytest.mark.parametrize('major_version', ['1', '2'])
def test_valid_sector_no_vocab(major_version):
    activity_stats = MockActivityStats(major_version)
    activity_stats.today = datetime.date(2014, 1, 1)
    root = etree.fromstring('''
        <iati-activities>
            <iati-activity>
                <activity-status code="2"/>
                <sector code="a" />
                <sector code="b" />
            </iati-activity>
        </iati-activities>
    ''')
    activity_stats.element = root.find('iati-activity')
    activity_stats_valid = MockActivityStats(major_version)
    activity_stats_valid.today = datetime.date(9990, 6, 1)
    root_valid = etree.fromstring('''
        <iati-activities>
            <iati-activity>
                <activity-status code="2"/>
                <sector code="11220" />
                <sector code="11240" />
            </iati-activity>
        </iati-activities>
    ''')
    activity_stats_valid.element = root_valid.find('iati-activity')
    assert activity_stats.comprehensiveness()['sector_dac'] == 1
    assert activity_stats.comprehensiveness_with_validation()['sector_dac'] == 0
    assert activity_stats_valid.comprehensiveness_with_validation()['sector_dac'] == 1


@pytest.mark.parametrize('major_version', ['1', '2'])
def test_valid_location(major_version):
    activity_stats = MockActivityStats(major_version)
    activity_stats.today = datetime.date(9990, 6, 1)
    activity_stats.element = etree.fromstring('''
        <iati-activity>
            <activity-status code="2"/>
            <location>
                <point>
                    <pos>+1.5 -2</pos>
                </point>
            </location>
        </iati-activity>
    ''')
    assert activity_stats.comprehensiveness_with_validation()['location_point_pos'] == 1

    activity_stats = MockActivityStats(major_version)
    activity_stats.today = datetime.date(9990, 6, 1)
    activity_stats.element = etree.fromstring('''
        <iati-activity>
            <activity-status code="2"/>
            <location>
                <point>
                    <pos>x1.5 -2</pos>
                </point>
            </location>
        </iati-activity>
    ''')
    assert activity_stats.comprehensiveness_with_validation()['location_point_pos'] == 0

    activity_stats = MockActivityStats(major_version)
    activity_stats.today = datetime.date(9990, 6, 1)
    activity_stats.element = etree.fromstring('''
        <iati-activity>
            <activity-status code="2"/>
            <location>
                <point>
                    <pos>1,5 2,5</pos>
                </point>
            </location>
        </iati-activity>
    ''')
    assert activity_stats.comprehensiveness_with_validation()['location_point_pos'] == 0


@pytest.mark.parametrize('major_version', ['1', '2'])
def test_comprehensiveness_transaction_level_elements(major_version):
    activity_stats = MockActivityStats(major_version)
    activity_stats.today = datetime.date(9990, 6, 1)
    activity_stats.element = etree.fromstring('''
        <iati-activity>
            <activity-status code="2"/>
            <transaction>
                <sector/>
                <recipient-country/>
            </transaction>
        </iati-activity>
    ''')
    comprehensiveness = activity_stats.comprehensiveness()
    assert comprehensiveness['sector'] == (0 if major_version == '1' else 1)
    assert comprehensiveness['country_or_region'] == (0 if major_version == '1' else 1)

    # Check recipient-region too
    activity_stats = MockActivityStats(major_version)
    activity_stats.today = datetime.date(9990, 6, 1)
    activity_stats.element = etree.fromstring('''
        <iati-activity>
            <activity-status code="2"/>
            <transaction>
                <recipient-region/>
            </transaction>
        </iati-activity>
    ''')
    comprehensiveness = activity_stats.comprehensiveness()
    assert comprehensiveness['country_or_region'] == (0 if major_version == '1' else 1)

    # If is only at transaction level, but not for all transactions, we should get 0
    activity_stats = MockActivityStats(major_version)
    activity_stats.today = datetime.date(9990, 6, 1)
    activity_stats.element = etree.fromstring('''
        <iati-activity>
            <activity-status code="2"/>
            <transaction>
                <sector/>
                <recipient-country/>
                <recipient-region/>
            </transaction>
            <transaction></transaction>
        </iati-activity>
    ''')
    comprehensiveness = activity_stats.comprehensiveness()
    assert comprehensiveness['sector'] == 0
    assert comprehensiveness['country_or_region'] == 0


@pytest.mark.parametrize('major_version', ['1', '2'])
@pytest.mark.parametrize('key', ['sector', 'country_or_region'])
def test_comprehensiveness_with_validation_transaction_level_elements(key, major_version):
    activity_stats = MockActivityStats(major_version)
    activity_stats.today = datetime.date(2014, 1, 1)
    root = etree.fromstring('''
        <iati-activities>
            <iati-activity>
                <activity-status code="2"/>
                <sector/>
                <sector/>
                <recipient-country/>
                <recipient-country/>
            </iati-activity>
        </iati-activities>
    ''')
    activity_stats.element = root.find('iati-activity')
    activity_stats_valid = MockActivityStats(major_version)
    root_valid = etree.fromstring('''
        <iati-activities>
            <iati-activity>
                <activity-status code="2"/>
                <transaction>
                    <sector/>
                    <recipient-country/>
                </transaction>
            </iati-activity>
        </iati-activities>
    ''')
    activity_stats_valid.element = root_valid.find('iati-activity')
    comprehensiveness = activity_stats.comprehensiveness()
    not_valid = activity_stats.comprehensiveness_with_validation()
    valid = activity_stats_valid.comprehensiveness_with_validation()
    assert comprehensiveness[key] == 1
    assert not_valid[key] == 0
    assert valid[key] == (0 if major_version == '1' else 1)



## Denominator


@pytest.mark.parametrize('major_version', ['1', '2'])
def test_comprehensivness_denominator_default(major_version):
    activity_stats = MockActivityStats(major_version)
    activity_stats.today = datetime.date(9990, 6, 1)
    activity_stats._comprehensiveness_is_current = lambda: True
    assert activity_stats.comprehensiveness_denominator_default() == 1
    activity_stats = MockActivityStats(major_version)
    activity_stats.today = datetime.date(9990, 6, 1)
    activity_stats._comprehensiveness_is_current = lambda: False
    assert activity_stats.comprehensiveness_denominator_default() == 0


@pytest.mark.parametrize('major_version', ['1', '2'])
def test_comprehensivness_denominator_empty(major_version):
    activity_stats = MockActivityStats(major_version)
    activity_stats.today = datetime.date(9990, 6, 1)
    activity_stats.element = etree.fromstring('''
        <iati-activity>
        </iati-activity>
    ''')
    assert activity_stats.comprehensiveness_denominators() == {
        'recipient_language': 0,
        'transaction_spend': 0,
        'transaction_traceability': 0
    }


@pytest.mark.parametrize('major_version', ['1', '2'])
@pytest.mark.parametrize('key', [
    'transaction_spend', 'transaction_traceability' ])
def test_transaction_exclusions(key, major_version):
    activity_stats = MockActivityStats(major_version)
    activity_stats.today = datetime.date(9990, 6, 1)
    activity_stats.element = etree.fromstring('''
        <iati-activity>
            <activity-date type="start-planned" iso-date="9989-05-01" />
            <transaction>
                <transaction-type code="C"/>
            </transaction>
            <transaction>
                <transaction-type code="D"/>
            </transaction>
        </iati-activity>
    ''')
    assert activity_stats.comprehensiveness_denominators()[key] == 0

    # Broken activity-date/@iso-date
    activity_stats = MockActivityStats(major_version)
    activity_stats.today = datetime.date(9990, 6, 1)
    activity_stats.element = etree.fromstring('''
        <iati-activity>
            <activity-date type="start-planned" iso-date="" />
            <transaction>
                <transaction-type code="C"/>
            </transaction>
            <transaction>
                <transaction-type code="D"/>
            </transaction>
        </iati-activity>
    ''')
    assert activity_stats.comprehensiveness_denominators()[key] == 0


@pytest.mark.parametrize('major_version', ['1', '2'])
@pytest.mark.parametrize('key', [
    'transaction_spend', 'transaction_traceability' ])
def test_transaction_non_exclusions(key, major_version):
    activity_stats = MockActivityStats(major_version)
    activity_stats.today = datetime.date(9990, 6, 1)
    activity_stats.element = etree.fromstring('''
        <iati-activity>
            <activity-status code="2"/>
            <activity-date type="start-planned" iso-date="9989-01-01" />
            <transaction>
                <transaction-type code="IF"/>
            </transaction>
            <transaction>
                <transaction-type code="D"/>
            </transaction>
        </iati-activity>
    ''' if major_version == '1' else '''
        <iati-activity>
            <activity-status code="2"/>
            <activity-date type="1" iso-date="9989-01-01" />
            <transaction>
                <transaction-type code="1"/>
            </transaction>
            <transaction>
                <transaction-type code="3"/>
            </transaction>
        </iati-activity>
    ''')
    assert activity_stats.comprehensiveness_denominators()[key] == 1


@pytest.mark.parametrize('major_version', ['1', '2'])
def test_comprehensivness_denominator_recipient_language_true(major_version):
    activity_stats = MockActivityStats(major_version)
    activity_stats.today = datetime.date(9990, 6, 1)
    activity_stats.element = etree.fromstring('''
        <iati-activity>
            <activity-status code="2"/>
            <recipient-country />
        </iati-activity>
    ''')
    assert activity_stats.comprehensiveness_denominators()['recipient_language'] == 1


@pytest.mark.parametrize('major_version', ['1', '2'])
def test_comprehensivness_denominator_recipient_language_false(major_version):
    activity_stats = MockActivityStats(major_version)
    activity_stats.today = datetime.date(9990, 6, 1)
    activity_stats.element = etree.fromstring('''
        <iati-activity>
            <activity-status code="2"/>
            <recipient-country code="AF" percentage="50" />
            <recipient-country code="AG" percentage="50" />
        </iati-activity>
    ''')
    assert activity_stats.comprehensiveness_denominators()['recipient_language'] == 0


@pytest.mark.parametrize('major_version', ['2'])
def test_comprehensiveness_dac_sector_codes_v2(major_version):
    """Check that DAC sector codes in transactions in version 2 are also included."""
    activity_stats = MockActivityStats(major_version)
    activity_stats.today = datetime.date(9990, 6, 1)
    root = etree.fromstring('''
        <iati-activities version="2.01">
            <iati-activity xml:lang="en">
                <reporting-org ref="AA-AAA">
                    <narrative>Reporting ORG Name</narrative>
                </reporting-org>
                <iati-identifier>AA-AAA-1</iati-identifier>
                <participating-org/>
                <title>
                    <narrative>A title</narrative>
                </title>
                <description>
                    <narrative>A description</narrative>
                </description>
                <activity-status code="2"/>
                <activity-date type="2" iso-date="9989-05-01" />
                <recipient-country code="AI"/>
                <default-aid-type code="A01" />
                <transaction>
                    <transaction-type code="2"/><!-- Commitment -->
                    <sector vocabulary="1"/>
                    <value currency="" value-date="2014-01-01"/>
                </transaction>
                <transaction>
                    <transaction-type code="3"/><!-- Expenditure -->
                    <sector vocabulary="1"/>
                    <value currency="" value-date="2014-01-01"/>
                </transaction>
                <transaction>
                    <provider-org provider-activity-id="AAA"/>
                    <transaction-type code="1"/><!-- Incoming Funds -->
                    <sector vocabulary="1"/>
                    <value currency="" value-date="2014-01-01"/>
                </transaction>
                <budget/>
                <contact-info>
                    <email>test@example.org</email>
                </contact-info>
                <location>
                    <point srsName="http://www.opengis.net/def/crs/EPSG/0/4326">
                        <pos>31.616944 65.716944</pos>
                    </point>
                </location>
                <capital-spend percentage=""/>
                <document-link/>
                <document-link>
                    <!-- Activity website -->
                    <category code="A12" />
                </document-link>
                <conditions attached="0"/>
                <result>
                    <indicator/>
                </result>
            </iati-activity>
        </iati-activities>
    ''')
    activity_stats.element = root.find('iati-activity')
    assert all(type(x) == int for x in activity_stats.comprehensiveness().values())
    assert activity_stats.comprehensiveness() == {
        'version': 1,
        'reporting-org': 1,
        'iati-identifier': 1,
        'participating-org': 1,
        'title': 1,
        'description': 1,
        'activity-status': 1,
        'activity-date': 1,
        'sector': 1,
        'country_or_region': 1,
        'transaction_commitment': 1,
        'transaction_spend': 1,
        'transaction_currency': 1,
        'transaction_traceability': 1,
        'budget': 1,
        'budget_not_provided': 0,
        'contact-info': 1,
        'location': 1,
        'location_point_pos': 1,
        'sector_dac': 1,
        'capital-spend': 1,
        'document-link': 1,
        'activity-website': 1,
        'recipient_language': 1,
        'conditions_attached': 1,
        'result_indicator': 1,
        'aid_type': 1
    }

@pytest.mark.parametrize('major_version', ['2'])
def test_comprehensiveness_dac_sector_codes_v2_incomplete(major_version):
    """Check that DAC sector codes in transactions in version 2 return False when sector not included in every transaction."""
    activity_stats = MockActivityStats(major_version)
    activity_stats.today = datetime.date(9990, 6, 1)
    root = etree.fromstring('''
        <iati-activities version="2.01">
            <iati-activity xml:lang="en">
                <reporting-org ref="AA-AAA">
                    <narrative>Reporting ORG Name</narrative>
                </reporting-org>
                <iati-identifier>AA-AAA-1</iati-identifier>
                <participating-org/>
                <title>
                    <narrative>A title</narrative>
                </title>
                <description>
                    <narrative>A description</narrative>
                </description>
                <activity-status code="2"/>
                <activity-date type="2" iso-date="9989-05-01" />
                <recipient-country code="AI"/>
                <default-aid-type code="A01" />
                <transaction>
                    <transaction-type code="2"/><!-- Commitment -->
                    <sector vocabulary="1"/>
                    <value currency="" value-date="2014-01-01"/>
                </transaction>
                <transaction>
                    <transaction-type code="3"/><!-- Expenditure -->
                    <value currency="" value-date="2014-01-01"/>
                </transaction>
                <transaction>
                    <provider-org provider-activity-id="AAA"/>
                    <transaction-type code="1"/><!-- Incoming Funds -->
                    <sector vocabulary="1"/>
                    <value currency="" value-date="2014-01-01"/>
                </transaction>
                <budget/>
                <contact-info>
                    <email>test@example.org</email>
                </contact-info>
                <location>
                    <point srsName="http://www.opengis.net/def/crs/EPSG/0/4326">
                        <pos>31.616944 65.716944</pos>
                    </point>
                </location>
                <capital-spend percentage=""/>
                <document-link/>
                <document-link>
                    <!-- Activity website -->
                    <category code="A12" />
                </document-link>
                <conditions attached="0"/>
                <result>
                    <indicator/>
                </result>
            </iati-activity>
        </iati-activities>
    ''')
    activity_stats.element = root.find('iati-activity')
    assert all(type(x) == int for x in activity_stats.comprehensiveness().values())
    assert activity_stats.comprehensiveness() == {
        'version': 1,
        'reporting-org': 1,
        'iati-identifier': 1,
        'participating-org': 1,
        'title': 1,
        'description': 1,
        'activity-status': 1,
        'activity-date': 1,
        'sector': 0,
        'country_or_region': 1,
        'transaction_commitment': 1,
        'transaction_spend': 1,
        'transaction_currency': 1,
        'transaction_traceability': 1,
        'budget': 1,
        'budget_not_provided': 0,
        'contact-info': 1,
        'location': 1,
        'location_point_pos': 1,
        'sector_dac': 0,
        'capital-spend': 1,
        'document-link': 1,
        'activity-website': 1,
        'recipient_language': 1,
        'conditions_attached': 1,
        'result_indicator': 1,
        'aid_type': 1
    }


@pytest.mark.parametrize('major_version', ['1'])
def test_comprehensiveness_v1_returns_false(major_version):
    """Check that V1 activity returns false when no valid sector element entered at activity level."""
    activity_stats = MockActivityStats(major_version)
    activity_stats.today = datetime.date(9990, 6, 1)
    root = etree.fromstring('''
        <iati-activities version="1.05">
            <iati-activity xml:lang="en">
                <reporting-org ref="AA-AAA">Reporting ORG Name</reporting-org>
                <iati-identifier>AA-AAA-1</iati-identifier>
                <participating-org/>
                <title>A title</title>
                <description>A description</description>
                <activity-status code="2"/>
                <activity-date type="start-actual" iso-date="9989-05-01" />
                <recipient-country code="AI"/>
                <default-aid-type code="A01" />
                <transaction>
                    <transaction-type code="C"/>
                    <sector vocabulary="DAC"/>
                    <value currency="" value-date="2014-01-01"/>
                </transaction>
                <transaction>
                    <transaction-type code="E"/>
                    <sector vocabulary="DAC"/>
                    <value currency="" value-date="2014-01-01"/>
                </transaction>
                <transaction>
                    <provider-org provider-activity-id="AAA"/>
                    <sector vocabulary="DAC"/>
                    <transaction-type code="IF"/>
                    <value currency="" value-date="2014-01-01"/>
                </transaction>
                <budget/>
                <contact-info>
                    <email>test@example.org</email>
                </contact-info>
                <location>
                    <point srsName="http://www.opengis.net/def/crs/EPSG/0/4326">
                        <pos>31.616944 65.716944</pos>
                    </point>
                </location>
                <capital-spend percentage=""/>
                <document-link/>
                <activity-website/>
                <conditions attached="0"/>
                <result>
                    <indicator/>
                </result>
            </iati-activity>
        </iati-activities>
    ''')
    activity_stats.element = root.find('iati-activity')
    assert all(type(x) == int for x in activity_stats.comprehensiveness().values())
    assert activity_stats.comprehensiveness() == {
        'version': 1,
        'reporting-org': 1,
        'iati-identifier': 1,
        'participating-org': 1,
        'title': 1,
        'description': 1,
        'activity-status': 1,
        'activity-date': 1,
        'sector': 0,
        'country_or_region': 1,
        'transaction_commitment': 1,
        'transaction_spend': 1,
        'transaction_currency': 1,
        'transaction_traceability': 1,
        'budget': 1,
        'budget_not_provided': 0,
        'contact-info': 1,
        'location': 1,
        'location_point_pos': 1,
        'sector_dac': 0,
        'capital-spend': 1,
        'document-link': 1,
        'activity-website': 1,
        'recipient_language': 1,
        'conditions_attached': 1,
        'result_indicator': 1,
        'aid_type': 1
    }
