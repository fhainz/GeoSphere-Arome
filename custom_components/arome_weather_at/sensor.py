"""Einzelsensoren fuer alle aktuellen Werte, die die API liefert (ueber die
weather-Entity hinaus, z.B. fuer Automationen/Graphen ohne Attribut-Zugriff)."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    UnitOfPrecipitationDepth,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import GeosphereAromeConfigEntry
from .const import DOMAIN
from .coordinator import GeosphereAromeCoordinator


@dataclass(frozen=True, kw_only=True)
class AromeSensorDescription(SensorEntityDescription):
    value_fn: Callable[[dict], object] = lambda current: None


SENSOR_DESCRIPTIONS: tuple[AromeSensorDescription, ...] = (
    AromeSensorDescription(
        key="temperature",
        translation_key="temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda c: c.get("temperature"),
    ),
    AromeSensorDescription(
        key="apparent_temperature",
        translation_key="apparent_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_fn=lambda c: c.get("apparent_temperature"),
    ),
    AromeSensorDescription(
        key="humidity",
        translation_key="humidity",
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda c: c.get("humidity"),
    ),
    AromeSensorDescription(
        key="cloud_coverage",
        translation_key="cloud_coverage",
        icon="mdi:cloud-percent",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda c: c.get("cloud_coverage"),
    ),
    AromeSensorDescription(
        key="pressure",
        translation_key="pressure",
        device_class=SensorDeviceClass.PRESSURE,
        native_unit_of_measurement=UnitOfPressure.HPA,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_fn=lambda c: c.get("pressure"),
    ),
    AromeSensorDescription(
        key="wind_speed",
        translation_key="wind_speed",
        device_class=SensorDeviceClass.WIND_SPEED,
        native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda c: c.get("wind_speed"),
    ),
    AromeSensorDescription(
        key="wind_gust_speed",
        translation_key="wind_gust_speed",
        device_class=SensorDeviceClass.WIND_SPEED,
        native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:weather-windy",
        value_fn=lambda c: c.get("wind_gust_speed"),
    ),
    AromeSensorDescription(
        key="wind_bearing",
        translation_key="wind_bearing",
        native_unit_of_measurement="°",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:compass-outline",
        entity_registry_enabled_default=False,
        value_fn=lambda c: c.get("wind_bearing"),
    ),
    AromeSensorDescription(
        key="precipitation",
        translation_key="precipitation",
        device_class=SensorDeviceClass.PRECIPITATION,
        native_unit_of_measurement=UnitOfPrecipitationDepth.MILLIMETERS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda c: c.get("precipitation"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: GeosphereAromeConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    async_add_entities(
        AromeSensor(entry, coordinator, description)
        for description in SENSOR_DESCRIPTIONS
    )


class AromeSensor(CoordinatorEntity[GeosphereAromeCoordinator], SensorEntity):
    """Einzelwert-Sensor, gespeist aus demselben Coordinator wie die weather-Entity."""

    _attr_has_entity_name = True
    entity_description: AromeSensorDescription

    def __init__(
        self,
        entry: GeosphereAromeConfigEntry,
        coordinator: GeosphereAromeCoordinator,
        description: AromeSensorDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "GeoSphere Austria / Open-Meteo",
            "model": "AROME 2.5km",
            "entry_type": "service",
        }

    @property
    def native_value(self):
        return self.entity_description.value_fn(self.coordinator.data.current)
