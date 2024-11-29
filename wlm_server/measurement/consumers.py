from channels.generic.websocket import AsyncWebsocketConsumer

class MeasurementConsumer(AsyncWebsocketConsumer):
    """Consumer for notifying the measurement of a specific channel.
    
    Attributes:
        ch: Target WLM channel.
        group_name: Name of group it belongs to in the channel layer.
    """

    # pylint: disable=attribute-defined-outside-init
    async def connect(self):
        self.ch = self.scope['url_route']['kwargs']['ch']
        self.group_name = f'channel_{self.ch}_measurement'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def notify(self, event: dict[str, str]):
        """Notifies the measurement to the channels that belong to the same group.
        
        Args:
            event: Dictionary with two keys.
              type: Please refer to the documentation of Channels.
              message: Dictionary with two keys.
                One of the two:
                  frequency: Measured frequency in Hz.
                  error: Occurred error code. Please refer to the documentation of pylablib.
                measured_at: Measured time in ISO 8601 format.
        """
        message = event['message']
        await self.send(text_data=message)
