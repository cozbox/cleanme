from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN
from .coordinator import CleanMeZone


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities,
) -> None:
    """Set up CleanMe binary sensors for a config entry."""
    zone: CleanMeZone = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([CleanMeNeedsTidyBinarySensor(zone, entry)])


class CleanMeNeedsTidyBinarySensor(BinarySensorEntity):
    """Binary flag: does this room need tidying?"""

    _attr_has_entity_name = True
    _attr_name = "Needs tidy"
    _attr_device_class = BinarySensorDeviceClass.PROBLEM
    _attr_icon = "mdi:broom"

    def __init__(self, zone: CleanMeZone, entry: ConfigEntry) -> None:
        self._zone = zone
        self._entry_id = entry.entry_id

    async def async_added_to_hass(self) -> None:
        self._zone.add_listener(self.async_write_ha_state)

    @property
    def unique_id(self) -> str:
        return f"{self._entry_id}_needs_tidy"

    @property
    def is_on(self) -> bool:
        return self._zone.needs_tidy
