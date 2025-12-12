"""Vemmio API interface definition."""

from abc import ABC, abstractmethod
from typing import Any


class VemmioApiInterface(ABC):
    """Abstract interface for Vemmio API implementations."""

    @abstractmethod
    async def get_status(self) -> dict[str, Any]:
        """Get device information."""

    @abstractmethod
    async def enable_home_assistant_integration(self) -> None:
        """Enable Home Assistant integration on the device."""

    @abstractmethod
    async def disable_home_assistant_integration(self) -> None:
        """Disable Home Assistant integration on the device."""
