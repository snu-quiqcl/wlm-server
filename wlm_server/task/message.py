"""Module for message queue from request handler to task handler."""

import dataclasses
import enum
import queue
from typing import Any

class ActionType(enum.Enum):
    """Action type."""
    CLOSE = 'close'
    OPERATE = 'operate'
    EXPOSURE = 'exposure'
    PERIOD = 'period'


@dataclasses.dataclass
class MessageInfo:
    """Message info.
    
    Fields:
        action: Action type.
        channel: Target channel. If None, it targets WLM.
        data: Additional arguments for action.

    Actions:
        CLOSE: Close the WLM connection.
          channel: None.
          data: None.
        OPERATE:
          channel: Target channel.
          data:
            on (bool): If True, start measurement of the given channel. Otherwise, stop measurement
              of the given channel.
        EXPOSURE:
          channel: Target channel.
          data:
            exposure (datetime.timedelta): New exposure time.
        PERIOD:
          channel: Target channel.
          data:
            period (datetime.timedelta): New period.
    """
    action: ActionType
    channel: int | None
    data: dict[str, Any] | None


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
        except queue.Empty:
            return None
        else:
            return message

    def clear(self):
        """Clears the message queue."""
        self._queue = queue.Queue()


messageQueue = MessageQueue()
