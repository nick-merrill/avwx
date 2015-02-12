# AviationWeather (avwx)

## Disclaimer

**This library is in development and should not be relied upon as
a primary aviation resource.**

This library relies upon the
[ADDS service](http://www.aviationweather.gov/adds/) by the NOAA.

## Installation

1. `pip install avwx`

## Example

Check out an example of how you could use this library:
[FlyTime](https://github.com/NicholasMerrill/FlyTime)

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

#### `Metar` Attributes

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

## In the works

1. TAFs
2. AIRMETs/SIGMETs

