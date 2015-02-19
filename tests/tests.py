import unittest
from avwx.models import MetarSet
import dateutil.parser
import datetime


class MetarTests(unittest.TestCase):

    def setUp(self):
        with open('tests/mock_KBUF.xml', 'rU') as f:
            self.mock_response = f.read()
        self.metar_set = MetarSet('KBUF')
        self.metar_set.refresh(mock_response=self.mock_response)

    def test_explicit_station_string(self):
        self.assertEqual(self.metar_set.station_string, "KBUF")

    def test_implicit_station_string(self):
        metar_set = MetarSet('wrong')
        metar_set.refresh(mock_response=self.mock_response)
        self.assertEqual(metar_set.station_string, "KBUF")

    def test_get_latest(self):
        latest_metar = self.metar_set.get_latest()
        expected_time = dateutil.parser.parse("2015-02-11T23:03:00Z")
        self.assertEqual(latest_metar.observation_time, expected_time)

    def test_available_attributes(self):
        metar = self.metar_set.report_set.pop()
        self.assertTrue(isinstance(metar.observation_time, datetime.datetime))


if __name__ == '__main__':
    unittest.main()
