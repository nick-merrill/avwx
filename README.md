# AviationWeather (avwx)

[![Build Status](https://travis-ci.org/cloudrave/avwx.svg?branch=master)](https://travis-ci.org/cloudrave/avwx)

## Disclaimer

**This library is in development and should not be relied upon as
a primary aviation resource.**

This library relies upon the
[ADDS service](http://www.aviationweather.gov/adds/) by the NOAA.

## Installation

*Note: This library supports only Python 3 as of version 1.0.0.*

1. `pip install avwx`

## Examples

Check out an example of how you could use this library:
[avwxsummarizer](https://github.com/cloudrave/avwxsummarizer)

### Quick Example

    from avwx.models import MetarSet

    # Initializes METAR
    jfk_metars = MetarSet('KJFK')

    # Grabs METAR data from ADDS service.
    jfk_metars.refresh()
    
    latest_jfk_metar = jfk_metars.get_latest()

    # Print the raw text of the METAR
    print latest_jfk_metar.raw_text

    # Print an exploded summary of the METAR to see what kinds of
    # attributes you can access.
    print latest_jfk_metar.detail_string()

## Models

### `Metar`

#### Attributes

(Based on [ADDS METAR data type](http://www.aviationweather.gov/dataserver/fields?datatype=metar))

* `raw_text`
* `station` -- `WeatherStation` object
* `observation_time` -- time the METAR was created (Python `datetime` object)
* `temp` -- temperature (in Celsius)
* `dewpoint` (in Celsius)
* `wind` -- `Wind` object
* `visibility` (in statute miles)
* `altimeter` -- altimeter pressure setting (in inches of mercury)
* `flight_category` -- e.g. VFR, LIFR, etc.
* `cloud_layers` -- `CloudLayerSet` object

### `Taf`

#### Attributes

(Based on [ADDS TAF data type](http://www.aviationweather.gov/dataserver/fields?datatype=taf))

* `raw_text`
* `station` -- `WeatherStation` object
* `issue_time`
* `bulletin_time`
* `valid_time_from`
* `valid_time_to`
* `remarks`
* `forecast` -- `TafForecast` object

### `TafForecast`

#### Attributes

* `time_from` -- the start of the forecast time
* `time_to` -- the end time of the forecast
* `change_indicator` -- one of the following:
    * `ChangeIndicator.TEMPORARY`
    * `ChangeIndicator.BECOMING`
    * `ChangeIndicator.FROM`
    * `ChangeIndicator.PROBABLE`
* `time_becoming`
* `probability` -- percent probability (e.g. 70)
* `wind` -- `Wind` object
* `visibility` -- horizontal visibility (in statute miles)
* `altimeter` (in inches of mercury)
* `vertical_visibility` (in feet)
* `wx_string` -- additional weather
* `not_decoded` -- information that wasn't decoded
* `cloud_layers` -- `CloudLayerSet` object

### `Wind`

#### Attributes

* `direction` (in degrees)
* `speed` (in knots)
* `gust` (in knots)


### `WeatherStation`

#### Attributes

* `latitude`
* `longitude`
* `elevation` -- elevation of reporting station (in feet)

## In the works

1. AIRMETs / SIGMETs
2. Testing

