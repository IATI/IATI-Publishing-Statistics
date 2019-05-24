from stats.dashboard import valid_coords, valid_date, valid_url, valid_value
from lxml import etree

def test_valid_coords():
    """
    Check that coordinates for a location on Earth are correctly detected as valid or not.

    Coordinates are located within an `iati-activity/location/point/pos`, though the validity function takes only the text.

    Note:
        The `(0, 0)` coordinate is permitted data against the IATI Standard, though is deemed invalid for Stats purposes since there is no reasonable reason an Activity would be undertaken there - it's in international waters in the ocean.
    """
    # empty values
    assert not valid_coords(etree.fromstring('<pos/>').text)
    assert not valid_coords(etree.fromstring('<pos />').text)
    assert not valid_coords(etree.fromstring('<pos></pos>').text)
    assert not valid_coords(etree.fromstring('<pos>  </pos>').text)
    # incorrect spacing
    assert not valid_coords(etree.fromstring('<pos> 1 2 </pos>').text)
    assert not valid_coords(etree.fromstring('<pos> 1 2</pos>').text)
    assert not valid_coords(etree.fromstring('<pos>1 2 </pos>').text)
    # invalid characters
    assert not valid_coords(etree.fromstring('<pos>a b</pos>').text)
    assert not valid_coords(etree.fromstring('<pos>one two</pos>').text)
    # incorrect number of values
    assert not valid_coords(etree.fromstring('<pos>1</pos>').text)
    assert not valid_coords(etree.fromstring('<pos>1 2 3</pos>').text)
    assert not valid_coords(etree.fromstring('<pos>1 2.3 4</pos>').text)
    # beyond boundary values
    assert not valid_coords(etree.fromstring('<pos>-90.00001 -180.00001</pos>').text)
    assert not valid_coords(etree.fromstring('<pos>-90.00001 180.00001</pos>').text)
    assert not valid_coords(etree.fromstring('<pos>90.00001 -180.00001</pos>').text)
    assert not valid_coords(etree.fromstring('<pos>90.00001 180.00001</pos>').text)
    # value deemed invalid for Stats purposes (though valid against the Standard)
    assert not valid_coords(etree.fromstring('<pos>0 0</pos>').text)

    # general permitted values
    assert valid_coords(etree.fromstring('<pos>1 2</pos>').text)
    assert valid_coords(etree.fromstring('<pos>1.2 2.3</pos>').text)
    assert valid_coords(etree.fromstring('<pos>1.23456789 2.34567890</pos>').text)
    assert valid_coords(etree.fromstring('<pos>-1.2 -2.3</pos>').text)
    assert valid_coords(etree.fromstring('<pos>-1.23456789 -2.34567890</pos>').text)
    # boundary values
    assert valid_coords(etree.fromstring('<pos>-90 -180</pos>').text)
    assert valid_coords(etree.fromstring('<pos>-90 180</pos>').text)
    assert valid_coords(etree.fromstring('<pos>90 -180</pos>').text)
    assert valid_coords(etree.fromstring('<pos>90 180</pos>').text)

def test_valid_date():
    assert not valid_date(etree.XML('<activity-date iso-date=""/>'))
    assert valid_date(etree.XML('<activity-date iso-date="2014-01-01"/>'))
    assert valid_date(etree.XML('<activity-date iso-date="2014-01-01" attribute="1">Some content<someelement/></activity-date>'))

    assert not valid_date(etree.XML('<transaction-date iso-date="2014-0101"/>'))
    assert valid_date(etree.XML('<transaction-date iso-date="2014-01-01"/>'))

    assert not valid_date(etree.XML('<value value-date="2014-0101"/>'))
    assert valid_date(etree.XML('<value value-date="2014-01-01"/>'))

    assert not valid_date(etree.XML('<period-start iso-date="2014-0101"/>'))
    assert valid_date(etree.XML('<period-start iso-date="2014-01-01"/>'))
    assert not valid_date(etree.XML('<period-end iso-date="2014-0101"/>'))
    assert valid_date(etree.XML('<period-end iso-date="2014-01-01"/>'))

    assert not valid_date(None)
    assert not valid_date(etree.XML('<otherelement/>'))


def test_valid_url():
    assert not valid_url(etree.XML('<document-link/>'))
    assert not valid_url(etree.XML('<document-link url=""/>'))
    assert not valid_url(etree.XML('<document-link url="http://:notaurl"/>'))
    assert not valid_url(etree.XML('<document-link url="notaurl"/>'))
    assert valid_url(etree.XML('<document-link url="http://example.org/"/>'))

    assert not valid_url(etree.XML('<activity-website/>'))
    assert not valid_url(etree.XML('<activity-website></activity-website>'))
    assert not valid_url(etree.XML('<activity-website>notaurl</activity-website>'))
    assert not valid_url(etree.XML('<activity-website>http://:notaurl</activity-website>'))
    assert valid_url(etree.XML('<document-link url="http://example.org/"/>'))


def test_valid_value():
    assert valid_value(etree.XML('<value>1.0</value>'))
    assert valid_value(etree.XML('<value someattribute="a">1.0</value>'))
    assert not valid_value(etree.XML('<value>1,0</value>'))
