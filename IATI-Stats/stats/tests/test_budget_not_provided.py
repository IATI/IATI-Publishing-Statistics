from lxml import etree

from stats.dashboard import ActivityStats

class MockActivityStats(ActivityStats):
    def __init__(self, major_version='2'):
        self.major_version = major_version
        return super(MockActivityStats, self).__init__()

    def _major_version(self):
        return self.major_version

def test_budget_not_provided_works():
    activity_stats = MockActivityStats()
    activity_stats.element = etree.fromstring('''
            <iati-activity budget-not-provided="1">
            </iati-activity>
    ''')
    assert activity_stats._budget_not_provided() == 1


def test_budget_not_provided_fails():
    activity_stats = MockActivityStats()
    activity_stats.element = etree.fromstring('''
            <iati-activity>
            </iati-activity>
    ''')
    assert activity_stats._budget_not_provided() is None


def test_budget_validation_bools():
    activity_stats = MockActivityStats()
    activity_stats.element = etree.fromstring('''
            <iati-activity budget-not-provided="3">
            </iati-activity>
    ''')
    assert (len(activity_stats.element.findall('budget')) == 0)
