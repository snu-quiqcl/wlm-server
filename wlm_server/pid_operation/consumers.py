import json

from django.conf import settings
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from channel.models import Channel
from utils import util

class PidOperationConsumer(AsyncWebsocketConsumer):
    """Consumer for notifying the PID operation change of a specific channel.
    
    Attributes:
        group_name: Name of group it belongs to in the channel layer.
    """

    # pylint: disable=attribute-defined-outside-init
    async def connect(self):
        user = self.scope['user']
        if not user.is_authenticated:
            await self.close(code=401)
            return
        ch = self.scope['url_route']['kwargs']['ch']
        channel, error_code = await database_sync_to_async(
            util.verify_channel_access_with_dac)(user, ch)
        if channel is None:
            await self.close(code=error_code)
            return
        self.group_name = f'channel_{ch}_pid_operation'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        on = util.is_channel_pid_enabled(ch)
        status = settings.CHANNEL_CACHE.get_pid_status(ch)
        await self.send(text_data=json.dumps({'on': on, 'status': status}))

    @database_sync_to_async
    def _check_dac_info(self, channel: Channel):
        """Checks if channel has DAC device and channel information."""
        return channel.dac_device is not None and channel.dac_channel is not None

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def notify(self, event: dict[str, str]):
        """Notifies the PID operation change to the channels that belong to the same group.
        
        Args:
            event: Dictionary with two keys.
              type: Please refer to the documentation of Channels.
              message: Dictionary with two keys.
                on: Updated PID operation enabled status (user's intent).
                status: Updated PID operational status (actual working state).
        """
        message = event['message']
        await self.send(text_data=message)
