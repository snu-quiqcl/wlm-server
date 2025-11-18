import json

from django.conf import settings
from channels.generic.websocket import AsyncWebsocketConsumer

from utils import util

class OperationConsumer(AsyncWebsocketConsumer):
    """Consumer for notifying the operation change of a specific channel.
    
    Attributes:
        ch: Target WLM channel.
        group_name: Name of group it belongs to in the channel layer.
    """

    # pylint: disable=attribute-defined-outside-init
    async def connect(self):
        self.ch = self.scope['url_route']['kwargs']['ch']
        self.group_name = f'channel_{self.ch}_operation'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        on = util.is_channel_running(self.ch)
        requesters = [op.user.username
                      for op in settings.CHANNEL_CACHE.get_operations(self.ch).values() if op.on]
        await self.send(text_data=json.dumps({'on': on, 'requesters': requesters}))

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def notify(self, event: dict[str, str]):
        """Notifies the operation change to the channels that belong to the same group.
        
        Args:
            event: Dictionary with two keys.
              type: Please refer to the documentation of Channels.
              message: Dictionary with one key.
                on: Updated operation status.
                requesters: List of usernames requesting measurement.
        """
        message = event['message']
        await self.send(text_data=message)
