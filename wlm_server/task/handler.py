"""Module for task handler with WLM."""

import ctypes
import logging
import time
import threading
import json
from collections import defaultdict
from datetime import timedelta
from typing import Any

from django.utils import timezone
from django.conf import settings
from pylablib.devices.HighFinesse.wlm import WLM
from pylablib.devices.HighFinesse.wlmData_defs import ESignal
from camel_converter import dict_to_camel

from config.models import Config
from setting.models import Setting
from measurement.models import Measurement
from pid.frequency import FrequencyInfo
from utils import util
from .message import ActionType, MessageQueue
from .measure import MeasureInfo, MeasureQueue

MEASUREMENT_SLICE_SECONDS = 0.5
IDLE_SLEEP_SECONDS = 0.01
# Interferometer pattern (fringes on the CCD) of each channel.
PATTERN_INDEX = ESignal.cSignal1Interferometers
PATTERN_ENABLE = 1  # cPatternEnable in wlmData.h.
PATTERN_INTERVAL_SECONDS = 0.5
PATTERN_ITEM_TYPES = {2: ctypes.c_int16, 4: ctypes.c_int32}

logger = logging.getLogger(__name__)


class TaskHandler(threading.Thread):  # pylint: disable=too-many-instance-attributes
    """Task handler for controlling and monitoring WLM.
    
    Workflow:
        1. Check if there are remaining messages in message queue. If so, perform all tasks.
        2. Get the most prioritized measurement from measurement queue.
        3. Perform the measurement and record the result.
        4. Repeat steps 2 and 3 for measurement slice.
        5. Notify all results to request handlers.
        6. Repeat steps 1 through 5.
    """

    def __init__(self):
        super().__init__()
        self.daemon = True
        self._wlm: WLM
        self._message_queue: MessageQueue = settings.MESSAGE_QUEUE
        self._measure_queue: MeasureQueue = MeasureQueue()
        self._channel_to_setting: dict[int, Setting] = {}
        self._active_channel: int | None = None
        self._is_pattern_enabled = False
        self._channel_to_pattern_time: dict[int, float] = {}
        self._connect_wlm()

    def _connect_wlm(self):
        config = Config.objects.first()
        self._wlm = WLM(config.wlm_version, config.wlm_dll_path, config.wlm_app_path)
        self._wlm.open()
        self._wlm.set_read_mode('single')
        self._enable_pattern()

    def _enable_pattern(self):
        """Makes the WLM export the interferometer pattern.

        Pattern export is optional, so a failure only disables the pattern notification.
        """
        try:
            self._wlm.lib.lib.SetPattern(PATTERN_INDEX, PATTERN_ENABLE)
        except (AttributeError, OSError):
            logger.exception('Failed to enable the interferometer pattern export.')
            return
        self._is_pattern_enabled = True

    def _read_pattern(self, channel: int) -> list[int] | None:
        """Reads the latest interferometer pattern of the given channel.

        Args:
            channel: Target channel.

        Returns:
            Pattern intensities in CCD pixel order. If the pattern is not available, it returns
              None.
        """
        lib = self._wlm.lib.lib
        try:
            count = lib.GetPatternItemCount(PATTERN_INDEX)
            item_type = PATTERN_ITEM_TYPES.get(lib.GetPatternItemSize(PATTERN_INDEX))
            if count <= 0 or item_type is None:
                return None
            buffer = (item_type * count)()
            lib.GetPatternDataNum(channel, PATTERN_INDEX, ctypes.addressof(buffer))
        except (AttributeError, OSError):
            logger.exception('Failed to read the interferometer pattern; it is disabled.')
            self._is_pattern_enabled = False
            return None
        return list(buffer)

    def _is_pattern_due(self, channel: int) -> bool:
        if not self._is_pattern_enabled:
            return False
        last_time = self._channel_to_pattern_time.get(channel)
        return last_time is None or time.monotonic() - last_time >= PATTERN_INTERVAL_SECONDS

    def _close_wlm(self):
        self._wlm.close()

    def _start_wlm(self, channel: int):
        self._switch(channel)
        self._wlm.start_measurement()

    def _stop_wlm(self):
        self._wlm.stop_measurement()

    def _start_channel_measurement(self, channel: int):
        measure = MeasureInfo(channel, timezone.now())
        self._measure_queue.push(measure)

    def _stop_channel_measurement(self, channel: int):
        self._measure_queue.remove(channel)

    def _set_channel_exposure(self, channel: int, exposure: timedelta):
        self._wlm.set_exposure(exposure=exposure.total_seconds(), channel=channel)

    def _switch(self, channel: int):
        if channel != self._active_channel:
            self._wlm.set_active_channel(channel=channel)
            self._active_channel = channel

    def _measure_channel(self, channel: int) -> dict[str, Any]:
        frequency_or_error = self._wlm.get_frequency(
            channel=channel, error_on_invalid=False, wait=True, timeout=3)
        setting = self._channel_to_setting[channel]
        deadline = timezone.now() + setting.period
        next_measure = MeasureInfo(channel, deadline)
        self._measure_queue.push(next_measure)
        measurement = {'frequency': None, 'error': None}
        if isinstance(frequency_or_error, float):
            measure_record = Measurement(setting=setting, frequency=frequency_or_error)
            measurement['frequency'] = frequency_or_error
            pid_operation = settings.CHANNEL_CACHE.get_pid_operation(channel)
            if pid_operation is not None:
                settings.FREQUENCY_QUEUE.push(
                    FrequencyInfo(channel, frequency_or_error, time.monotonic()))
        else:
            measure_record = Measurement(setting=setting, error=frequency_or_error)
            measurement['error'] = frequency_or_error
        measure_record.save()
        measurement['measured_at'] = measure_record.measured_at.isoformat()
        return dict_to_camel(measurement)

    def _calibrate(self, channel: int, frequency: float):
        self._wlm.calibrate(source_type='other', source_frequency=frequency, channel=channel)

    def run(self):  # pylint: disable=too-many-locals
        while True:
            while (message := self._message_queue.pop()) is not None:
                channel = message.channel
                data = message.data
                match message.action:
                    case ActionType.CLOSE:
                        self._close_wlm()
                        return
                    case ActionType.START:
                        self._start_wlm(channel)
                    case ActionType.STOP:
                        self._stop_wlm()
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
                    case ActionType.CALIB:
                        self._calibrate(channel, data['freq'])
            measurements: dict[int, list] = defaultdict(list)  # {channel: [measurement]}
            patterns: dict[int, dict[str, Any]] = {}  # {channel: latest pattern}
            measurement_slice_deadline = time.monotonic() + MEASUREMENT_SLICE_SECONDS
            while time.monotonic() < measurement_slice_deadline:
                measure = self._measure_queue.pop()
                if measure is None:
                    time.sleep(IDLE_SLEEP_SECONDS)
                    continue
                channel = measure.channel
                self._switch(channel)
                measurement = self._measure_channel(channel)
                measurements[channel].append(measurement)
                if self._is_pattern_due(channel):
                    self._channel_to_pattern_time[channel] = time.monotonic()
                    pattern = self._read_pattern(channel)
                    if pattern is not None:
                        patterns[channel] = {'pattern': pattern,
                                             'measuredAt': measurement['measuredAt']}
            for channel, channel_measurements in measurements.items():
                util.group_send_from_thread(
                    f'channel_{channel}_measurement',
                    {'type': 'notify', 'message': json.dumps(channel_measurements)}
                )
            for channel, pattern in patterns.items():
                util.group_send_from_thread(
                    f'channel_{channel}_pattern',
                    {'type': 'notify', 'message': json.dumps(pattern)}
                )
