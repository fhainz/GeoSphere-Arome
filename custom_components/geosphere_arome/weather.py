"""Weather-Entity: AROME-Austria-Werte 1:1 als weather_entity fuer andere Add-ons/Automationen."""

from __future__ import annotations

from homeassistant.components.weather import (
    Forecast,
    WeatherEntity,
    WeatherEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfPrecipitationDepth,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import GeosphereAromeConfigEntry
from .const import CONF_LATITUDE, CONF_LONGITUDE, DOMAIN
from .coordinator import GeosphereAromeCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: GeosphereAromeConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities([GeosphereAromeWeather(entry, entry.runtime_data)])


class GeosphereAromeWeather(CoordinatorEntity[GeosphereAromeCoordinator], WeatherEntity):
    """Weather-Entity gespeist aus GeosphereAromeCoordinator (Open-Meteo AROME AT)."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_native_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_native_pressure_unit = UnitOfPressure.HPA
    _attr_native_wind_speed_unit = UnitOfSpeed.KILOMETERS_PER_HOUR
    _attr_native_precipitation_unit = UnitOfPrecipitationDepth.MILLIMETERS
    _attr_supported_features = (
        WeatherEntityFeature.FORECAST_HOURLY | WeatherEntityFeature.FORECAST_DAILY
    )

    def __init__(self, entry: ConfigEntry, coordinator: GeosphereAromeCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = entry.entry_id
        self._attr_attribution = "Daten: GeoSphere Austria (AROME) via Open-Meteo"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "GeoSphere Austria / Open-Meteo",
            "model": "AROME 2.5km",
            "entry_type": "service",
        }
        self._latitude = entry.data[CONF_LATITUDE]
        self._longitude = entry.data[CONF_LONGITUDE]

    @property
    def condition(self) -> str | None:
        return self.coordinator.data.current.get("condition")

    @property
    def native_temperature(self) -> float | None:
        return self.coordinator.data.current.get("temperature")

    @property
    def native_apparent_temperature(self) -> float | None:
        return self.coordinator.data.current.get("apparent_temperature")

    @property
    def humidity(self) -> float | None:
        return self.coordinator.data.current.get("humidity")

    @property
    def cloud_coverage(self) -> float | None:
        return self.coordinator.data.current.get("cloud_coverage")

    @property
    def native_pressure(self) -> float | None:
        return self.coordinator.data.current.get("pressure")

    @property
    def native_wind_speed(self) -> float | None:
        return self.coordinator.data.current.get("wind_speed")

    @property
    def native_wind_gust_speed(self) -> float | None:
        return self.coordinator.data.current.get("wind_gust_speed")

    @property
    def wind_bearing(self) -> float | None:
        return self.coordinator.data.current.get("wind_bearing")

    async def async_forecast_hourly(self) -> list[Forecast] | None:
        return [
            Forecast(
                datetime=h["datetime"],
                condition=h["condition"],
                native_temperature=h["temperature"],
                cloud_coverage=h["cloud_coverage"],
                native_wind_speed=h["wind_speed"],
                native_wind_gust_speed=h["wind_gust_speed"],
                wind_bearing=h["wind_bearing"],
                native_precipitation=h["precipitation"],
                precipitation_probability=h["precipitation_probability"],
            )
            for h in self.coordinator.data.hourly
        ]

    async def async_forecast_daily(self) -> list[Forecast] | None:
        return [
            Forecast(
                datetime=d["datetime"],
                condition=d["condition"],
                native_temperature=d["temperature"],
                native_templow=d["templow"],
                native_precipitation=d["precipitation"],
                native_wind_gust_speed=d["wind_gust_speed"],
            )
            for d in self.coordinator.data.daily
        ]
