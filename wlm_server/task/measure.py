"""Module for prioritized measurement queue."""

import dataclasses
import heapq
from datetime import datetime

@dataclasses.dataclass
class MeasureInfo:
    """Measurement info.
    
    Fields:
        channel: Target channel.
        deadline: Measurement deadline.
    """
    channel: int
    deadline: datetime


class MeasureQueue:
    """Prioritized measurement queue based on deadlines."""

    def __init__(self):
        self._queue = []

    def push(self, measure: MeasureInfo):
        """Pushes the given measurement to the measurement queue.
        
        Args:
            measure: Measurement info.
        """
        priority = measure.deadline
        heapq.heappush(self._queue, (priority, measure))

    def pop(self) -> MeasureInfo | None:
        """Pops the measurement with the earlist deadline from the measurement queue.

        Returns:
            The measurement with the earlist deadline. If there are no scheduled measurements, it
              returns None.
        """
        try:
            item = heapq.heappop(self._queue)
            return item[1]
        except IndexError:
            return None
