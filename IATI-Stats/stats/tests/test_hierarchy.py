from lxml import etree

from stats.dashboard import ActivityStats, PublisherStats

def test_hierarchies():
    activity_stats = ActivityStats()
    activity_stats.element = etree.fromstring('''
        <iati-activity>
        </iati-activity>
    ''')
    assert activity_stats.hierarchies() == {None: 1}

    activity_stats = ActivityStats()
    activity_stats.element = etree.fromstring('''
        <iati-activity hierarchy="3">
        </iati-activity>
    ''')
    assert activity_stats.hierarchies() == {'3': 1}


def test_by_hierarchy():
    # Unlike the hierarchies dict, by_hierarchy should treat activities without
    # a hierarchy attribute as hierarchy 1
    activity_stats = ActivityStats()
    activity_stats.element = etree.fromstring('''
        <iati-activity>
        </iati-activity>
    ''')
    assert activity_stats.by_hierarchy().keys() == [ '1' ]

    activity_stats = ActivityStats()
    activity_stats.element = etree.fromstring('''
        <iati-activity hierarchy="3">
        </iati-activity>
    ''')
    assert activity_stats.by_hierarchy().keys() == [ '3' ]


def test_bottom_hierarchy():
    publisher_stats = PublisherStats()

    publisher_stats.aggregated = {
        'by_hierarchy': {
        }
    }
    assert publisher_stats.bottom_hierarchy() == {}

    publisher_stats.aggregated = {
        'by_hierarchy': {
            '1': { 'testkey': 'v1' },
            '2': { 'testkey': 'v2' },
            '3': { 'testkey': 'v3' }
        }
    }
    assert publisher_stats.bottom_hierarchy() == { 'testkey': 'v3' }


def test_bottom_hierarchy_non_integer():
    """ Hierachy values that are not integers should be ignored """

    publisher_stats = PublisherStats()

    publisher_stats.aggregated = {
        'by_hierarchy': {
            'notaninteger': { 'testkey': 'v_notaninteger' },
        }
    }
    assert publisher_stats.bottom_hierarchy() == {}

    publisher_stats.aggregated = {
        'by_hierarchy': {
            'notaninteger': { 'testkey': 'v_notaninteger' },
            '2': { 'testkey': 'v2' },
            '3': { 'testkey': 'v3' }
        }
    }
    assert publisher_stats.bottom_hierarchy() == { 'testkey': 'v3' }

