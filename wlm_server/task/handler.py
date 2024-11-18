"""Module for task handler with WLM."""

import threading
from datetime import timedelta

from django.conf import settings
from pylablib.devices.HighFinesse.wlm import WLM

from config.models import Config
from .message import MessageQueue
from .measure import MeasureQueue

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
        self._wlm: WLM
        self._message_queue: MessageQueue = settings.MESSAGE_QUEUE
        self._measure_queue: MeasureQueue = MeasureQueue()
        self._channel_to_period: dict[int, timedelta] = {}
        self._open_connection()

    def _open_connection(self):
        config = Config.objects.first()
        wlm_version = config.wlm_version
        wlm_dll_path = config.wlm_dll_path
        wlm_app_path = config.wlm_app_path
        self._wlm = WLM(wlm_version, wlm_dll_path, wlm_app_path)
        self._wlm.open()

    def run(self):
        while True:
            while (message := self._message_queue.pop()) is not None:  # pylint: disable=unused-variable
                pass
            measure = self._measure_queue.pop()  # pylint: disable=unused-variable
