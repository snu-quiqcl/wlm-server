"""Module for caching the channel status."""

from collections import defaultdict

from operation.models import Operation
from setting.models import Setting

class ChannelCache:
    """Cache for channel status."""

    def __init__(self):
        # outer key: Channel__channel, inner key: User__username
        self._channel_to_operation: defaultdict[int, dict[str, Operation]] = defaultdict(dict)
        # key: Channel__channel
        self._channel_to_setting: dict[int, Setting] = {}
        self.load()

    def load(self):
        """Loads all channels status."""
        operations = (
            Operation.objects.order_by('channel', 'user', '-occurred_at').distinct('channel', 'user')
        )
        for operation in operations:
            (self._channel_to_operation
             [operation.channel.channel][operation.user.username]) = operation
        settings = Setting.objects.order_by('channel', '-created_at').distinct('channel')
        for setting in settings:
            self._channel_to_setting[setting.channel.channel] = setting

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
