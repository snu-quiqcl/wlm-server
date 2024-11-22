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
