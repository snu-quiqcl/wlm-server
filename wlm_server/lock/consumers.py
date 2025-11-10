import json

from django.conf import settings
from channels.generic.websocket import AsyncWebsocketConsumer

class LockConsumer(AsyncWebsocketConsumer):
    """Consumer for notifying the lock change of a specific channel.
    
    Attributes:
        ch: Target WLM channel.
        group_name: Name of group it belongs to in the channel layer.
    """

    # pylint: disable=attribute-defined-outside-init
    async def connect(self):
        self.ch = self.scope['url_route']['kwargs']['ch']
        self.group_name = f'channel_{self.ch}_lock'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        lock = settings.CHANNEL_CACHE.get_lock(self.ch)
        notif = {}
        if lock is None:
            notif = {'locked': False, 'owner': None}
        else:
            notif = {'locked': True, 'owner': lock.user.username}
        await self.send(text_data=json.dumps(notif))

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def notify(self, event: dict[str, str]):
        """Notifies the lock change to the channels that belong to the same group.
        
        Args:
            event: Dictionary with two keys.
              type: Please refer to the documentation of Channels.
              message: Dictionary with two keys.
                locked: Whether the channel is locked.
                owner: Username holding the lock on the channel. If the channel is open,
                  it is set to None.
        """
        message = event['message']
        await self.send(text_data=message)
