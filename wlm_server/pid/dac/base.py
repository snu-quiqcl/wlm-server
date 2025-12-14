"""Module for base class of DAC devices."""

from abc import ABC, abstractmethod

class BaseDAC(ABC):
    """Base class for DAC devices.

    Each DAC is associated with a single communication port (e.g. 'COM4').
    The only required high-level operation is: set a voltage on a given channel.
    """

    def __init__(self, port: str):
        """
        Args:
            port: See port property.
        """
        self._port = port
        self._is_open: bool = False

    @property
    def port(self) -> str:
        """Communication port identifier, e.g. 'COM4'."""
        return self._port

    @property
    def is_open(self) -> bool:
        """Whether the DAC connection is open."""
        return self._is_open

    @abstractmethod
    def open(self):
        """Opens the DAC connection."""
        self._is_open = True

    @abstractmethod
    def close(self):
        """Closes the DAC connection."""
        self._is_open = False

    @abstractmethod
    def set_voltage(self, channel: int, voltage: float):
        """Sets the voltage on the target channel.

        Args:
            channel: Target channel.
            voltage: Target voltage in V.
        """
        raise NotImplementedError
