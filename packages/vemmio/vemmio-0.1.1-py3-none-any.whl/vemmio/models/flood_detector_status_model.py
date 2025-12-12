"""Module holding FloodDetectorStatusModel dataclass."""

from dataclasses import dataclass, field
from typing import Any

from mashumaro import field_options

from .base_model import BaseModel


@dataclass(kw_only=True)
class FloodState(BaseModel):
    """Enum holding relay states."""

    state: str = field(default="clear", metadata=field_options(alias="state"))

    timestamp: int = field(default=0, metadata=field_options(alias="timestamp"))


@dataclass(kw_only=True)
class FloodDetectorStatusModel(BaseModel):
    """Object holding status information from Flood Detector Vemmio device."""

    flood: FloodState = field(
        default_factory=FloodState, metadata=field_options(alias="flood")
    )

    def update_from_dict(self, data: dict[str, Any]) -> "FloodDetectorStatusModel":
        """Return FloodDetectorStatusModel object from Vemmio API response.

        Args:
        ----
            data: Update the device object with the data received from a
                Vemmio device API.

        Returns:
        -------
            The updated MotionStatusModel object.

        """

        if _flood := data.get("flood"):
            self.flood = FloodState.from_dict(_flood)

        return self
