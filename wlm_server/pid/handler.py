"""Module for PID handler with DAC."""

import time
import threading
import json

from django.conf import settings
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from channel.models import Channel
from pid_setting.models import PidSetting
from .dac_control import DacControlQueue
from .message import ActionType, PidMessageQueue

class PidHandler(threading.Thread):
    """PID handler for configuring and running feedback control on WLM channels."""

    def __init__(self):
        super().__init__()
        self.daemon = True
        self._message_queue: PidMessageQueue = settings.PID_MESSAGE_QUEUE
        self._dac_control_queue: DacControlQueue = settings.DAC_CONTROL_QUEUE
        # {channel: (backend_alias, port, dac_channel)}
        self._channel_to_dac_info: dict[int, tuple[str, str, int]] = {}
        # {channel: pid_enabled}
        self._channel_to_pid_enabled: dict[int, bool] = {}
        # {channel: pid_setting}
        self._channel_to_pid_setting: dict[int, PidSetting] = {}
        self._dac_control_slice_seconds = 0.5

    def _get_dac_info(self, ch: int) -> tuple[str, str, int]:
        """Gets the DAC information for the given channel.
        
        Args:
            ch: Target WLM channel.
        
        Returns:
            Tuple of (backend_alias, port, dac_channel).
        """
        if ch not in self._channel_to_dac_info:
            channel = Channel.objects.get(channel=ch)
            dac_device = channel.dac_device
            dac_channel = channel.dac_channel
            self._channel_to_dac_info[ch] = (dac_device.backend, dac_device.port, dac_channel)
        return self._channel_to_dac_info[ch]

    def _set_dac_voltage(self, channel: int, voltage: float):
        """Sets the voltage for the given channel.
        
        Args:
            channel: Target WLM channel.
            voltage: Target voltage in V.
        """
        backend_alias, port, dac_channel = self._get_dac_info(channel)
        dac = settings.DAC_MANAGER.get_or_open(backend_alias, port)
        dac.set_voltage(dac_channel, voltage)
        settings.CHANNEL_CACHE.set_dac_voltage(channel, voltage)

    def run(self):
        while True:
            while (message := self._message_queue.pop()) is not None:
                data = message.data
                match message.action:
                    case ActionType.CLOSE:
                        settings.DAC_MANAGER.close_all()
                        return
                    case ActionType.ON:
                        self._channel_to_pid_enabled[data['channel']] = True
                    case ActionType.OFF:
                        self._channel_to_pid_enabled[data['channel']] = False
                    case ActionType.SETTING:
                        self._channel_to_pid_setting[data['channel']] = data['pid_setting']
            # DAC control
            latest_commands: dict[int, float] = {}
            dac_control_slice_deadline = time.monotonic() + self._dac_control_slice_seconds
            while time.monotonic() < dac_control_slice_deadline:
                dac_control = self._dac_control_queue.pop()
                if dac_control is None:
                    continue
                if self._channel_to_pid_enabled.get(dac_control.channel, False):
                    continue
                latest_commands[dac_control.channel] = dac_control.voltage
            for channel, voltage in latest_commands.items():
                self._set_dac_voltage(channel, voltage)
            channel_layer = get_channel_layer()
            for channel in latest_commands:
                voltage = settings.CHANNEL_CACHE.get_dac_voltage(channel)
                async_to_sync(channel_layer.group_send)(
                    f'channel_{channel}_dac_output',
                    {'type': 'notify', 'message': json.dumps({'voltage': voltage})}
                )
