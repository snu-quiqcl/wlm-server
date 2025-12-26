"""Module for PID handler with DAC."""

import time
import threading
import json

from django.conf import settings
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from channel.models import Channel
from pid_setting.models import PidSetting
from event.models import Event
from utils import util
from .dac_control import DacControlQueue
from .message import ActionType, PidMessageQueue

MAX_ERROR_THRESHOLD_HZ = 10e9

class PidHandler(threading.Thread):  # pylint: disable=too-many-instance-attributes
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
        # {channel: {'prev_error': float, 'integral': float, 'last_time': float}}
        self._channel_to_pid_state: dict[int, dict[str, float]] = {}
        self._pid_slice_seconds = 0.5
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

    def run(self):  # pylint: disable=too-many-locals, too-many-statements
        while True:
            while (message := self._message_queue.pop()) is not None:
                data = message.data
                match message.action:
                    case ActionType.CLOSE:
                        settings.DAC_MANAGER.close_all()
                        return
                    case ActionType.ON:
                        channel = data['channel']
                        self._channel_to_pid_enabled[channel] = True
                        self._channel_to_pid_state[channel] = {
                            'prev_error': 0.0,
                            'integral': 0.0,
                            'last_time': time.monotonic()
                        }
                    case ActionType.OFF:
                        channel = data['channel']
                        self._channel_to_pid_enabled[channel] = False
                    case ActionType.SETTING:
                        self._channel_to_pid_setting[data['channel']] = data['pid_setting']
            # PID
            pid_slice_deadline = time.monotonic() + self._pid_slice_seconds
            while time.monotonic() < pid_slice_deadline:
                frequency_info = settings.FREQUENCY_QUEUE.pop()
                if frequency_info is None:
                    continue
                channel, measured_time = frequency_info.channel, frequency_info.measured_at
                # Skip if PID not enabled
                if not self._channel_to_pid_enabled.get(channel, False):
                    continue
                pid_setting = self._channel_to_pid_setting.get(channel)
                pid_state = self._channel_to_pid_state.get(channel)
                # Calculate PID
                dt = max(0, measured_time - pid_state['last_time'])
                error = pid_setting.target_frequency - frequency_info.frequency
                # Safety check: large error
                if abs(error) >= MAX_ERROR_THRESHOLD_HZ:
                    self._channel_to_pid_enabled[channel] = False
                    error_ghz = abs(error) / 1e9
                    util.record_event(
                        Event.EventType.PID,
                        f'PID disabled for channel {channel} due to large error '
                        f'({error_ghz:.3f} GHz).'
                    )
                    channel_layer = get_channel_layer()
                    async_to_sync(channel_layer.group_send)(
                        f'channel_{channel}_pid_operation',
                        {
                            'type': 'notify',
                            'message': json.dumps({'on': False})
                        }
                    )
                    continue
                # PID calculation
                proportional = pid_setting.kp * error
                pid_state['integral'] += error * dt
                derivative = (error - pid_state['prev_error']) / dt if dt > 0 else 0.0
                pid_output = (
                    proportional +
                    pid_setting.ki * pid_state['integral'] +
                    pid_setting.kd * derivative
                )
                current_voltage = settings.CHANNEL_CACHE.get_dac_voltage(channel)
                new_voltage = current_voltage + pid_output
                # Safety check: voltage range
                if new_voltage < 0.0 or new_voltage > 2.5:
                    self._channel_to_pid_enabled[channel] = False
                    util.record_event(
                        Event.EventType.PID,
                        f'PID disabled for channel {channel} due to voltage out of range '
                        f'({new_voltage:.4f} V).'
                    )
                    async_to_sync(channel_layer.group_send)(
                        f'channel_{channel}_pid_operation',
                        {'type': 'notify', 'message': json.dumps({'on': False})}
                    )
                    continue
                # Apply PID output
                self._set_dac_voltage(channel, new_voltage)
                # Update state
                pid_state['prev_error'] = error
                pid_state['last_time'] = measured_time
                # Notify DAC output change
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f'channel_{channel}_dac_output',
                    {'type': 'notify', 'message': json.dumps({'voltage': new_voltage})}
                )
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
