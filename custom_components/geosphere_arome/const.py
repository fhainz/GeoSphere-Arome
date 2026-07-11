"""Constants for the GeoSphere Austria AROME (via Open-Meteo) integration."""

from __future__ import annotations

import logging

DOMAIN = "geosphere_arome"
LOGGER = logging.getLogger(__package__)

API_URL = "https://api.open-meteo.com/v1/forecast"
MODEL = "geosphere_arome_austria"

CONF_NAME = "name"
CONF_LATITUDE = "latitude"
CONF_LONGITUDE = "longitude"

DEFAULT_NAME = "GeoSphere Austria AROME"

UPDATE_INTERVAL_MINUTES = 15

CURRENT_PARAMS = (
    "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,"
    "weather_code,cloud_cover,pressure_msl,wind_speed_10m,wind_direction_10m,"
    "wind_gusts_10m,is_day"
)
HOURLY_PARAMS = (
    "temperature_2m,weather_code,cloud_cover,wind_speed_10m,wind_gusts_10m,"
    "wind_direction_10m,precipitation,precipitation_probability"
)
DAILY_PARAMS = (
    "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,"
    "wind_gusts_10m_max"
)

# WMO weather code -> HA condition. Code 0 ist Tag/Nacht-abhaengig (sunny/clear-night),
# siehe _condition_from_code in coordinator.py.
WMO_CONDITION_MAP: dict[int, str] = {
    0: "sunny",
    1: "partlycloudy",
    2: "partlycloudy",
    3: "cloudy",
    45: "fog",
    48: "fog",
    51: "rainy",
    53: "rainy",
    55: "rainy",
    56: "rainy",
    57: "rainy",
    61: "rainy",
    63: "rainy",
    65: "pouring",
    66: "rainy",
    67: "pouring",
    71: "snowy",
    73: "snowy",
    75: "snowy",
    77: "snowy",
    80: "rainy",
    81: "rainy",
    82: "pouring",
    85: "snowy",
    86: "snowy",
    95: "lightning-rainy",
    96: "lightning-rainy",
    99: "lightning-rainy",
}
