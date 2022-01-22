"""Platform for sensor integration."""
from __future__ import annotations

from typing import Any

from homeassistant.components.aquacomputer.aquacomputer import AquacomputerDevice
from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN, SENSOR_IDS_TO_UNITS_MAP


def _sensor_setup(sensor: dict[str, Any]):
    key = sensor["i"]
    name = sensor["n"]
    sensor_units = SENSOR_IDS_TO_UNITS_MAP.get(sensor["u"])
    # Determine the units for the sensor
    native_unit_of_measurement = sensor_units[0] if sensor_units else None
    device_class = sensor_units[1] if sensor_units else None
    return SensorEntityDescription(
        key=key,
        device_class=device_class,
        native_unit_of_measurement=native_unit_of_measurement,
        name=name,
    )


class AquacomputerDeviceSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Aquacomputer Sensor device."""

    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        aquacomputer_device: AquacomputerDevice,
        entity_description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)

        self.entity_description = entity_description

        self._attr_unique_id = (
            f"{aquacomputer_device.device_id}_{entity_description.key}"
        )
        self._id = aquacomputer_device.device_id
        self._attr_device_info = DeviceInfo(
            configuration_url="https://aquasuite.aquacomputer.de/",
            identifiers={(DOMAIN, aquacomputer_device.device_id)},
            manufacturer="Aquacomputer",
        )

    @property
    def native_value(self) -> StateType:
        """Return the value reported by the sensor."""
        return self.coordinator.data[self._id].sensors[self.entity_description.key]["v"]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Aquacomputer sensors."""

    coordinator: DataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [
        AquacomputerDeviceSensor(
            coordinator,
            aquacomputer_device,
            _sensor_setup(sensor_type),
        )
        for aquacomputer_device in coordinator.data.values()
        for sensor_type in aquacomputer_device.sensor_types
    ]
    async_add_entities(entities)
