"""Module for PID handler with DAC."""

import threading

from django.conf import settings

from channel.models import Channel
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

    def run(self):
        while True:
            while (message := self._message_queue.pop()) is not None:
                data = message.data  # pylint: disable=unused-variable
                match message.action:
                    case ActionType.CLOSE:
                        settings.DAC_MANAGER.close_all()
                        return
            dac_control = self._dac_control_queue.pop()
            if dac_control is None:
                continue
            self._set_dac_voltage(dac_control.channel, dac_control.voltage)
