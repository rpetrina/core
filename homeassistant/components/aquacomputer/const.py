"""Constants for the aquacomputer integration."""

from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.const import PERCENTAGE, TEMP_CELSIUS

DEFAULT_SYNC_TIME_S = 30
DEVICE_NAME = "device_name"
DOMAIN = "aquacomputer"
SENSOR_IDS_TO_UNITS_MAP = {
    25: (PERCENTAGE, "Coolant Quality"),
    31: (TEMP_CELSIUS, SensorDeviceClass.TEMPERATURE),
    33: ("L/h", "Flow Rate"),
}
