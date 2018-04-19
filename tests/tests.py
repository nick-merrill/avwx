import unittest
from avwx.models import MetarSet, WeatherStation, Wind, CloudLayerSet
import dateutil.parser
import datetime


class MetarTests(unittest.TestCase):

    def setUp(self):
        with open('mock_KBUF.xml', 'r') as f:
            self.mock_response = f.read()
        self.metar_set = MetarSet('KBUF,KAPA')
        self.metar_set.refresh(mock_response=self.mock_response)

    def test_explicit_station_string(self):
        self.assertEqual(self.metar_set.station_string, "KBUF,KAPA")

    def test_implicit_station_string(self):
        metar_set = MetarSet('wrong')
        metar_set.refresh(mock_response=self.mock_response)
        for metar in metar_set.report_set:
            self.assertEqual(metar.station.station_id, "KBUF")

    def test_get_latest(self):
        """
        Ensures algorithm is getting the Metar with the most recent timestamp.
        """
        latest_metar = self.metar_set.get_latest()
        expected_time = dateutil.parser.parse("2015-02-11T23:03:00Z")
        self.assertEqual(latest_metar.observation_time, expected_time)

    def _test_metar_attributes(self, metar):
        self.assertTrue(isinstance(metar.raw_text, str))
        self.assertTrue(isinstance(metar.flight_category, str))
        self.assertTrue(isinstance(metar.observation_time, datetime.datetime))
        self.assertTrue(isinstance(metar.station, WeatherStation))
        self.assertTrue(isinstance(metar.wind, Wind))
        self.assertTrue(isinstance(metar.cloud_layers, CloudLayerSet))
        # Floats
        for key in ['temp', 'dewpoint', 'visibility', 'altimeter']:
            val = getattr(metar, key)
            self.assertTrue(isinstance(val, float), "%s should be a float, not a %s" % (key, type(val)))

    def test_available_attributes(self):
        for metar in self.metar_set.report_set:
            self._test_metar_attributes(metar)


if __name__ == '__main__':
    unittest.main()
