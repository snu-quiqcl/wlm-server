"""Module for prioritized measurement queue."""

import dataclasses
from datetime import timedelta

@dataclasses.dataclass
class MeasureInfo:
    """Measurement info.
    
    Fields:
        channel: Target channel.
        deadline: Measurement deadline.
    """
    channel: int
    deadline: timedelta
