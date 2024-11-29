"""Module for task handler with WLM."""

import threading
import json
from datetime import datetime, timedelta

from django.conf import settings
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from pylablib.devices.HighFinesse.wlm import WLM

from config.models import Config
from setting.models import Setting
from measurement.models import Measurement
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
        self.daemon = True
        self._wlm: WLM
        self._message_queue: MessageQueue = settings.MESSAGE_QUEUE
        self._measure_queue: MeasureQueue = MeasureQueue()
        self._channel_to_setting: dict[int, Setting] = {}
        self._active_channel: int | None = None
        self._connect_wlm()

    def _connect_wlm(self):
        config = Config.objects.first()
        self._wlm = WLM(config.wlm_version, config.wlm_dll_path, config.wlm_app_path)
        self._wlm.open()
        self._wlm.set_read_mode('single')

    def _start_wlm(self, channel: int):
        self._switch(channel)
        self._wlm.start_measurement()

    def _stop_wlm(self):
        self._wlm.stop_measurement()
        self._wlm.close()

    def _start_channel_measurement(self, channel: int):
        measure = MeasureInfo(channel, datetime.now())
        self._measure_queue.push(measure)

    def _stop_channel_measurement(self, channel: int):
        self._measure_queue.remove(channel)

    def _set_channel_exposure(self, channel: int, exposure: timedelta):
        self._wlm.set_exposure(exposure=exposure.total_seconds(), channel=channel)

    def _switch(self, channel: int):
        if channel != self._active_channel:
            self._wlm.set_active_channel(channel=channel)
            self._active_channel = channel

    def run(self):
        while True:
            while (message := self._message_queue.pop()) is not None:
                channel = message.channel
                data = message.data
                match message.action:
                    case ActionType.START:
                        self._start_wlm(channel)
                    case ActionType.STOP:
                        self._stop_wlm()
                        return
                    case ActionType.OPERATE:
                        on = data['on']
                        if on:
                            self._start_channel_measurement(channel)
                        else:
                            self._stop_channel_measurement(channel)
                    case ActionType.SETTING:
                        setting = data['setting']
                        if data['update_exposure']:
                            self._set_channel_exposure(channel, setting.exposure)
                        self._channel_to_setting[channel] = setting
            measure = self._measure_queue.pop()
            if measure is None:
                continue
            channel = measure.channel
            self._switch(channel)
            frequency_or_error = self._wlm.get_frequency(
                channel=channel, error_on_invalid=False, wait=True, timeout=3)
            setting = self._channel_to_setting[channel]
            deadline = datetime.now() + setting.period
            next_measure = MeasureInfo(channel, deadline)
            self._measure_queue.push(next_measure)
            notif = {}
            if isinstance(frequency_or_error, float):
                measure_record = Measurement(setting=setting, frequency=frequency_or_error)
                notif['frequency'] = frequency_or_error
            else:
                measure_record = Measurement(setting=setting, error=frequency_or_error)
                notif['error'] = frequency_or_error
            measure_record.save()
            notif['measured_at'] = measure_record.measured_at.isoformat()
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'channel_{channel}_measurement',
                {'type': 'notify', 'message': json.dumps(notif)}
            )
