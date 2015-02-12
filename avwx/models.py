import urllib2
import xml.etree.ElementTree as ET
import datetime
import dateutil.parser

BASE_URL = "https://aviationweather.gov/adds/dataserver_current/httpparam"

def _format(value):
    if isinstance(value, datetime.datetime):
        return value.strftime('%Y-%m-%d %H:%M %Z')
    return value

def get_base_cloud_layer(cloud_layers):
    lowest_layer = None
    for layer in cloud_layers:
        if layer.coverage not in [SkyCondition.BROKEN, SkyCondition.OVERCAST]:
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

class SkyCondition(object):
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

class Metar(object):
    metar_tree = None
    properties = []

    station_id = None
    observation_time = None

    raw_text = None

    latitude = None
    longitude = None
    elevation = None
    temp = None
    dewpoint = None
    wind_dir = None
    wind_speed = None
    wind_gust = None
    visibility = None
    altimiter = None
    cloud_layers = None
    flight_category = None
    wx_string = None

    def __init__(self, station_id, fake=False):
        self.station_id = station_id
        self.fake = fake

    def get_base_cloud_layer(self):
        return get_base_cloud_layer(self.cloud_layers)

    def refresh(self):
        if self.fake is False:
            body = urllib2.urlopen(
                "%s?dataSource=metars&requestType=retrieve&format=XML&stationString=%s&hoursBeforeNow=2" %
                (BASE_URL, self.station_id)
            ).read()
            root = ET.fromstring(body)
        else:
            root = ET.parse(self.fake)
        metar = root.find('data').find('METAR')
        if metar is None:
            raise Exception("Metar could not be found.")
        self.init_with_data_from_tree(metar)

    def _init_with_property(self, prop, model_prop=None):
        tree = self.metar_tree
        if tree is None:
            raise Exception("metar_tree must be defined")
        if model_prop is None:
            model_prop = prop
        subtree = tree.find(prop)
        if subtree is None:
            return
        val = subtree.text
        if 'time' in model_prop:
            val = dateutil.parser.parse(val)
        else:
            try:
                val = float(val) if '.' in val else int(val)
            except ValueError:
                pass
        setattr(self, model_prop, val)
        self.properties.append(model_prop)

    def init_with_data_from_tree(self, metar_tree):
        self.properties = []

        self.metar_tree = metar_tree

        self._init_with_property('raw_text')

        self._init_with_property('station_id')
        self._init_with_property('observation_time')
        self._init_with_property('latitude')
        self._init_with_property('longitude')
        self._init_with_property('elevation_m', 'elevation')
        self._init_with_property('temp_c', 'temp')
        self._init_with_property('dewpoint_c', 'dewpoint')
        self._init_with_property('wind_dir_degrees', 'wind_dir')
        self._init_with_property('wind_speed_kt', 'wind_speed')
        self._init_with_property('wind_gust_kt', 'wind_gust')
        self._init_with_property('visibility_statute_mi', 'visibility')
        self._init_with_property('altim_in_hg', 'altimiter')
        self._init_with_property('flight_category')
        self.elevation = self.elevation * 3.28084
        self._init_with_property('wx_string')

        cloud_layers = metar_tree.findall('sky_condition')
        self.cloud_layers = []
        for cloud_layer_tree in cloud_layers:
            attrs = cloud_layer_tree.attrib
            cloud_layer = SkyCondition(attrs['sky_cover'], attrs.get('cloud_base_ft_agl'))
            self.cloud_layers.append(cloud_layer)
        self.properties.append('cloud_layers')

    def __str__(self):
        return self.station_id

    def detail_string(self):
        ret = ""
        for prop in self.properties:
            if ret != "":
                ret += "\n"
            val = getattr(self, prop)
            ret += "%s:\t%s" % (prop, _format(val))
        return ret

