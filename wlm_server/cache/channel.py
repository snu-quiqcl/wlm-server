"""Module for caching the channel status."""

import threading
from collections import defaultdict

<<<<<<< HEAD
=======
from django.utils import timezone

from channel.models import Channel
>>>>>>> 69d5140 (Save DAC voltages periodically)
from operation.models import Operation
from pid_operation.models import PidOperation
from setting.models import Setting
from pid_setting.models import PidSetting, DacVoltage
from lock.models import Lock

DAC_VOLTAGE_SAVE_INTERVAL_SECONDS = 60.0

class ChannelCache:
    """Cache for channel status."""

    def __init__(self):
        # outer key: channel, inner key: username
        self._channel_to_operation: defaultdict[int, dict[str, Operation]] = defaultdict(dict)
        # key: channel
        self._channel_to_setting: dict[int, Setting] = {}
        self._channel_to_pid_operation: dict[int, PidOperation] = {}
        self._channel_to_pid_setting: dict[int, PidSetting] = {}
        self._channel_to_lock: dict[int, Lock] = {}
        self._channel_to_dac_voltage: dict[int, float] = defaultdict(float)
        self._channel_to_pid_status: dict[int, bool] = defaultdict(bool)
        self._load()
        self._start_dac_voltage_periodic_saving()

    def _load(self):
        """Loads all channels status."""
        settings = Setting.objects.order_by('channel', '-created_at').distinct('channel')
        for setting in settings:
            self._channel_to_setting[setting.channel.channel] = setting
        pid_settings = PidSetting.objects.order_by('channel', '-created_at').distinct('channel')
        for pid_setting in pid_settings:
            self._channel_to_pid_setting[pid_setting.channel.channel] = pid_setting
        locks = (Lock.objects.order_by('channel', '-started_at').distinct('channel'))
        for lock in locks:
            self._channel_to_lock[lock.channel.channel] = lock
        dac_voltages = DacVoltage.objects.order_by('channel', '-created_at').distinct('channel')
        for dac_voltage in dac_voltages:
            self._channel_to_dac_voltage[dac_voltage.channel.channel] = dac_voltage.voltage

    def set_operation(self, operation: Operation):
        """Stores the given operation as the latest.
        
        Args:
            operation: The latest operation.
        """
        self._channel_to_operation[operation.channel.channel][operation.user.username] = operation

    def set_setting(self, setting: Setting):
        """Stores the given setting as the latest.
        
        Args:
            setting: The latest setting.
        """
        self._channel_to_setting[setting.channel.channel] = setting

    def set_pid_operation(self, pid_operation: PidOperation):
        """Stores the given PID operation as the latest.
        
        Args:
            pid_operation: The latest PID operation.
        """
        self._channel_to_pid_operation[pid_operation.channel.channel] = pid_operation

    def set_pid_setting(self, pid_setting: PidSetting):
        """Stores the given PID setting as the latest.
        
        Args:
            pid_setting: The latest PID setting.
        """
        self._channel_to_pid_setting[pid_setting.channel.channel] = pid_setting

    def set_lock(self, lock: Lock):
        """Stores the given lock as the latest.
        
        Args:
            lock: The latest lock.
        """
        self._channel_to_lock[lock.channel.channel] = lock

    def set_dac_voltage(self, channel: int, voltage: float):
        """Stores the given DAC voltage as the latest.
        
        Args:
            channel: Target channel.
            voltage: The latest DAC voltage.
        """
        self._channel_to_dac_voltage[channel] = voltage

    def set_pid_status(self, channel: int, status: bool):
        """Stores the given PID status as the latest.
        
        Args:
            channel: Target channel.
            status: The latest PID operational status.
        """
        self._channel_to_pid_status[channel] = status

    def delete_lock(self, channel: int):
        """Deletes the lock from the given channel.
        
        Args:
            channel: Target channel.
        """
        del self._channel_to_lock[channel]

    def delete_pid_operation(self, channel: int):
        """Deletes the PID operation from the given channel.
        
        Args:
            channel: Target channel.
        """
        del self._channel_to_pid_operation[channel]

    def get_operations(self, channel: int) -> dict[str, Operation]:
        """Returns the latest operation status for the given channel.
        
        Args:
            channel: Target channel.

        Returns:
            Dictionary with user name as the key and the latest operation status as the value.
        """
        return self._channel_to_operation[channel]

    def get_setting(self, channel: int) -> Setting:
        """Returns the latest setting for the given channel.
        
        Args:
            channel: Target channel.

        Returns:
            The latest setting.
        """
        return self._channel_to_setting[channel]

    def get_pid_operation(self, channel: int) -> PidOperation | None:
        """Returns the latest PID operation for the given channel.
        
        Args:
            channel: Target channel.

        Returns:
            The latest PID operation. If there is no PID operation, it returns None.
        """
        return self._channel_to_pid_operation.get(channel, None)

    def get_pid_setting(self, channel: int) -> PidSetting | None:
        """Returns the latest PID setting for the given channel.
        
        Args:
            channel: Target channel.

        Returns:
            The latest PID setting. If there is no PID setting, it returns None.
        """
        return self._channel_to_pid_setting.get(channel, None)

    def get_lock(self, channel: int) -> Lock | None:
        """Returns the latest lock for the given channel.
        
        Args:
            channel: Target channel.

        Returns:
            The latest lock. If there is no valid lock, it returns None.
        """
        return self._channel_to_lock.get(channel, None)

    def get_dac_voltage(self, channel: int) -> float:
        """Returns the latest DAC voltage for the given channel.
        
        Args:
            channel: Target channel.

        Returns:
            The latest DAC voltage.
        """
        return self._channel_to_dac_voltage[channel]

    def get_pid_status(self, channel: int) -> bool:
        """Returns the latest PID status for the given channel.
        
        Args:
            channel: Target channel.

        Returns:
            The latest PID operational status.
        """
        return self._channel_to_pid_status[channel]

    def _save_dac_voltages(self):
        """Saves current DAC voltages to database."""
        for channel_num, voltage in self._channel_to_dac_voltage.items():
            channel = Channel.objects.get(channel=channel_num)
            DacVoltage.objects.create(channel=channel, voltage=voltage)

    def _start_dac_voltage_periodic_saving(self):
        """Starts periodic saving of DAC voltages."""
        def save_periodically():
            self._save_dac_voltages()
            timer = threading.Timer(DAC_VOLTAGE_SAVE_INTERVAL_SECONDS, save_periodically)
            timer.daemon = True
            timer.start()
        timer = threading.Timer(DAC_VOLTAGE_SAVE_INTERVAL_SECONDS, save_periodically)
        timer.daemon = True
        timer.start()
