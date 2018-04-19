from urllib.request import urlopen
from xml.etree import ElementTree
import datetime
import dateutil.parser
import re

BASE_URL = "https://aviationweather.gov/adds/dataserver_current/httpparam"


class AbstractMethodError(Exception):
    def __init__(self, message=""):
        Exception(message)


def _format(value):
    if isinstance(value, datetime.datetime):
        return value.strftime('%Y-%m-%d %H:%M %Z')
    return value


def _xml_text(element):
    if element is None:
        return None
    return element.text


class CloudLayerSet(object):
    cloud_layers = set()

    def __init__(self, cloud_layers=()):
        """
        :type cloud_layers: list|set|tuple
        """
        self.cloud_layers = set(cloud_layers)

    def add_cloud_layer(self, cloud_layer):
        """
        :type cloud_layer: CloudLayer
        """
        self.cloud_layers.add(cloud_layer)

    def get_ceiling_cloud_layer(self):
        """
        Returns the lowest layer of broken or overcast clouds.
        :rtype: CloudLayer|None
        """
        lowest_layer = None
        for layer in self.cloud_layers:
            if layer.coverage not in [CloudLayer.BROKEN, CloudLayer.OVERCAST]:
                continue
            if lowest_layer is None:
                lowest_layer = layer
                continue
            if layer.height > lowest_layer.height:
                continue
            if layer.height < lowest_layer.height or \
                    lowest_layer.get_coverage_percentage() < layer.get_coverage_percentage():
                lowest_layer = layer
        return lowest_layer

    def load_xml(self, cloud_layers_xml):
        for cloud_layer_tree in cloud_layers_xml:
            attrs = cloud_layer_tree.attrib
            cloud_layer = CloudLayer(attrs['sky_cover'], attrs.get('cloud_base_ft_agl'))
            self.add_cloud_layer(cloud_layer)

    def __str__(self):
        return str(list(self.cloud_layers))


class CloudLayer(object):
    CLEAR = 'SKC'
    FEW = 'FEW'
    SCATTERED = 'SCT'
    BROKEN = 'BKN'
    OVERCAST = 'OVX'

    coverage = None
    height = None

    def __init__(self, coverage, height=None):
        self.coverage = coverage
        if height is not None:
            self.height = int(height)

    def get_coverage_percentage(self):
        if self.coverage == self.FEW:
            return 0.2
        elif self.coverage == self.SCATTERED:
            return 0.4
        elif self.coverage == self.BROKEN:
            return 0.75
        elif self.coverage == self.OVERCAST:
            return 1.0
        raise Exception("Unknown or unexpected coverage")

    def __str__(self):
        return "%s %s" % (self.coverage, self.height)


class WeatherStation(object):
    station_id = None

    latitude = None
    longitude = None
    elevation = None

    def __init__(self, station_id):
        """
        :type station_id: str
        """
        self.station_id = station_id

    def __str__(self):
        return self.station_id


class WeatherReport(object):
    class Meta:
        abstract = True

    xml_root_tag = None  # A declarative check to ensure the correct XML is being passed

    properties = set()
    station = None
    xml_data = None
    raw_text = None

    temp = None
    dewpoint = None
    wind = None
    visibility = None
    altimeter = None
    cloud_layers = None
    flight_category = None
    wx_string = None

    def __init__(self, xml_data):
        """
        :type xml_data: ElementTree.Element
        """
        if not isinstance(xml_data, ElementTree.Element):
            raise Exception("Invalid xml_data encountered: %s" % xml_data)
        if xml_data.tag != self.xml_root_tag:
            raise Exception("xml_data root tag should be %s, but is %s" % (self.xml_root_tag, xml_data.tag))
        self.xml_data = xml_data
        self.parse_xml_data()

    def parse_xml_data(self):
        """
        Parses `xml_data` and loads it into object properties.
        """
        self.raw_text = self.xml_data.find('raw_text').text
        self.station = WeatherStation(self.xml_data.find('station_id').text)
        self.station.latitude = float(self.xml_data.find('latitude').text)
        self.station.longitude = float(self.xml_data.find('longitude').text)
        self.station.elevation = float(self.xml_data.find('elevation_m').text) * 3.28084


class Wind(object):
    direction = None
    speed = None
    gust = None

    def __init__(self, direction, speed, gust=None):
        """
        :type direction: int|str
        :type speed: int|str
        :type gust: int|str|None
        """
        self.direction = int(direction)
        self.speed = int(speed)
        if gust is not None:
            self.gust = int(gust)

    def __str__(self):
        ret = "%d@%d" % self.direction, self.speed
        if self.gust is not None:
            ret += "-%d" % self.gust
        return ret


class WeatherReportSet(object):
    class Meta:
        abstract = True

    station_set = set()
    report_set = set()
    xml_data = None

    def __init__(self, station_id_or_station_ids=()):
        """
        :type station_id_or_station_ids: str|set|list|tuple
        :param station_id_or_station_ids: Pass a single station ID string or a list of several.
        """
        if isinstance(station_id_or_station_ids, str):
            station_id_or_station_ids = [station_id_or_station_ids]
        self.station_set = set(station_id_or_station_ids)

    def get_api_url(self):
        raise AbstractMethodError("Abstract method must be implemented by subclass")

    @property
    def station_string(self):
        """
        :rtype: str
        :returns: comma-separated list of station IDs
        """
        return ','.join(self.station_set)

    def refresh(self, mock_response=None):
        self.download_data(mock_response=mock_response)
        self.parse_data()

    def download_data(self, mock_response=None):
        """
        Loads XML data into the `xml_data` attribute.
        """
        if mock_response is not None:
            body = mock_response
        else:
            api_url = self.get_api_url()
            body = urlopen(api_url).read()
        xml_root = ElementTree.fromstring(body)
        xml_warnings = xml_root.find('warnings')
        if len(xml_warnings.attrib) != 0:
            print("Data warnings found: %s" % xml_warnings.attrib)
        xml_errors = xml_root.find('errors')
        if len(xml_errors.attrib) != 0:
            raise Exception("Data errors found: %s" % xml_errors.attrib)
        self.xml_data = xml_root.find('data')

    def parse_data(self):
        raise AbstractMethodError("Abstract method must be implemented by subclass")


class MetarSet(WeatherReportSet):
    def get_api_url(self):
        return "%(base_url)s?dataSource=metars&requestType=retrieve&format=XML&stationString=%(station_string)s&hoursBeforeNow=2" % {
            'base_url': BASE_URL,
            'station_string': self.station_string,
        }

    def parse_data(self):
        metar_elms = self.xml_data.findall('METAR')
        for metar_elm in metar_elms:
            metar = Metar(metar_elm)
            self.report_set.add(metar)

    def get_latest(self):
        """
        :rtype: Metar|None
        :returns: most recent metar, none if no metars exist
        """
        latest = None
        for metar in self.report_set:
            if latest is None:
                latest = metar
                continue
            assert isinstance(metar.observation_time, datetime.datetime)
            if metar.observation_time > latest.observation_time:
                latest = metar
        return latest


class Metar(WeatherReport):
    xml_root_tag = 'METAR'

    observation_time = None

    def __init__(self, xml_data):
        super(Metar, self).__init__(xml_data)

    def get_api_url(self):
        return "%(base_url)s?dataSource=metars&requestType=retrieve&format=XML&stationString=%(station_id)s&hoursBeforeNow=2" % {
            'base_url': BASE_URL,
            'station_id': self.station.station_id,
        }

    def parse_xml_data(self):
        super(Metar, self).parse_xml_data()

        self._init_with_property('observation_time')
        self._init_with_property('temp_c', 'temp')
        self._init_with_property('dewpoint_c', 'dewpoint')
        self.wind = Wind(
            _xml_text(self.xml_data.find('wind_dir_degrees')),
            _xml_text(self.xml_data.find('wind_speed_kt')),
            _xml_text(self.xml_data.find('wind_gust_kt')),
        )
        self.properties.add('wind')
        self._init_with_property('visibility_statute_mi', 'visibility')
        self._init_with_property('altim_in_hg', 'altimeter')
        self._init_with_property('flight_category')
        self._init_with_property('wx_string')

        self.cloud_layers = CloudLayerSet()
        self.cloud_layers.load_xml(self.xml_data.findall('sky_condition'))
        self.properties.add('cloud_layers')

    def get_ceiling_cloud_layer(self):
        cloud_layers = self.cloud_layers
        if cloud_layers is None:
            raise Exception("cloud_layers has not been initialized")
        assert isinstance(cloud_layers, CloudLayerSet)
        return cloud_layers.get_ceiling_cloud_layer()

    def _init_with_property(self, prop, model_prop=None):
        xml = self.xml_data
        if xml is None:
            raise Exception("xml_data must be defined")
        if model_prop is None:
            model_prop = prop
        subtree = xml.find(prop)
        if subtree is None:
            return
        val = subtree.text
        if re.search(r'(_|\b)time(_|\b)', model_prop) is not None:
            val = dateutil.parser.parse(val)
        else:
            try:
                val = float(val) if '.' in val else int(val)
            except ValueError:
                pass
        setattr(self, model_prop, val)
        self.properties.add(model_prop)

    def __str__(self):
        return str(self.station)

    def detail_string(self):
        ret = ""
        for prop in self.properties:
            if ret != "":
                ret += "\n"
            val = getattr(self, prop)
            ret += "%s:\t%s" % (prop, _format(val))
        return ret
