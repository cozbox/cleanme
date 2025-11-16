from __future__ import annotations

from typing import Any, Dict

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN, ATTR_TASKS, ATTR_FULL_TASKS, ATTR_COMMENT, ATTR_LAST_ERROR
from .coordinator import CleanMeZone


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities,
) -> None:
    """Set up CleanMe sensors for a config entry."""
    zone: CleanMeZone = hass.data[DOMAIN][entry.entry_id]

    entities: list[SensorEntity] = [
        CleanMeStatusSensor(zone, entry),
        CleanMeTaskCountSensor(zone, entry),
        CleanMeLastCheckedSensor(zone, entry),
    ]

    async_add_entities(entities)


class CleanMeBaseSensor(SensorEntity):
    """Base class for CleanMe sensors."""

    _attr_has_entity_name = True

    def __init__(self, zone: CleanMeZone, entry: ConfigEntry) -> None:
        self._zone = zone
        self._entry_id = entry.entry_id

    async def async_added_to_hass(self) -> None:
        self._zone.add_listener(self.async_write_ha_state)


class CleanMeStatusSensor(CleanMeBaseSensor):
    """Overall tidy status for a zone."""

    _attr_name = "Tidy status"
    _attr_icon = "mdi:broom"

    @property
    def unique_id(self) -> str:
        return f"{self._entry_id}_status"

    @property
    def native_value(self) -> str:
        return self._zone.state.status

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        tasks = self._zone.state.tasks or []
        return {
            ATTR_TASKS: [t.get("title") for t in tasks],
            ATTR_FULL_TASKS: tasks,
            ATTR_COMMENT: self._zone.state.comment,
            ATTR_LAST_ERROR: self._zone.state.last_error,
        }


class CleanMeTaskCountSensor(CleanMeBaseSensor):
    """Number of active tidy tasks."""

    _attr_name = "Tidy task count"
    _attr_icon = "mdi:format-list-checkbox"

    @property
    def unique_id(self) -> str:
        return f"{self._entry_id}_task_count"

    @property
    def native_value(self) -> int:
        return len(self._zone.state.tasks or [])


class CleanMeLastCheckedSensor(CleanMeBaseSensor):
    """When this zone was last analysed."""

    _attr_name = "Last analysed"
    _attr_icon = "mdi:clock-check-outline"
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    @property
    def unique_id(self) -> str:
        return f"{self._entry_id}_last_checked"

    @property
    def native_value(self):
        return self._zone.state.last_checked
