import pandas as pd
from pkg_resources import resource_stream
from collections import namedtuple
from eeweather.geo import get_lat_long_climate_zones
import numpy as np
import logging
from .location_code import location_lookup

logger = logging.getLogger('epathermostat')

BASELINE_TEMPERATURE = {
    'Very-Cold/Cold': {
        'heating': 68.0,
        'cooling': 73.0,
        },
    'Mixed-Humid': {
        'heating': 69.0,
        'cooling': 73.0,
        },
    'Mixed-Dry/Hot-Dry': {
        'heating': 69.0,
        'cooling': 75.0,
        },
    'Hot-Humid': {
        'heating': 70.0,
        'cooling': 75.0,
        },
    'Marine': {
        'heating': 67.0,
        'cooling': np.nan,
        }
    }

CLIMATE_ZONE_MAPPING = {
    'Cold': 'Very-Cold/Cold',
    'Very Cold': 'Very-Cold/Cold',
    'Hot-Dry': 'Mixed-Dry/Hot-Dry',
    'Mixed-Dry': 'Mixed-Dry/Hot-Dry',
    }


def retrieve_climate_zone(location_code):
    """ Performs a lookup of the Climate Zone from eeweather
    and returns the climate zone and baseline regional comfort temperatures.

    Parameters
    ----------
    location_code : The ZIP / Postal Code to lookup using eeweather's climate zones

    Returns
    -------

    climate_zone_nt : named tuple
       Named Tuple consisting of the Climate Zone, baseline_regional_cooling_comfort_temperature, and baseline_regional_heating_comfort_temperature
    """
    ClimateZone = namedtuple('ClimateZone', ['climate_zone', 'baseline_regional_cooling_comfort_temperature', 'baseline_regional_heating_comfort_temperature'])
    try:
        lat, lon = location_lookup(location_code)
        latitude = float(lat)
        longitude = float(lon)
        ee_climate_zones = get_lat_long_climate_zones(latitude, longitude)
        ba_climate_zone = ee_climate_zones['ba_climate_zone']
        climate_zone = CLIMATE_ZONE_MAPPING.get(ba_climate_zone, ba_climate_zone)
        baseline_regional_cooling_comfort_temperature = BASELINE_TEMPERATURE.get(climate_zone, {}).get('cooling', None)
        baseline_regional_heating_comfort_temperature = BASELINE_TEMPERATURE.get(climate_zone, {}).get('heating', None)

        climate_zone_nt = ClimateZone(climate_zone, baseline_regional_cooling_comfort_temperature, baseline_regional_heating_comfort_temperature)
    except IndexError:
        logger.warning(f'Location Code {location_code} is not found. Is it valid?')
        climate_zone_nt = ClimateZone(np.nan, np.nan, np.nan)
    return climate_zone_nt
