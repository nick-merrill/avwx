# AviationWeather (avwx)

## Installation

1. `pip install avwx`

## Usage

### METARs

    from avwx.models import Metar, SkyCondition

    # Initializes METAR
    jfk_metar = Metar('KJFK')

    # Grabs METAR data from ADDS service.
    jfk_metar.refresh()

    # Print the raw text of the METAR
    print jfk_metar.raw_text

    # Print an exploded summary of the METAR to see what kinds of
    # attributes you can access.
    print jfk_metar.detail_string()

#### METAR Attributes

* `raw_text`
* `station_id` -- e.g. "KJFK"
* `observation_time` -- time the METAR was created (Python `datetime` object)
* `latitude`
* `longitude`
* `elevation` -- elevation of reporting station
* `temp` -- temperature (in Celsius)
* `dewpoint` (in Celsius)
* `wind_dir` -- wind direction (in degrees)
* `wind_speed` -- wind speed (in knots)
* `wind_gust` -- wind gust speed (in knots)
* `visibility` (in statute miles)
* `altimeter` -- altimiter pressure setting (in inches of mercury)
* `flight_category` -- e.g. VFR, LIFR, etc.

