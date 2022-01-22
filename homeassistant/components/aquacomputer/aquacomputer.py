"""Support for Aquacomputer sensors."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
import logging

from aiohttp import ClientError
import async_timeout

_LOGGER = logging.getLogger(__name__)

API_URL = "https://aquasuite.aquacomputer.de/json/"
TIMEOUT = 10


@dataclass
class AquacomputerDevice:
    """Aquacomputer device."""

    device_id: str
    sensors: dict[str, dict]

    @classmethod
    def init_from_response(cls, response):
        """Class method."""
        sensors_data = response.get("s")
        sensors_dict = {}
        for sensor_data in sensors_data:
            sensors_dict[sensor_data["i"]] = sensor_data
        return cls(response.get("g"), sensors_dict)

    @property
    def sensor_types(self):
        """Sensor types."""
        return self.sensors


class AquacomputerError(Exception):
    """General Aquacomputer exception occurred."""


class AquacomputerConnectionError(AquacomputerError):
    """ConnectionError Airthings occurred."""


class AquacomputerAuthError(AquacomputerError):
    """AirthingsAuthError Airthings occurred."""


class Aquacomputer:
    """Aquacomputer data handler."""

    def __init__(self, websession, devicekey):
        """Init Aquacomputer data handler."""
        self._websession = websession
        self.devicekey = devicekey
        self._devices = []

    async def update_devices(self):
        """Update data."""
        _LOGGER.debug("In aquacomputer update_devices")
        if not self._devices:
            _LOGGER.debug(f"Devicekey: {self.devicekey}")
            response = await self._request(API_URL + self.devicekey)
            json_data = await response.json(content_type="text/html")
            self._devices.append(AquacomputerDevice.init_from_response(json_data))

        res = {}
        for device in self._devices:
            if not device.sensors:
                response = await self._request(API_URL + device.device_id)
                json_data = await response.json(content_type="text/html")
                device.sensors = json_data.get("s")
            res[device.device_id] = device
        return res

    async def _request(self, url, json_data=None, retry=3):
        _LOGGER.debug("Request %s %s, %s", url, retry, json_data)

        try:
            async with async_timeout.timeout(TIMEOUT):
                if json_data:
                    response = await self._websession.post(url, json=json_data)
                else:
                    response = await self._websession.get(url)
            if response.status != 200:
                if retry > 0 and response.status != 429:
                    return await self._request(url, json_data, retry=retry - 1)
                _LOGGER.error(
                    "Error connecting to Aquacomputer, response: %s %s",
                    response.status,
                    response.reason,
                )
                raise AquacomputerError(
                    f"Error connecting to Aquacomputer, response: {response.reason}"
                )
        except ClientError as err:
            _LOGGER.error("Error connecting to Aquacomputer: %s ", err, exc_info=True)
            raise AquacomputerError from err
        except asyncio.TimeoutError as err:
            if retry > 0:
                return await self._request(url, json_data, retry=retry - 1)
            _LOGGER.error("Timed out when connecting to Aquacomputer")
            raise AquacomputerError from err
        return response
