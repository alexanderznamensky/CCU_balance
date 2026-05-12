"""Config flow for CCU Balance."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import CcuBalanceApiClient
from .const import (
    CONF_LOGIN,
    CONF_SCAN_INTERVAL,
    CONF_UPDATE_INTERVAL_HOURS,
    DEFAULT_UPDATE_INTERVAL_HOURS,
    DOMAIN,
    MAX_UPDATE_INTERVAL_HOURS,
    MIN_UPDATE_INTERVAL_HOURS,
)


def _normalize_hours(value: int) -> int:
    """Clamp update interval to supported range."""
    return min(max(int(value), MIN_UPDATE_INTERVAL_HOURS), MAX_UPDATE_INTERVAL_HOURS)


def _hours_from_entry(config_entry: config_entries.ConfigEntry) -> int:
    """Read current interval, including fallback from old seconds setting."""
    if CONF_UPDATE_INTERVAL_HOURS in config_entry.options:
        return _normalize_hours(config_entry.options[CONF_UPDATE_INTERVAL_HOURS])
    if CONF_UPDATE_INTERVAL_HOURS in config_entry.data:
        return _normalize_hours(config_entry.data[CONF_UPDATE_INTERVAL_HOURS])
    if CONF_SCAN_INTERVAL in config_entry.options:
        return _normalize_hours(round(int(config_entry.options[CONF_SCAN_INTERVAL]) / 3600))
    if CONF_SCAN_INTERVAL in config_entry.data:
        return _normalize_hours(round(int(config_entry.data[CONF_SCAN_INTERVAL]) / 3600))
    return DEFAULT_UPDATE_INTERVAL_HOURS


class CcuBalanceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for CCU Balance."""

    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None):
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            login = user_input[CONF_LOGIN]
            password = user_input[CONF_PASSWORD]
            interval_hours = _normalize_hours(user_input[CONF_UPDATE_INTERVAL_HOURS])

            await self.async_set_unique_id(login)
            self._abort_if_unique_id_configured()

            session = async_get_clientsession(self.hass)
            client = CcuBalanceApiClient(session, login, password)
            result = await client.async_get_balance()

            if result.get("status") in {"http_401", "http_403"}:
                errors["base"] = "invalid_auth"
            else:
                return self.async_create_entry(
                    title=f"CCU Balance {login}",
                    data={
                        CONF_LOGIN: login,
                        CONF_PASSWORD: password,
                        CONF_UPDATE_INTERVAL_HOURS: interval_hours,
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_LOGIN): str,
                    vol.Required(CONF_PASSWORD): str,
                    vol.Optional(
                        CONF_UPDATE_INTERVAL_HOURS,
                        default=DEFAULT_UPDATE_INTERVAL_HOURS,
                    ): vol.All(
                        vol.Coerce(int),
                        vol.Range(min=MIN_UPDATE_INTERVAL_HOURS, max=MAX_UPDATE_INTERVAL_HOURS),
                    ),
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Return options flow."""
        return CcuBalanceOptionsFlow()


class CcuBalanceOptionsFlow(config_entries.OptionsFlow):
    """Handle options for CCU Balance."""

    async def async_step_init(self, user_input: dict | None = None):
        """Manage options."""
        if user_input is not None:
            interval_hours = _normalize_hours(user_input[CONF_UPDATE_INTERVAL_HOURS])
            return self.async_create_entry(
                title="",
                data={CONF_UPDATE_INTERVAL_HOURS: interval_hours},
            )

        current_interval_hours = _hours_from_entry(self.config_entry)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_UPDATE_INTERVAL_HOURS,
                        default=current_interval_hours,
                    ): vol.All(
                        vol.Coerce(int),
                        vol.Range(min=MIN_UPDATE_INTERVAL_HOURS, max=MAX_UPDATE_INTERVAL_HOURS),
                    )
                }
            ),
        )
