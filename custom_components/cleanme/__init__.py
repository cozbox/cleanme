import logging
from . import dashboard as cleanme_dashboard

LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry):
    # Existing zone setup code...
    # Call the new dashboard update function
    await _update_dashboard(hass)

async def async_unload_entry(hass, entry):
    # Existing zone unload code...
    # Call the new dashboard update function when zones change
    await _update_dashboard(hass)

async def _update_dashboard(hass):
    try:
        cleanme_dashboard.generate_dashboard_config(hass)
        LOGGER.info('Dashboard updated successfully.')
    except Exception as e:
        LOGGER.error(f'Failed to update dashboard: {e}')

# Update _find_zone_by_name to check hasattr for name attribute
async def _find_zone_by_name(name):
    zone = ... # Existing code to find the zone
    if zone and hasattr(zone, 'name') and zone.name == name:
        return zone
    return None
