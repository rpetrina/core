"""The aquacomputer integration."""
from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.components.aquacomputer.aquacomputer import (
    Aquacomputer,
    AquacomputerError,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DEFAULT_SYNC_TIME_S, DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]
SCAN_INTERVAL = timedelta(seconds=DEFAULT_SYNC_TIME_S)
DEVICEKEYS = ["31fe7d75-af10-452c-873c-c1b6e51e7d94"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up aquacomputer from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    aquacomputer_session = Aquacomputer(async_get_clientsession(hass), DEVICEKEYS)

    async def _update_method():
        """Get the latest data from Aquacomputer."""
        try:
            return await aquacomputer_session.update_devices()
        except AquacomputerError as err:
            raise UpdateFailed(f"Unable to fetch data: {err}") from err

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN,
        update_method=_update_method,
        update_interval=SCAN_INTERVAL,
    )
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    hass.config_entries.async_setup_platforms(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
