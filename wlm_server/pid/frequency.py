"""Module for frequency queue from task handler to PID handler."""

import dataclasses
import queue

@dataclasses.dataclass
class FrequencyInfo:
    """Frequency info.
    
    Fields:
        channel: Target channel
        frequency: Measured frequency in Hz.
    """
    channel: int
    frequency: float


class FrequencyQueue:
    """Thread-safe frequency queue from task handler to PID handler."""

    def __init__(self):
        self._queue = queue.Queue()

    def push(self, frequency: FrequencyInfo):
        """Pushes the given frequency to the frequency queue.
        
        Args:
            frequency: Frequency info.
        """
        self._queue.put(frequency)

    def pop(self) -> FrequencyInfo | None:
        """Pops the oldest frequency from the frequency queue.
        
        Returns:
            The oldest frequency. If there are no remaining frequencies, it returns None.
        """
        try:
            frequency = self._queue.get_nowait()
        except queue.Empty:
            return None
        return frequency

    def clear(self):
        """Clears the frequency queue."""
        self._queue = queue.Queue()
