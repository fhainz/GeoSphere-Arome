"""GeoSphere Austria AROME via Open-Meteo (models=geosphere_arome_austria)."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_LATITUDE, CONF_LONGITUDE
from .coordinator import GeosphereAromeCoordinator

PLATFORMS = ["weather", "sensor"]

GeosphereAromeConfigEntry = ConfigEntry[GeosphereAromeCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: GeosphereAromeConfigEntry) -> bool:
    coordinator = GeosphereAromeCoordinator(
        hass, entry.data[CONF_LATITUDE], entry.data[CONF_LONGITUDE]
    )
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: GeosphereAromeConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
