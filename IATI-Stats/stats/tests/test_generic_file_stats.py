# coding=utf-8

from lxml import etree
import pytest

from stats.dashboard import ActivityStats


@pytest.mark.parametrize('version', ['1.01', '1.02', '1.03', '1.04', '1.05', '2.01', '2.02', '2.03'])
def test_version_detection_valid(version):
    """
    Tests that valid versions of the IATI Standard are detected.
    """

    activity = ActivityStats()

    tree = etree.fromstring('''
        <iati-activities version="{0}">
           <iati-activity>
           </iati-activity>
        </iati-activities>
    '''.format(version))

    activity.element = tree.getchildren()[0]

    assert activity._version() == version


@pytest.mark.parametrize('version', ['1.06', '2.04', '3.01', '1', '', 'version 1.03', '1.03 version', '1.03 or 1.04', ' 2.01', '2 .01'])
def test_version_detection_invalid(version):
    """
    Tests that invalid versions of the IATI Standard are detected.
    """

    activity = ActivityStats()

    tree = etree.fromstring('''
        <iati-activities version="{0}">
           <iati-activity>
           </iati-activity>
        </iati-activities>
    '''.format(version))

    activity.element = tree.getchildren()[0]

    assert activity._version() == '1.01'


def test_version_detection_no_parent():
    """
    Tests that XML with no parent returns default version.
    """

    activity = ActivityStats()

    activity.element = etree.fromstring('''
        <iati-activity>
        </iati-activity>
    ''')

    assert activity._version() == '1.01'


def test_version_detection_no_version_attrib():
    """
    Tests that XML with no version attribute returns default version.
    """

    activity = ActivityStats()

    tree = etree.fromstring('''
        <iati-activities>
           <iati-activity>
           </iati-activity>
        </iati-activities>
    ''')

    activity.element = tree.getchildren()[0]

    assert activity._version() == '1.01'
