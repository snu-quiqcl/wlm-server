"""Module for message queue from request handler to task handler."""

import dataclasses
import enum
import queue
from typing import Any

class ActionType(enum.Enum):
    """Action type."""
    OPERATE = "operate"
    EXPOSURE = "exposure"
    PERIOD = "period"


@dataclasses.dataclass
class MessageInfo:
    """Message info.
    
    Fields:
        action: Action type.
        channel: Target channel. If None, it targets WLM.
        data: Additional arguments for action. The arguments required for each action type are as follows.
          OPERATE:
            on (bool): If True, start measurement. Otherwise, stop measurement.
          EXPOSURE:
            exposure (datetime.timedelta): New exposure time.
          PERIOD:
            period (datetime.timedelta): New period.
    """
    action: ActionType
    channel: int | None
    data: dict[str, Any]


class MessageQueue:
    """Thread-safe message queue from request handler to task handler."""

    def __init__(self):
        self._queue = queue.Queue()

    def push(self, message: MessageInfo):
        """Pushes the given message to the message queue.
        
        Args:
            message: Message info.
        """
        self._queue.put(message)

    def pop(self) -> MessageInfo | None:
        """Pops the oldest message from the message queue.
        
        Returns:
            The oldest message. If there are no remaining messages, it returns None.
        """
        try:
            message = self._queue.get_nowait()
            return message
        except queue.Empty:
            return None

    def clear(self):
        """Clears the message queue."""
        self._queue = queue.Queue()


messageQueue = MessageQueue()
