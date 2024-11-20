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
        self._queue: list[tuple[datetime, MeasureInfo]] = []

    def push(self, measure: MeasureInfo):
        """Pushes the given measurement to the measurement queue.
        
        Args:
            measure: Measurement info.
        """
        priority = measure.deadline
        heapq.heappush(self._queue, (priority, measure))

    def pop(self) -> MeasureInfo | None:
        """Pops the measurement with the earliest deadline from the measurement queue.

        Returns:
            The measurement with the earliest deadline. If there are no scheduled measurements, it
              returns None.
        """
        try:
            item = heapq.heappop(self._queue)
        except IndexError:
            return None
        return item[1]

    def remove(self, channel: int):
        """Removes the measurement of the given channel from the measurement queue.
        
        Args:
            channel: Target channel.
        """
        self._queue = [item for item in self._queue if item[1].channel != channel]
        heapq.heapify(self._queue)
