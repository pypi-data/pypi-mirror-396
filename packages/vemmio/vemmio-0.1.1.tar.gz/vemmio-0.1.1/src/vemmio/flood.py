"""Vemmio Motion Device Class."""

import json
import logging

from .api import VemmioHttpRestApi, VemmioWebsocketApi
from .capability import CAPABILITY_TYPES, Capability, FloodCapability
from .device import Device, DeviceModel
from .models import FloodDetectorStatusModel

logger = logging.getLogger(__name__)


class FloodDevice(Device):
    """Class representing a Vemmio Flood Device."""

    def __init__(
        self,
        model: DeviceModel,
        api: VemmioHttpRestApi,
        websocket_api: VemmioWebsocketApi,
    ) -> None:
        """Initialize the FloodDevice object."""
        super().__init__(model, api, websocket_api)

        self._flood_capability = None
        self._status_model: FloodDetectorStatusModel = None

        # Get switch capabilities and store them separately
        for capability in self.capabilities:
            if isinstance(capability, FloodCapability):
                self._flood_capability = capability

    async def get_status(self) -> None:
        """Get the status of the flood device."""
        try:
            status_response = await self.api.get_status()
            if not self._status_model:
                self._status_model = FloodDetectorStatusModel()
            self._status_model.update_from_dict(json.loads(status_response))
            logger.debug("Flood status model updated: %s", self._status_model)

        except Exception as e:
            logger.error("Error getting status: %s", e)

    def get_flood_status_state(self) -> bool | None:
        """Get the last known flood status state."""
        if self._status_model is not None:
            return self._status_model.flood.state == "flood"
        return None

    def get_flood_status_timestamp(self) -> int | None:
        """Get the last known flood status timestamp."""
        if self._status_model is not None:
            return self._status_model.flood.timestamp
        return None

    def _websocket_callback(self, data: dict) -> None:
        """Handle websocket updates for the flood detector device."""
        logger.debug("Received websocket update for flood detector device: %s", data)
        self._status_model.update_from_dict(data)
        super()._websocket_callback(data)
