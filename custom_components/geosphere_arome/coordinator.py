"""Data update coordinator: pollt Open-Meteo mit fix gesetztem AROME-Austria-Modell."""

from __future__ import annotations

import datetime
from dataclasses import dataclass

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    API_URL,
    CURRENT_PARAMS,
    DAILY_PARAMS,
    HOURLY_PARAMS,
    LOGGER,
    MODEL,
    UPDATE_INTERVAL_MINUTES,
    WMO_CONDITION_MAP,
)


def _condition_from_code(code: int | None, is_day: bool = True) -> str | None:
    if code is None:
        return None
    if code == 0 and not is_day:
        return "clear-night"
    return WMO_CONDITION_MAP.get(code)


@dataclass
class GeosphereAromeData:
    """Aufbereitete Antwort eines Poll-Zyklus."""

    current: dict
    hourly: list[dict]
    daily: list[dict]


class GeosphereAromeCoordinator(DataUpdateCoordinator[GeosphereAromeData]):
    """Holt Open-Meteo-Daten mit models=geosphere_arome_austria in einem Request."""

    def __init__(self, hass: HomeAssistant, latitude: float, longitude: float) -> None:
        super().__init__(
            hass,
            LOGGER,
            name="geosphere_arome",
            update_interval=datetime.timedelta(minutes=UPDATE_INTERVAL_MINUTES),
        )
        self._latitude = latitude
        self._longitude = longitude

    async def _async_update_data(self) -> GeosphereAromeData:
        session = async_get_clientsession(self.hass)
        params = {
            "latitude": self._latitude,
            "longitude": self._longitude,
            "models": MODEL,
            "current": CURRENT_PARAMS,
            "hourly": HOURLY_PARAMS,
            "daily": DAILY_PARAMS,
            "timezone": "auto",
            "forecast_days": 3,
        }
        try:
            async with session.get(API_URL, params=params, timeout=15) as resp:
                if resp.status != 200:
                    body = await resp.text()
                    raise UpdateFailed(f"Open-Meteo HTTP {resp.status}: {body[:200]}")
                payload = await resp.json()
        except UpdateFailed:
            raise
        except Exception as exc:  # noqa: BLE001 - alle Netzwerk-/Parsing-Fehler sind gleich zu behandeln
            raise UpdateFailed(f"Open-Meteo Anfrage fehlgeschlagen: {exc}") from exc

        try:
            return self._parse(payload)
        except (KeyError, IndexError, TypeError) as exc:
            raise UpdateFailed(f"Unerwartetes Open-Meteo Antwortformat: {exc}") from exc

    @staticmethod
    def _parse(payload: dict) -> GeosphereAromeData:
        cur = payload["current"]
        is_day = bool(cur.get("is_day", 1))
        current = {
            "time": cur["time"],
            "temperature": cur.get("temperature_2m"),
            "apparent_temperature": cur.get("apparent_temperature"),
            "humidity": cur.get("relative_humidity_2m"),
            "cloud_coverage": cur.get("cloud_cover"),
            "pressure": cur.get("pressure_msl"),
            "wind_speed": cur.get("wind_speed_10m"),
            "wind_bearing": cur.get("wind_direction_10m"),
            "wind_gust_speed": cur.get("wind_gusts_10m"),
            "precipitation": cur.get("precipitation"),
            "condition": _condition_from_code(cur.get("weather_code"), is_day),
        }

        hourly_raw = payload.get("hourly", {})
        hourly = []
        for i, ts in enumerate(hourly_raw.get("time", [])):
            hourly.append({
                "datetime": ts,
                "temperature": _at(hourly_raw, "temperature_2m", i),
                "condition": _condition_from_code(_at(hourly_raw, "weather_code", i)),
                "cloud_coverage": _at(hourly_raw, "cloud_cover", i),
                "wind_speed": _at(hourly_raw, "wind_speed_10m", i),
                "wind_gust_speed": _at(hourly_raw, "wind_gusts_10m", i),
                "wind_bearing": _at(hourly_raw, "wind_direction_10m", i),
                "precipitation": _at(hourly_raw, "precipitation", i),
                "precipitation_probability": _at(hourly_raw, "precipitation_probability", i),
            })

        daily_raw = payload.get("daily", {})
        daily = []
        for i, ts in enumerate(daily_raw.get("time", [])):
            daily.append({
                "datetime": ts,
                "condition": _condition_from_code(_at(daily_raw, "weather_code", i)),
                "temperature": _at(daily_raw, "temperature_2m_max", i),
                "templow": _at(daily_raw, "temperature_2m_min", i),
                "precipitation": _at(daily_raw, "precipitation_sum", i),
                "wind_gust_speed": _at(daily_raw, "wind_gusts_10m_max", i),
            })

        return GeosphereAromeData(current=current, hourly=hourly, daily=daily)


def _at(series: dict, key: str, i: int):
    values = series.get(key)
    if values is None or i >= len(values):
        return None
    return values[i]
