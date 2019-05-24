"""
Unit tests to be run on the data produced.

Note: this file is not up to date, and will fail.

"""
from __future__ import unicode_literals
import unittest
import os
import json
import decimal

OUTPUT_DIR = 'out'

class TestAggregatedValues(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(OUTPUT_DIR, 'aggregated.json')) as fp:
            self.aggregated = json.load(fp, parse_float=decimal.Decimal)

    def test_activity_sum(self):
        a = self.aggregated
        for key in ['activities_per_year']:
            self.assertEqual(a['activities'], sum(a[key].values()), msg=key)

    def test_spend_sum(self):
        a = self.aggregated
        for key in ['spend_per_year', 'spend_per_country']:
            self.assertAlmostEqual(a['spend'], sum(a[key].values()), places=2)

    def test_activities_upper_bound(self):
        a = self.aggregated
        for key in ['activities_per_country', 'activities_per_year']:
            for value in a[key].values():
                self.assertLessEqual(value, a['activities'], msg='{0} {1}'.format(key,value))

    def test_publishers_upper_bound(self):
        a = self.aggregated
        for key in ['publishers_per_country']:
            for value in a[key].values():
                self.assertLessEqual(value, a['publishers'], msg='{0} {1}'.format(key,value))
        

if __name__ == '__main__':
    unittest.main()
