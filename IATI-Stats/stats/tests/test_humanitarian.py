# coding=utf-8
from lxml import etree
import pytest

from stats.dashboard import ActivityStats

class MockActivityStats(ActivityStats):
    def __init__(self, version):
        if len(version) == 1 or len(version.split('.')) < 2:
            self.major_version = version
            self.minor_version = '02'
        else:
            self.major_version = version.split('.')[0]
            self.minor_version = version.split('.')[1]
        return super(MockActivityStats, self).__init__()

    def _major_version(self):
        return self.major_version

    def _minor_version(self):
        return self.minor_version

    def _version(self):
        return self._major_version() + '.' + self._minor_version()

HUMANITARIAN_SECTOR_CODES_5_DIGITS = [72010, 72040, 72050, 73010, 74010, 74020]
HUMANITARIAN_SECTOR_CODES_3_DIGITS = [720, 730, 740]

@pytest.mark.parametrize('version', ['2.02', '2.03'])
@pytest.mark.parametrize('hum_attrib_val_true', ['1', 'true'])
@pytest.mark.parametrize('hum_attrib_val_false', ['0', 'false', 'True', 'False', ''])
@pytest.mark.parametrize('xml', ['''
        <!-- activity level true -->
        <iati-activity humanitarian="{0}">
        </iati-activity>
    ''', '''
        <!-- transaction level true -->
        <iati-activity>
            <transaction humanitarian="{0}" />
        </iati-activity>
    ''', '''
        <!-- activity level true, transaction false -->
        <iati-activity humanitarian="{0}">
            <transaction humanitarian="{1}" />
        </iati-activity>
    ''', '''
        <!-- activity and transaction level both true -->
        <iati-activity humanitarian="{0}">
            <transaction humanitarian="{0}" />
        </iati-activity>
    ''', '''
        <!-- transaction level both true and false -->
        <iati-activity>
            <transaction humanitarian="{0}" />
            <transaction humanitarian="{1}" />
        </iati-activity>
    '''])
def test_humanitarian_attrib_true(version, hum_attrib_val_true, hum_attrib_val_false, xml):
    """
    Detect an activity to be humanitarian using @humanitarian values that evaluate to true.
    """
    activity_stats = MockActivityStats(version)

    activity_stats.element = etree.fromstring(xml.format(hum_attrib_val_true, hum_attrib_val_false))
    assert activity_stats.humanitarian()['is_humanitarian'] == 1
    assert activity_stats.humanitarian()['is_humanitarian_by_attrib'] == 1
    assert activity_stats.humanitarian()['contains_humanitarian_scope'] == 0
    assert activity_stats.humanitarian()['uses_humanitarian_clusters_vocab'] == 0


@pytest.mark.parametrize('version', ['1.01', '1.02', '1.03', '1.04', '1.05', '2.01', 'unknown version'])
@pytest.mark.parametrize('hum_attrib_val_true', ['1', 'true'])
@pytest.mark.parametrize('hum_attrib_val_false', ['0', 'false', 'True', 'False', ''])
@pytest.mark.parametrize('xml', ['''
        <!-- activity level true -->
        <iati-activity humanitarian="{0}">
        </iati-activity>
    ''', '''
        <!-- transaction level true -->
        <iati-activity>
            <transaction humanitarian="{0}" />
        </iati-activity>
    ''', '''
        <!-- activity level true, transaction false -->
        <iati-activity humanitarian="{0}">
            <transaction humanitarian="{1}" />
        </iati-activity>
    ''', '''
        <!-- transaction level true, activity false -->
        <iati-activity humanitarian="{1}">
            <transaction humanitarian="{0}" />
        </iati-activity>
    ''', '''
        <!-- activity and transaction level both true -->
        <iati-activity humanitarian="{0}">
            <transaction humanitarian="{0}" />
        </iati-activity>
    ''', '''
        <!-- transaction level both true and false -->
        <iati-activity>
            <transaction humanitarian="{0}" />
            <transaction humanitarian="{1}" />
        </iati-activity>
    '''])
def test_humanitarian_attrib_true_invalid_version(version, hum_attrib_val_true, hum_attrib_val_false, xml):
    """
    Detect an activity to be humanitarian using @humanitarian values that evaluate to true, but at a version of the standard that does not support the attribute.
    """
    activity_stats = MockActivityStats(version)

    activity_stats.element = etree.fromstring(xml.format(hum_attrib_val_true, hum_attrib_val_false))
    assert activity_stats.humanitarian()['is_humanitarian'] == 0
    assert activity_stats.humanitarian()['is_humanitarian_by_attrib'] == 0
    assert activity_stats.humanitarian()['contains_humanitarian_scope'] == 0
    assert activity_stats.humanitarian()['uses_humanitarian_clusters_vocab'] == 0


@pytest.mark.parametrize('version', ['2.02', '2.03'])
@pytest.mark.parametrize('hum_attrib_val', ['0', 'false'])
@pytest.mark.parametrize('sector', HUMANITARIAN_SECTOR_CODES_5_DIGITS)
@pytest.mark.parametrize('xml', ['''
        <iati-activity humanitarian="{0}">
        </iati-activity>
    ''', '''
        <iati-activity>
            <transaction humanitarian="{0}" />
        </iati-activity>
    ''', '''
        <iati-activity humanitarian="{0}">
            <transaction humanitarian="{0}" />
        </iati-activity>
    ''', '''
        <iati-activity humanitarian="{0}">
            <sector code="{1}" />
        </iati-activity>
    ''', '''
        <iati-activity>
            <transaction humanitarian="{0}">
                <sector code="{1}" />
            </transaction>
        </iati-activity>
    ''', '''
        <iati-activity humanitarian="{0}">
            <transaction>
                <sector code="{1}" />
            </transaction>
        </iati-activity>
    ''', '''
        <!-- transaction level true, activity false -->
        <iati-activity humanitarian="{0}">
            <transaction humanitarian="true" />
        </iati-activity>
    '''])
def test_humanitarian_attrib_false(version, hum_attrib_val, sector, xml):
    """
    Detect an activity to not be humanitarian using @humanitarian values that evaluate to false.

    If there is a sector generally deemed to be humanitarian, the attribute shall take precedence.
    """
    activity_stats = MockActivityStats(version)

    activity_stats.element = etree.fromstring(xml.format(hum_attrib_val, sector))
    assert activity_stats.humanitarian()['is_humanitarian'] == 0
    assert activity_stats.humanitarian()['is_humanitarian_by_attrib'] == 0
    assert activity_stats.humanitarian()['contains_humanitarian_scope'] == 0
    assert activity_stats.humanitarian()['uses_humanitarian_clusters_vocab'] == 0


@pytest.mark.parametrize('version', ['2.02', '2.03'])
@pytest.mark.parametrize('hum_attrib_val', ['True', 'False', ''])
@pytest.mark.parametrize('sector', HUMANITARIAN_SECTOR_CODES_5_DIGITS)
@pytest.mark.parametrize('xml', ['''
        <iati-activity humanitarian="{0}">
            <sector code="{1}" />
        </iati-activity>
    ''', '''
        <iati-activity>
            <transaction humanitarian="{0}">
                <sector code="{1}" />
            </transaction>
        </iati-activity>
    ''', '''
        <iati-activity humanitarian="{0}">
            <transaction>
                <sector code="{1}" />
            </transaction>
        </iati-activity>
    '''])
def test_humanitarian_attrib_invalid_sector(version, hum_attrib_val, sector, xml):
    """
    Detect an activity to not be humanitarian using @humanitarian values that evaluate to false.

    If there is a sector generally deemed to be humanitarian, the attribute shall take precedence.
    """
    activity_stats = MockActivityStats(version)

    activity_stats.element = etree.fromstring(xml.format(hum_attrib_val, sector))
    assert activity_stats.humanitarian()['is_humanitarian'] == 1
    assert activity_stats.humanitarian()['is_humanitarian_by_attrib'] == 0
    assert activity_stats.humanitarian()['contains_humanitarian_scope'] == 0
    assert activity_stats.humanitarian()['uses_humanitarian_clusters_vocab'] == 0


@pytest.mark.parametrize('version', ['2.02', '2.03'])
@pytest.mark.parametrize('hum_attrib_val', ['True', 'False', ''])
@pytest.mark.parametrize('sector', HUMANITARIAN_SECTOR_CODES_5_DIGITS)
@pytest.mark.parametrize('xml', ['''
        <iati-activity humanitarian="{0}">
        </iati-activity>
    ''', '''
        <iati-activity>
            <transaction humanitarian="{0}" />
        </iati-activity>
    ''', '''
        <iati-activity humanitarian="{0}">
            <transaction humanitarian="{0}" />
        </iati-activity>
    '''])
def test_humanitarian_attrib_invalid_no_sector(version, hum_attrib_val, sector, xml):
    """
    Detect an activity to not be humanitarian using @humanitarian values that evaluate to false.

    If there is a sector generally deemed to be humanitarian, the attribute shall take precedence.
    """
    activity_stats = MockActivityStats(version)

    activity_stats.element = etree.fromstring(xml.format(hum_attrib_val, sector))
    assert activity_stats.humanitarian()['is_humanitarian'] == 0
    assert activity_stats.humanitarian()['is_humanitarian_by_attrib'] == 0
    assert activity_stats.humanitarian()['contains_humanitarian_scope'] == 0
    assert activity_stats.humanitarian()['uses_humanitarian_clusters_vocab'] == 0


@pytest.mark.parametrize('major_version', ['1', '2'])
@pytest.mark.parametrize('sector', HUMANITARIAN_SECTOR_CODES_5_DIGITS)
@pytest.mark.parametrize('xml', ['''
        <!-- activity level sector, assumed vocab -->
        <iati-activity>
        	<sector code="{0}" />
        </iati-activity>
    ''', '''
        <!-- activity level sector, explicit vocab -->
        <iati-activity>
        	<sector code="{0}" vocabulary="{1}" />
        </iati-activity>
    ''', '''
        <!-- both activity and transaction level sector -->
        <iati-activity>
            <sector code="{0}" />
            <transaction>
                <sector code="{0}" vocabulary="{1}" />
            </transaction>
        </iati-activity>
    '''])
def test_humanitarian_sector_true(major_version, sector, xml):
    """
    Detects an activity to be humanitarian using sector codes considered to relate to humanitarian.

    Also checks that the appropriate vocabulary is provided or assumed.
    """
    activity_stats = MockActivityStats(major_version)

    activity_stats.element = etree.fromstring(xml.format(sector, activity_stats._dac_5_code()))
    assert activity_stats.humanitarian()['is_humanitarian'] == 1
    assert activity_stats.humanitarian()['is_humanitarian_by_attrib'] == 0
    assert activity_stats.humanitarian()['contains_humanitarian_scope'] == 0
    assert activity_stats.humanitarian()['uses_humanitarian_clusters_vocab'] == 0


@pytest.mark.parametrize('major_version', ['1', '2'])
@pytest.mark.parametrize('sector', HUMANITARIAN_SECTOR_CODES_3_DIGITS)
@pytest.mark.parametrize('xml', ['''
        <iati-activity>
            <sector code="{0}" vocabulary="{1}" />
        </iati-activity>
    '''])
def test_humanitarian_sector_true_3_digit(major_version, sector, xml):
    """
    Detects an activity to be humanitarian using 3-digit sector codes considered to relate to humanitarian.

    Also checks that the appropriate vocabulary is provided or assumed.
    """
    activity_stats = MockActivityStats(major_version)

    activity_stats.element = etree.fromstring(xml.format(sector, activity_stats._dac_3_code()))
    assert activity_stats.humanitarian()['is_humanitarian'] == 1
    assert activity_stats.humanitarian()['is_humanitarian_by_attrib'] == 0
    assert activity_stats.humanitarian()['contains_humanitarian_scope'] == 0
    assert activity_stats.humanitarian()['uses_humanitarian_clusters_vocab'] == 0


@pytest.mark.parametrize('version', ['2.01', '2.02', '2.03'])
@pytest.mark.parametrize('hum_sector', HUMANITARIAN_SECTOR_CODES_5_DIGITS)
@pytest.mark.parametrize('not_hum_sector', [-89, 'not_a_code', HUMANITARIAN_SECTOR_CODES_5_DIGITS[0]+1, HUMANITARIAN_SECTOR_CODES_3_DIGITS[0]+1, HUMANITARIAN_SECTOR_CODES_5_DIGITS[-1]-1, HUMANITARIAN_SECTOR_CODES_3_DIGITS[-1]-1])
@pytest.mark.parametrize('xml', ['''
        <!-- transaction level sector, assumed vocab -->
        <iati-activity>
            <transaction>
                <sector code="{0}" />
            </transaction>
        </iati-activity>
    ''', '''
        <!-- transaction level sector, explicit vocab -->
        <iati-activity>
            <transaction>
                <sector code="{0}" vocabulary="{1}" />
            </transaction>
        </iati-activity>
    ''', '''
        <!-- both activity and transaction level sector -->
        <iati-activity>
            <sector code="{0}" />
            <transaction>
                <sector code="{0}" vocabulary="{1}" />
            </transaction>
        </iati-activity>
    ''', '''
        <!-- both activity and transaction level sector, hum at transaction level -->
        <iati-activity>
            <sector code="{0}" />
            <transaction>
                <sector code="{2}" vocabulary="{1}" />
            </transaction>
        </iati-activity>
    ''', '''
        <!-- both activity and transaction level sector, hum at activity level -->
        <iati-activity>
            <sector code="{2}" />
            <transaction>
                <sector code="{0}" vocabulary="{1}" />
            </transaction>
        </iati-activity>
    ''', '''
        <!-- activity level sector, not hum attribute -->
        <iati-activity>
            <sector code="{0}" />
            <transaction humanitarian="0" />
        </iati-activity>
    '''])
def test_humanitarian_sector_true_transaction(version, hum_sector, not_hum_sector, xml):
    """
    Detects an activity to be humanitarian using sector codes at transaction level considered to relate to humanitarian.

    Also checks that the appropriate vocabulary is provided or assumed.
    """
    activity_stats = MockActivityStats(version)

    activity_stats.element = etree.fromstring(xml.format(hum_sector, activity_stats._dac_5_code(), not_hum_sector))
    assert activity_stats.humanitarian()['is_humanitarian'] == 1
    assert activity_stats.humanitarian()['is_humanitarian_by_attrib'] == 0
    assert activity_stats.humanitarian()['contains_humanitarian_scope'] == 0
    assert activity_stats.humanitarian()['uses_humanitarian_clusters_vocab'] == 0


@pytest.mark.parametrize('version', ['1.01', '1.02', '1.03', '1.04', '1.05', 'unknown version'])
@pytest.mark.parametrize('sector', HUMANITARIAN_SECTOR_CODES_5_DIGITS)
@pytest.mark.parametrize('xml', ['''
        <!-- transaction level sector, assumed vocab -->
        <iati-activity>
            <transaction>
                <sector code="{0}" />
            </transaction>
        </iati-activity>
    ''', '''
        <!-- transaction level sector, explicit vocab -->
        <iati-activity>
            <transaction>
                <sector code="{0}" vocabulary="{1}" />
            </transaction>
        </iati-activity>
    '''])
def test_humanitarian_sector_true_transaction_invalid_version(version, sector, xml):
    """
    Detects an activity to be not humanitarian due to an invalid version despite correctly formed transactions.
    """
    activity_stats = MockActivityStats(version)

    activity_stats.element = etree.fromstring(xml.format(sector, activity_stats._dac_5_code()))
    assert activity_stats.humanitarian()['is_humanitarian'] == 0
    assert activity_stats.humanitarian()['is_humanitarian_by_attrib'] == 0
    assert activity_stats.humanitarian()['contains_humanitarian_scope'] == 0
    assert activity_stats.humanitarian()['uses_humanitarian_clusters_vocab'] == 0


@pytest.mark.parametrize('major_version', ['1', '2'])
@pytest.mark.parametrize('sector', [-89, 'not_a_code', HUMANITARIAN_SECTOR_CODES_5_DIGITS[0]+1, HUMANITARIAN_SECTOR_CODES_3_DIGITS[0]+1, HUMANITARIAN_SECTOR_CODES_5_DIGITS[-1]-1, HUMANITARIAN_SECTOR_CODES_3_DIGITS[-1]-1])
@pytest.mark.parametrize('xml', ['''
        <iati-activity>
            <sector code="{0}" />
        </iati-activity>
    '''])
def test_humanitarian_sector_false_bad_codes(major_version, sector, xml):
    """
    Detects an activity not to be humanitarian using sector codes that are not considered to relate to humanitarian.
    """
    activity_stats = MockActivityStats(major_version)

    activity_stats.element = etree.fromstring(xml.format(sector))
    assert activity_stats.humanitarian()['is_humanitarian'] == 0
    assert activity_stats.humanitarian()['is_humanitarian_by_attrib'] == 0
    assert activity_stats.humanitarian()['contains_humanitarian_scope'] == 0
    assert activity_stats.humanitarian()['uses_humanitarian_clusters_vocab'] == 0


@pytest.mark.parametrize('major_version', ['1', '2'])
@pytest.mark.parametrize('sector', HUMANITARIAN_SECTOR_CODES_5_DIGITS)
@pytest.mark.parametrize('vocab', [2, 99, 'DAC-3'])
@pytest.mark.parametrize('xml', ['''
        <iati-activity>
            <sector code="{0}" vocabulary="{1}" />
        </iati-activity>
    '''])
def test_humanitarian_sector_false_bad_vocab(major_version, sector, vocab, xml):
    """
    Detects an activity not to be humanitarian due to specification of an incorrect vocabulary despite @code values that are considered to relate to humanitarian by default.
    """
    activity_stats = MockActivityStats(major_version)

    activity_stats.element = etree.fromstring(xml.format(sector, vocab))
    assert activity_stats.humanitarian()['is_humanitarian'] == 0
    assert activity_stats.humanitarian()['is_humanitarian_by_attrib'] == 0
    assert activity_stats.humanitarian()['contains_humanitarian_scope'] == 0
    assert activity_stats.humanitarian()['uses_humanitarian_clusters_vocab'] == 0


@pytest.mark.parametrize('major_version', ['1', '2'])
@pytest.mark.parametrize('sector', HUMANITARIAN_SECTOR_CODES_3_DIGITS)
@pytest.mark.parametrize('vocab', [1, 99, 'DAC'])
@pytest.mark.parametrize('xml', ['''
        <iati-activity>
            <sector code="{0}" vocabulary="{1}" />
        </iati-activity>
    '''])
def test_humanitarian_sector_false_bad_vocab_3_digit(major_version, sector, vocab, xml):
    """
    Detects an activity not to be humanitarian due to specification of an incorrect vocabulary despite 3-digit @code values that are considered to relate to humanitarian by default.
    """
    activity_stats = MockActivityStats(major_version)

    activity_stats.element = etree.fromstring(xml.format(sector, vocab))
    assert activity_stats.humanitarian()['is_humanitarian'] == 0
    assert activity_stats.humanitarian()['is_humanitarian_by_attrib'] == 0
    assert activity_stats.humanitarian()['contains_humanitarian_scope'] == 0
    assert activity_stats.humanitarian()['uses_humanitarian_clusters_vocab'] == 0


@pytest.mark.parametrize('sector', HUMANITARIAN_SECTOR_CODES_3_DIGITS + HUMANITARIAN_SECTOR_CODES_5_DIGITS)
@pytest.mark.parametrize('vocab', ['1', '2', ''])
@pytest.mark.parametrize('xml', ['''
        <iati-activity>
            <sector code="{0}" vocabulary="{1}" />
        </iati-activity>
    '''])
def test_humanitarian_sector_false_bad_major_version_1(sector, vocab, xml, major_version='1'):
    """
    Detects an activity not to be humanitarian due to specification of a vocabulary that is valid at an alternative major version of the Standard.
    """
    activity_stats = MockActivityStats(major_version)

    activity_stats.element = etree.fromstring(xml.format(sector, vocab))
    assert activity_stats.humanitarian()['is_humanitarian'] == 0
    assert activity_stats.humanitarian()['is_humanitarian_by_attrib'] == 0
    assert activity_stats.humanitarian()['contains_humanitarian_scope'] == 0
    assert activity_stats.humanitarian()['uses_humanitarian_clusters_vocab'] == 0


@pytest.mark.parametrize('sector', HUMANITARIAN_SECTOR_CODES_3_DIGITS + HUMANITARIAN_SECTOR_CODES_5_DIGITS)
@pytest.mark.parametrize('vocab', ['DAC', 'DAC-3', ''])
@pytest.mark.parametrize('xml', ['''
        <iati-activity>
            <sector code="{0}" vocabulary="{1}" />
        </iati-activity>
    ''', '''
        <!-- transaction level sector - valid at V2, but not V1 -->
        <iati-activity>
            <transaction>
                <sector code="{0}" vocabulary="{1}" />
            </transaction>
        </iati-activity>
    '''])
def test_humanitarian_sector_false_bad_major_version_2(sector, vocab, xml, major_version='2'):
    """
    Detects an activity not to be humanitarian due to specification of a vocabulary that is valid at an alternative major version of the Standard.
    """
    activity_stats = MockActivityStats(major_version)

    activity_stats.element = etree.fromstring(xml.format(sector, vocab))
    assert activity_stats.humanitarian()['is_humanitarian'] == 0
    assert activity_stats.humanitarian()['is_humanitarian_by_attrib'] == 0
    assert activity_stats.humanitarian()['contains_humanitarian_scope'] == 0
    assert activity_stats.humanitarian()['uses_humanitarian_clusters_vocab'] == 0


@pytest.mark.parametrize('major_version', ['2'])
@pytest.mark.parametrize('sector', HUMANITARIAN_SECTOR_CODES_5_DIGITS + [89, 'not_a_code'])
@pytest.mark.parametrize('hum_attrib_val', ['1', 'true'])
def test_humanitarian_attrib_true_sector_anything(major_version, sector, hum_attrib_val):
    """
    Detect an activity to be humanitarian using @humanitarian values that evaluate to true in combination with sector codes.

    Both valid and invalid sector codes are tested because everything should still evaluate the same, given that @humanitarian is true.
    """
    activity_stats = MockActivityStats(major_version)

    activity_stats.element = etree.fromstring('''
        <iati-activity humanitarian="{0}">
        	<sector code="{1}" />
        </iati-activity>
    '''.format(hum_attrib_val, sector))
    assert activity_stats.humanitarian()['is_humanitarian'] == 1
    assert activity_stats.humanitarian()['is_humanitarian_by_attrib'] == 1
    assert activity_stats.humanitarian()['contains_humanitarian_scope'] == 0
    assert activity_stats.humanitarian()['uses_humanitarian_clusters_vocab'] == 0


@pytest.mark.parametrize('version', ['2.02', '2.03'])
@pytest.mark.parametrize('sector', [-89, 'not_a_code'])
@pytest.mark.parametrize('hum_attrib_val', ['0', 'false', 'True', 'False', ''])
def test_humanitarian_attrib_false_sector_false(version, sector, hum_attrib_val):
    """
    Detect an activity not to be humanitarian using sector codes that are deemed not to be humanitarian, in combination with a @humanitarian value which evaluates to false.
    """
    activity_stats = MockActivityStats(version)

    activity_stats.element = etree.fromstring('''
        <iati-activity humanitarian="{0}">
        	<sector code="{1}" />
        </iati-activity>
    '''.format(hum_attrib_val, sector))
    assert activity_stats.humanitarian()['is_humanitarian'] == 0
    assert activity_stats.humanitarian()['is_humanitarian_by_attrib'] == 0
    assert activity_stats.humanitarian()['contains_humanitarian_scope'] == 0
    assert activity_stats.humanitarian()['uses_humanitarian_clusters_vocab'] == 0


@pytest.mark.parametrize('version', ['1.01', '1.02', '1.03', '1.04', '1.05', '2.01', 'unknown version'])
@pytest.mark.parametrize('hum_attrib_val_true', ['1', 'true'])
@pytest.mark.parametrize('hum_attrib_val_false', ['0', 'false', 'True', 'False', ''])
@pytest.mark.parametrize('xml', ['''
        <iati-activity humanitarian="{0}">
        </iati-activity>
    ''', '''
        <iati-activity>
            <transaction humanitarian="{0}" />
        </iati-activity>
    ''', '''
        <iati-activity humanitarian="{0}">
            <transaction humanitarian="{1}" />
        </iati-activity>
    ''', '''
        <iati-activity humanitarian="{1}">
            <transaction humanitarian="{0}" />
        </iati-activity>
    '''])
def test_humanitarian_attrib_false_sector_false(version, hum_attrib_val_true, hum_attrib_val_false, xml):
    """
    Detect an activity not to be humanitarian at versions of the standard not expecting @humanitarian when a @humanitarian value that evaluates to true is present.
    """
    activity_stats = MockActivityStats(version)

    activity_stats.element = etree.fromstring(xml.format(hum_attrib_val_true, hum_attrib_val_false))
    assert activity_stats.humanitarian()['is_humanitarian'] == 0
    assert activity_stats.humanitarian()['is_humanitarian_by_attrib'] == 0
    assert activity_stats.humanitarian()['contains_humanitarian_scope'] == 0
    assert activity_stats.humanitarian()['uses_humanitarian_clusters_vocab'] == 0


@pytest.mark.parametrize('version', ['2.02', '2.03'])
@pytest.mark.parametrize('hum_attrib_val', ['1', 'true'])
def test_humanitarian_elements_valid_version(version, hum_attrib_val):
    """
    Detect that an activity containing a humanitarian-scope element (with required non-empty attributes) counts as humanitarian.
    """

    activity_stats = MockActivityStats(version)

    activity_stats.element = etree.fromstring('''
       <iati-activity humanitarian="{0}">
          <humanitarian-scope type="xx" code="xx" />
       </iati-activity>
    '''.format(hum_attrib_val))

    assert activity_stats.humanitarian()['is_humanitarian'] == 1
    assert activity_stats.humanitarian()['is_humanitarian_by_attrib'] == 1
    assert activity_stats.humanitarian()['contains_humanitarian_scope'] == 1
    assert activity_stats.humanitarian()['uses_humanitarian_clusters_vocab'] == 0


@pytest.mark.parametrize('version', ['1.01', '1.02', '1.03', '1.04', '1.05', '2.01', 'unknown version'])
@pytest.mark.parametrize('hum_attrib_val', ['1', 'true'])
def test_humanitarian_elements_invalid_version(version, hum_attrib_val):
    """
    Tests that humanitarian elements are detected at supported versions.
    """

    activity_stats = MockActivityStats(version)

    activity_stats.element = etree.fromstring('''
       <iati-activity humanitarian="{1}">
          <humanitarian-scope type="xx" code="xx" />
       </iati-activity>
    '''.format(version, hum_attrib_val))

    assert activity_stats.humanitarian()['is_humanitarian'] == 0
    assert activity_stats.humanitarian()['is_humanitarian_by_attrib'] == 0
    assert activity_stats.humanitarian()['contains_humanitarian_scope'] == 0
    assert activity_stats.humanitarian()['uses_humanitarian_clusters_vocab'] == 0


@pytest.mark.parametrize('version', ['2.02', '2.03'])
@pytest.mark.parametrize('hum_attrib_val', ['1', 'true'])
def test_humanitarian_scope_invalid(version, hum_attrib_val):
    """
    Detect that even if an activity (at an expected version) contains a humanitarian-scope element, it must include the required attributes to count as humanitarian.
    """
    activity_stats = MockActivityStats(version)

    activity_stats.element = etree.fromstring('''
        <iati-activity humanitarian="{0}">
           <humanitarian-scope />
        </iati-activity>
    '''.format(hum_attrib_val))
    assert activity_stats.humanitarian()['is_humanitarian'] == 1
    assert activity_stats.humanitarian()['contains_humanitarian_scope'] == 0


@pytest.mark.parametrize('version', ['2.02', '2.03'])
@pytest.mark.parametrize('hum_attrib_val', ['1', 'true'])
def test_humanitarian_scope_invalid_empty_values(version, hum_attrib_val):
    """
    Detect that even if the humanitarian-scope (at an expected version) element is present (with required attributes), there must be non-empty data within the @type and @code attributes for it to count as humanitarian.
    """
    activity_stats = MockActivityStats(version)

    activity_stats.element = etree.fromstring('''
        <iati-activity humanitarian="{0}">
           <humanitarian-scope type="" code="" />
        </iati-activity>
    '''.format(hum_attrib_val))
    assert activity_stats.humanitarian()['is_humanitarian'] == 1
    assert activity_stats.humanitarian()['contains_humanitarian_scope'] == 0


@pytest.mark.parametrize('version', ['1.01', '1.02', '1.03', '1.04', '1.05', '2.01', '2.02', '2.03', 'unknown version'])
def test_humanitarian_scope_but_not_humanitarian_no_attrib(version):
    """
    Detect that even if an activity (of any version) contains the humanitarian-scope element, the humanitarian attribute must be present and marked as true to count.
    """

    activity_stats = MockActivityStats(version)

    activity_stats.element = etree.fromstring('''
       <iati-activity>
          <humanitarian-scope type="xx" code="xx" />
       </iati-activity>
    ''')

    assert activity_stats.humanitarian()['is_humanitarian'] == 0
    assert activity_stats.humanitarian()['is_humanitarian_by_attrib'] == 0
    assert activity_stats.humanitarian()['contains_humanitarian_scope'] == 0
    assert activity_stats.humanitarian()['uses_humanitarian_clusters_vocab'] == 0


@pytest.mark.parametrize('version', ['1.01', '1.02', '1.03', '1.04', '1.05', '2.01', '2.02', '2.03', 'unknown version'])
@pytest.mark.parametrize('hum_attrib_val_false', ['0', 'false', 'True', 'False', ''])
def test_humanitarian_scope_but_humanitarian_is_false(version, hum_attrib_val_false):
    """
    Detect that even if an activity (at any version) contains a humanitarian-scope element, the humanitarian attribute must be present and marked as true to count.
    """

    activity_stats = MockActivityStats(version)

    activity_stats.element = etree.fromstring('''
       <iati-activity humanitarian="{0}">
          <humanitarian-scope type="xx" code="xx" />
       </iati-activity>
    '''.format(hum_attrib_val_false))

    assert activity_stats.humanitarian()['is_humanitarian'] == 0
    assert activity_stats.humanitarian()['is_humanitarian_by_attrib'] == 0
    assert activity_stats.humanitarian()['contains_humanitarian_scope'] == 0
    assert activity_stats.humanitarian()['uses_humanitarian_clusters_vocab'] == 0


@pytest.mark.parametrize('version', ['2.02', '2.03'])
@pytest.mark.parametrize('hum_attrib_val', ['1', 'true'])
def test_humanitarian_clusters_valid(version, hum_attrib_val):
    """
    Detect that an activity contains a sector defined by the 'Humanitarian Global Clusters' sector vocabulary.
    """
    activity_stats = MockActivityStats(version)

    activity_stats.element = etree.fromstring('''
        <iati-activity humanitarian="{0}">
           <sector vocabulary="10" />
        </iati-activity>
    '''.format(hum_attrib_val))
    assert activity_stats.humanitarian()['is_humanitarian'] == 1
    assert activity_stats.humanitarian()['uses_humanitarian_clusters_vocab'] == 1


@pytest.mark.parametrize('version', ['2.02', '2.03'])
def test_humanitarian_clusters_invalid_no_attrib(version):
    """
    Detect that even if an activity contains a sector defined by the 'Humanitarian Global Clusters' sector vocabulary, the humanitarian attribute must be present and marked as true to count.
    """
    activity_stats = MockActivityStats(version)

    activity_stats.element = etree.fromstring('''
        <iati-activity>
           <sector vocabulary="10" />
        </iati-activity>
    ''')
    assert activity_stats.humanitarian()['is_humanitarian'] == 0
    assert activity_stats.humanitarian()['uses_humanitarian_clusters_vocab'] == 0


@pytest.mark.parametrize('version', ['2.02', '2.03'])
@pytest.mark.parametrize('hum_attrib_val_false', ['0', 'false', 'True', 'False', ''])
def test_humanitarian_clusters_invalid_humanitarian_is_false(version, hum_attrib_val_false):
    """
    Detect that even if an activity contains a sector defined by the 'Humanitarian Global Clusters' sector vocabulary, the humanitarian attribute must be present and marked as true to count.
    """
    activity_stats = MockActivityStats(version)

    activity_stats.element = etree.fromstring('''
        <iati-activity humanitarian="{0}">
           <sector vocabulary="10" />
        </iati-activity>
    '''.format(hum_attrib_val_false))
    assert activity_stats.humanitarian()['is_humanitarian'] == 0
    assert activity_stats.humanitarian()['uses_humanitarian_clusters_vocab'] == 0


@pytest.mark.parametrize('version', ['1.01', '1.02', '1.03', '1.04', '1.05', '2.01', 'unknown version'])
@pytest.mark.parametrize('hum_attrib_val', ['1', 'true'])
def test_humanitarian_clusters_version_1(version, hum_attrib_val):
    """
    Detect that a pre-2.02 activity containing a sector defined by the 'Humanitarian Global Clusters' sector vocabulary is not detected.
    """
    activity_stats = MockActivityStats(version)

    activity_stats.element = etree.fromstring('''
        <iati-activity humanitarian="{0}">
           <sector vocabulary="10" />
        </iati-activity>
    '''.format(hum_attrib_val))
    assert activity_stats.humanitarian()['is_humanitarian'] == 0
    assert activity_stats.humanitarian()['uses_humanitarian_clusters_vocab'] == 0


@pytest.mark.parametrize('version', ['1.01', '1.02', '1.03', '1.04', '1.05', '2.01', '2.02', '2.03', 'unknown version'])
@pytest.mark.parametrize('hum_attrib_val', ['1', 'true'])
@pytest.mark.parametrize('sector_vocabulary_code', ['', '1', 'internal vocabulary'])
def test_humanitarian_clusters_invalid(version, hum_attrib_val,
                                       sector_vocabulary_code):
    """
    Detect that an activity does not contain a sector defined by the 'Humanitarian Global Clusters' sector vocabulary.
    """
    activity_stats = MockActivityStats(version)

    activity_stats.element = etree.fromstring('''
        <iati-activity humanitarian="{0}">
           <sector vocabulary="{1}" />
        </iati-activity>
    '''.format(hum_attrib_val, sector_vocabulary_code))
    assert activity_stats.humanitarian()['uses_humanitarian_clusters_vocab'] == 0
