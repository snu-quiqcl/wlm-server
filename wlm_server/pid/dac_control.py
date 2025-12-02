"""Module for DAC control queue from request handler to PID handler."""

import dataclasses
import queue

@dataclasses.dataclass
class DacControlInfo:
    """DAC control info.
    
    Fields:
        channel: Target channel
        voltage: Target voltage in V.
    """
    channel: int
    voltage: float


class DacControlQueue:
    """Thread-safe DAC control queue from request handler to PID handler."""

    def __init__(self):
        self._queue = queue.Queue()

    def push(self, dac_control: DacControlInfo):
        """Pushes the given DAC control to the DAC control queue.
        
        Args:
            dac_control: DAC control info.
        """
        self._queue.put(dac_control)

    def pop(self) -> DacControlInfo | None:
        """Pops the oldest DAC control from the DAC control queue.
        
        Returns:
            The oldest DAC control. If there are no remaining DAC controls, it returns None.
        """
        try:
            dac_control = self._queue.get_nowait()
        except queue.Empty:
            return None
        return dac_control

    def clear(self):
        """Clears the DAC control queue."""
        self._queue = queue.Queue()
