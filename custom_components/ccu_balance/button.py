"""Button platform for CCU Balance."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import CcuBalanceCoordinator
from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up CCU Balance button."""
    coordinator: CcuBalanceCoordinator = entry.runtime_data
    async_add_entities([CcuBalanceUpdateButton(coordinator, entry)])


class CcuBalanceUpdateButton(CoordinatorEntity[CcuBalanceCoordinator], ButtonEntity):
    """Manual update button for CCU Balance."""

    _attr_has_entity_name = True
    _attr_translation_key = "manual_update"

    def __init__(self, coordinator: CcuBalanceCoordinator, entry: ConfigEntry) -> None:
        """Initialize button."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_manual_update"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "ccu.su",
            "configuration_url": "https://ccu.su/",
        }

    async def async_press(self) -> None:
        """Trigger manual data refresh."""
        await self.coordinator.async_request_refresh()
