"""Module for message queue from request handler to task handler."""

import dataclasses
import enum

class ActionType(enum.Enum):
    """Action type."""
    OPERATE = "operate"
    EXPOSURE = "exposure"
    PERIOD = "period"


@dataclasses.dataclass
class MessageInfo:
    """Message info."""


class messageQueue:
    """Thread-safe message queue from request handler to task handler."""
