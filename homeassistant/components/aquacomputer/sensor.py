"""Platform for sensor integration."""
from __future__ import annotations

from homeassistant.components.aquacomputer.aquacomputer import AquacomputerDevice
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import TEMP_CELSIUS
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType, StateType
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN

SENSORS: dict[str, SensorEntityDescription] = {
    "temp": SensorEntityDescription(
        key="temp",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=TEMP_CELSIUS,
        name="Temperature",
    ),
    "flow_rate": SensorEntityDescription(
        key="flow_rate",
        device_class="Flow Rate",
        native_unit_of_measurement="L/h",
        name="Flow Rate",
    ),
    "water_quality": SensorEntityDescription(
        key="water_quality",
        device_class="Coolant Quality",
        native_unit_of_measurement="%",
        name="Coolant Quality",
    ),
}


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the sensor platform."""
    add_entities([ExampleSensor()])


class ExampleSensor(SensorEntity):
    """Representation of a Sensor."""

    _attr_name = "Example Temperature"
    _attr_native_unit_of_measurement = TEMP_CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT

    def update(self) -> None:
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        self._attr_native_value = 23


# async def async_setup_entry(
#     hass: HomeAssistant,
#     entry: ConfigEntry,
#     async_add_entities: AddEntitiesCallback,
# ) -> None:
#     """Set up the Airthings sensor."""

#     coordinator: DataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
#     entities = [
#         AirthingsHeaterEnergySensor(
#             coordinator,
#             airthings_device,
#             SENSORS[sensor_types],
#         )
#         for airthings_device in coordinator.data.values()
#         for sensor_types in airthings_device.sensor_types
#         if sensor_types in SENSORS
#     ]
#     async_add_entities(entities)


class AirthingsHeaterEnergySensor(CoordinatorEntity, SensorEntity):
    """Representation of a Aquacomputer Sensor device."""

    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        airthings_device: AquacomputerDevice,
        entity_description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)

        self.entity_description = entity_description

        self._attr_unique_id = f"{airthings_device.device_id}_{entity_description.key}"
        self._id = airthings_device.device_id
        self._attr_device_info = DeviceInfo(
            configuration_url="https://dashboard.airthings.com/",
            identifiers={(DOMAIN, airthings_device.device_id)},
            manufacturer="Airthings",
        )

    @property
    def native_value(self) -> StateType:
        """Return the value reported by the sensor."""
        return self.coordinator.data[self._id].sensors[self.entity_description.key]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Airthings sensor."""

    coordinator: DataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [
        AirthingsHeaterEnergySensor(
            coordinator,
            airthings_device,
            SENSORS[sensor_types],
        )
        for airthings_device in coordinator.data.values()
        for sensor_types in airthings_device.sensor_types
        if sensor_types in SENSORS
    ]
    async_add_entities(entities)
