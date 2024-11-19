"""Module for task handler with WLM."""

import threading
from datetime import datetime, timedelta

from django.conf import settings
from pylablib.devices.HighFinesse.wlm import WLM

from config.models import Config
from setting.models import Setting
from .message import ActionType, MessageQueue
from .measure import MeasureInfo, MeasureQueue

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
        self._wlm.start_measurement()

    def _close_connection(self):
        self._wlm.stop_measurement()
        self._wlm.close()

    def _start_channel_measurement(self, channel: int):
        setting = Setting.objects.filter(channel__name=channel).order_by('-created_at').first()
        period = setting.period
        self._channel_to_period[channel] = period
        deadline = datetime.now() + period
        measure = MeasureInfo(channel, deadline)
        self._measure_queue.push(measure)

    def _stop_channel_measurement(self, channel: int):
        self._measure_queue.remove(channel)

    def _set_channel_exposure(self, channel: int, exposure: timedelta):
        self._wlm.set_exposure(exposure=exposure.total_seconds(), channel=channel)

    def run(self):
        while True:
            while (message := self._message_queue.pop()) is not None:
                channel = message.channel
                data = message.data
                match message.action:
                    case ActionType.CLOSE:
                        self._close_connection()
                        return
                    case ActionType.OPERATE:
                        on = data['on']
                        if on:
                            self._start_channel_measurement(channel)
                        else:
                            self._stop_channel_measurement(channel)
                    case ActionType.EXPOSURE:
                        exposure = data['exposure']
                        self._set_channel_exposure(channel, exposure)
                    case ActionType.PERIOD:
                        period = data['period']
                        self._channel_to_period[channel] = period
            measure = self._measure_queue.pop()  # pylint: disable=unused-variable
