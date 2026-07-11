"""Config flow: Name + Standort, vorbelegt mit der HA-Heimatzone."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers import selector

from .const import CONF_LATITUDE, CONF_LONGITUDE, CONF_NAME, DEFAULT_NAME, DOMAIN


class GeosphereAromeConfigFlow(ConfigFlow, domain=DOMAIN):
    """Ein Schritt: Name + Koordinaten, Default aus der HA-Heimatzone."""

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            await self.async_set_unique_id(
                f"{user_input[CONF_LATITUDE]}_{user_input[CONF_LONGITUDE]}"
            )
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
                    vol.Required(
                        CONF_LATITUDE, default=self.hass.config.latitude
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(step=0.0001, mode=selector.NumberSelectorMode.BOX)
                    ),
                    vol.Required(
                        CONF_LONGITUDE, default=self.hass.config.longitude
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(step=0.0001, mode=selector.NumberSelectorMode.BOX)
                    ),
                }
            ),
        )
