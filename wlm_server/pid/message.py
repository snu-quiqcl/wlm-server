"""Module for message queue from request handler to PID handler."""

import dataclasses
import enum
import queue
from typing import Any

class ActionType(enum.Enum):
    """Action type."""
    CLOSE = 'close'


@dataclasses.dataclass
class PidMessageInfo:
    """PID message info.
    
    Fields:
        action: Action type.
        data: Additional arguments for action.

    Actions:
        CLOSE: Close all the DAC connections.
          data: None.
    """
    action: ActionType
    data: dict[str, Any] | None

class PidMessageQueue:
    """Thread-safe message queue from request handler to PID handler."""

    def __init__(self):
        self._queue = queue.Queue()

    def push(self, message: PidMessageInfo):
        """Pushes the given message to the message queue.
        
        Args:
            message: Message info.
        """
        self._queue.put(message)

    def pop(self) -> PidMessageInfo | None:
        """Pops the oldest message from the message queue.
        
        Returns:
            The oldest message. If there are no remaining messages, it returns None.
        """
        try:
            dac_control = self._queue.get_nowait()
        except queue.Empty:
            return None
        return dac_control

    def clear(self):
        """Clears the message queue."""
        self._queue = queue.Queue()
