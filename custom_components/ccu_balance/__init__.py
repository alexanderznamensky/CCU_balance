"""CCU Balance integration."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .api import CcuBalanceApiClient
from .const import (
    CONF_LOGIN,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    CONF_UPDATE_INTERVAL_HOURS,
    DEFAULT_UPDATE_INTERVAL_HOURS,
    DOMAIN,
    MAX_UPDATE_INTERVAL_HOURS,
    MIN_UPDATE_INTERVAL_HOURS,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BUTTON]

type CcuBalanceConfigEntry = ConfigEntry[CcuBalanceCoordinator]


def _get_update_interval_hours(entry: ConfigEntry) -> int:
    """Return update interval in hours, with migration fallback from old seconds option."""
    if CONF_UPDATE_INTERVAL_HOURS in entry.options:
        hours = int(entry.options[CONF_UPDATE_INTERVAL_HOURS])
    elif CONF_UPDATE_INTERVAL_HOURS in entry.data:
        hours = int(entry.data[CONF_UPDATE_INTERVAL_HOURS])
    elif CONF_SCAN_INTERVAL in entry.options:
        hours = round(int(entry.options[CONF_SCAN_INTERVAL]) / 3600)
    elif CONF_SCAN_INTERVAL in entry.data:
        hours = round(int(entry.data[CONF_SCAN_INTERVAL]) / 3600)
    else:
        hours = DEFAULT_UPDATE_INTERVAL_HOURS

    return min(max(hours, MIN_UPDATE_INTERVAL_HOURS), MAX_UPDATE_INTERVAL_HOURS)


async def async_setup_entry(hass: HomeAssistant, entry: CcuBalanceConfigEntry) -> bool:
    """Set up CCU Balance from a config entry."""
    coordinator = CcuBalanceCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator
    entry.async_on_unload(entry.add_update_listener(async_update_options))

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: CcuBalanceConfigEntry) -> bool:
    """Unload CCU Balance config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_update_options(hass: HomeAssistant, entry: CcuBalanceConfigEntry) -> None:
    """Reload entry after options update."""
    await hass.config_entries.async_reload(entry.entry_id)


class CcuBalanceCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator for CCU Balance data."""

    config_entry: CcuBalanceConfigEntry

    def __init__(self, hass: HomeAssistant, entry: CcuBalanceConfigEntry) -> None:
        """Initialize coordinator."""
        self.config_entry = entry
        interval_hours = _get_update_interval_hours(entry)

        session = async_get_clientsession(hass)
        self.api = CcuBalanceApiClient(
            session=session,
            login=entry.data[CONF_LOGIN],
            password=entry.data[CONF_PASSWORD],
        )

        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=timedelta(hours=interval_hours),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API."""
        return await self.api.async_get_balance()
