"""Support for Aquacomputer sensors."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
import logging
from typing import Any

from aiohttp import ClientError
import async_timeout

_LOGGER = logging.getLogger(__name__)

API_URL = "https://aquasuite.aquacomputer.de/json/"
TIMEOUT = 10


@dataclass
class AquacomputerDevice:
    """Aquacomputer device."""

    device_id: str
    # device_type: str
    # name: str
    sensors: list[dict[str, Any | None]]
    # is_active: bool

    @classmethod
    def init_from_response(cls, response):
        """Class method."""
        return cls(
            response.get("g"),
            # response.get("deviceType"),
            # response.get("segment").get("name"),
            {sensor: None for sensor in response.get("s")},
            # response.get("segment").get("isActive"),
        )

    @property
    def sensor_types(self):
        """Sensor types."""
        return [item.keys() for item in self.sensors]


class AquacomputerError(Exception):
    """General Aquacomputer exception occurred."""


class AquacomputerConnectionError(AquacomputerError):
    """ConnectionError Airthings occurred."""


class AquacomputerAuthError(AquacomputerError):
    """AirthingsAuthError Airthings occurred."""


class Aquacomputer:
    """Aquacomputer data handler."""

    def __init__(self, websession, devicekeys):
        """Init Aquacomputer data handler."""
        self._websession = websession
        self.devicekeys = devicekeys
        self._devices = []

    async def update_devices(self):
        """Update data."""
        if not self._devices:
            for devicekey in self.devicekeys:
                response = await self._request(API_URL + devicekey)
                json_data = await response.json()
                self._devices.append(AquacomputerDevice.init_from_response(json_data))

        res = {}
        for device in self._devices:
            if not device.sensors:
                response = await self._request(API_URL + device.device_id)
                json_data = await response.json()
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
