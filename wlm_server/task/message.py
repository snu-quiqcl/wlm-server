"""Module for message queue from request handler to task handler."""

import dataclasses
import enum
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


class messageQueue:
    """Thread-safe message queue from request handler to task handler."""
