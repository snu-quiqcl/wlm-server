"""Module for message queue from request handler to task handler."""

import dataclasses
import enum
import queue
from typing import Any

class ActionType(enum.Enum):
    """Action type."""
    START = 'start'
    STOP = 'stop'
    OPERATE = 'operate'
    SETTING = 'setting'


@dataclasses.dataclass
class MessageInfo:
    """Message info.
    
    Fields:
        action: Action type.
        channel: Target channel. If None, it targets WLM.
        data: Additional arguments for action.

    Actions:
        START: Switch to the target channel and start the WLM measurement.
          channel: Target channel.
          data: None.
        STOP: Stop the WLM measurement and close the WLM connection.
          channel: None.
          data: None.
        OPERATE: Start or stop the measurement of a specific channel.
          channel: Target channel.
          data:
            on (bool): If True, start measurement of the given channel. Otherwise, stop measurement
              of the given channel.
        SETTING: Update the setting of a specific channel.
          channel: Target channel.
          data:
            setting (setting.models.Setting): New setting.
            update_exposure (bool): If True, update the exposure time in task handler.
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
        return message

    def clear(self):
        """Clears the message queue."""
        self._queue = queue.Queue()
