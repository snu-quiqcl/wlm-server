"""Module for task handler with WLM."""

import threading
from datetime import timedelta

from .measure import MeasureQueue
from .message import messageQueue

class TaskHandler(threading.Thread):
    """Task handler for controlling and monitoring WLM.
    
    Workflow:
        1. Check if there are remaining messages in message queue. If so, perform all tasks.
        2. Get the most prioritized measurement from measurement queue.
        3. Perform the measurement and notify the result to request handler.
        4. Put the next measurement to measurement queue.
        5. Repeat steps 1 through 4.
    """

    def __init__(self):
        super().__init__()
        self._measure_queue: MeasureQueue = MeasureQueue()
        self._channel_to_period: dict[int, timedelta] = {}

    def run(self):
        while True:
            while (message := messageQueue.pop()) is not None:
                pass
            measure = messageQueue.pop()
