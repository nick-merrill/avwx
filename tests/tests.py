import unittest
from avwx.models import MetarSet


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


if __name__ == '__main__':
    unittest.main()
