"""Sensor platform for CCU Balance."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import CcuBalanceCoordinator
from .const import CONF_LOGIN, DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up CCU Balance sensor."""
    coordinator: CcuBalanceCoordinator = entry.runtime_data
    async_add_entities([CcuBalanceSensor(coordinator, entry)])


class CcuBalanceSensor(CoordinatorEntity[CcuBalanceCoordinator], SensorEntity):
    """CCU Balance sensor."""

    # Не используем SensorDeviceClass.MONETARY, потому что фронтенд Home Assistant
    # может отображать валюту как символ (например, ₽/Р).
    # Обычная единица измерения показывает именно RUB.
    _attr_native_unit_of_measurement = "RUB"
    _attr_icon = "mdi:cash"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 2
    _attr_has_entity_name = True
    _attr_translation_key = "balance"

    def __init__(self, coordinator: CcuBalanceCoordinator, entry: ConfigEntry) -> None:
        """Initialize sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_balance"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "ccu.su",
            "configuration_url": "https://ccu.su/",
        }

    @property
    def native_value(self) -> float:
        """Return balance."""
        if not self.coordinator.data:
            return 0.0
        return float(f"{float(self.coordinator.data.get('balance', 0.0)):.2f}")

    @property
    def extra_state_attributes(self) -> dict:
        """Return diagnostic attributes."""
        data = self.coordinator.data or {}
        return {
            "ok": data.get("ok", False),
            "status": data.get("status", "unknown"),
            "raw_balance": data.get("raw_balance"),
            "login": self._entry.data.get(CONF_LOGIN),
        }
