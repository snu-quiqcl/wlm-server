import json

from django.conf import settings
from channels.generic.websocket import AsyncWebsocketConsumer

class FocusConsumer(AsyncWebsocketConsumer):
    """Consumer for notifying the focused channel.

    Attributes:
        group_name: Name of group it belongs to in the channel layer.
    """

    # pylint: disable=attribute-defined-outside-init
    async def connect(self):
        self.group_name = 'focus'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        focused_channel = settings.CHANNEL_CACHE.get_focused_channel()
        await self.send(text_data=json.dumps({'channel': focused_channel}))

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def notify(self, event: dict[str, str]):
        """Notifies the focus change to the channels that belong to the same group.

        Args:
            event: Dictionary with two keys.
              type: Please refer to the documentation of Channels.
              message: Dictionary with one key.
                channel: Focused channel. If no channel is focused, it is set to None.
        """
        message = event['message']
        await self.send(text_data=message)
