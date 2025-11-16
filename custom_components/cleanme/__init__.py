from __future__ import annotations

from typing import Any, Dict

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.typing import ConfigType

from .const import (
    DOMAIN,
    PLATFORMS,
    SERVICE_REQUEST_CHECK,
    SERVICE_SNOOZE_ZONE,
    SERVICE_CLEAR_TASKS,
    ATTR_ZONE,
    ATTR_DURATION_MINUTES,
)
from .coordinator import CleanMeZone


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up from YAML (not used)."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a CleanMe config entry."""
    hass.data.setdefault(DOMAIN, {})

    zone = CleanMeZone(
        hass=hass,
        entry_id=entry.entry_id,
        name=entry.data.get("name") or entry.title,
        data=entry.data,
    )

    hass.data[DOMAIN][entry.entry_id] = zone

    await zone.async_setup()
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    if not hass.services.has_service(DOMAIN, SERVICE_REQUEST_CHECK):
        _register_services(hass)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a CleanMe entry."""
    zone: CleanMeZone = hass.data[DOMAIN].pop(entry.entry_id, None)
    if zone:
        await zone.async_unload()

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if not hass.data[DOMAIN]:
        hass.services.remove(DOMAIN, SERVICE_REQUEST_CHECK)
        hass.services.remove(DOMAIN, SERVICE_SNOOZE_ZONE)
        hass.services.remove(DOMAIN, SERVICE_CLEAR_TASKS)

    return unload_ok


def _find_zone_by_name(hass: HomeAssistant, zone_name: str) -> CleanMeZone | None:
    for zone in hass.data.get(DOMAIN, {}).values():
        if zone.name == zone_name:
            return zone
    return None


def _register_services(hass: HomeAssistant) -> None:
    """Register CleanMe domain services."""

    async def handle_request_check(call: ServiceCall) -> None:
        zone_name = call.data[ATTR_ZONE]
        zone = _find_zone_by_name(hass, zone_name)
        if not zone:
            return
        await zone.async_request_check(reason="service")

    async def handle_snooze(call: ServiceCall) -> None:
        zone_name = call.data[ATTR_ZONE]
        minutes = int(call.data[ATTR_DURATION_MINUTES])
        zone = _find_zone_by_name(hass, zone_name)
        if not zone:
            return
        await zone.async_snooze(minutes)

    async def handle_clear_tasks(call: ServiceCall) -> None:
        zone_name = call.data[ATTR_ZONE]
        zone = _find_zone_by_name(hass, zone_name)
        if not zone:
            return
        await zone.async_clear_tasks()

    hass.services.async_register(
        DOMAIN,
        SERVICE_REQUEST_CHECK,
        handle_request_check,
        vol.Schema({vol.Required(ATTR_ZONE): str}),
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_SNOOZE_ZONE,
        handle_snooze,
        vol.Schema(
            {
                vol.Required(ATTR_ZONE): str,
                vol.Required(ATTR_DURATION_MINUTES): vol.All(
                    int, vol.Range(min=1, max=1440)
                ),
            }
        ),
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_CLEAR_TASKS,
        handle_clear_tasks,
        vol.Schema({vol.Required(ATTR_ZONE): str}),
    )
