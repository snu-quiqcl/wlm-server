from channels.generic.websocket import AsyncWebsocketConsumer

class SettingConsumer(AsyncWebsocketConsumer):
    """Consumer for notifying the setting change of a specific channel.
    
    Attributes:
        ch: Target WLM channel.
        group_name: Name of group it belongs to in the channel layer.
    """

    # pylint: disable=attribute-defined-outside-init
    async def connect(self):
        self.ch = self.scope['url_route']['kwargs']['ch']
        self.group_name = f'channel_{self.ch}_setting'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def notify(self, event: dict[str, str]):
        """Notifies the operation change to the channels that belong to the same group.
        
        Args:
            event: Dictionary with two keys.
              type: Please refer to the documentation of Channels.
              message: Dictionary with up to two keys.
                exposure: Updated exposure time in seconds.
                period: Updated period in seconds.
        """
        message = event['message']
        await self.send(text_data=message)
