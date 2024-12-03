from channels.generic.websocket import AsyncWebsocketConsumer

class EventConsumer(AsyncWebsocketConsumer):
    """Consumer for notifying the event.
    
    Attributes:
        group_name: Name of group it belongs to in the channel layer.
    """

    # pylint: disable=attribute-defined-outside-init
    async def connect(self):
        self.group_name = 'event'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def notify(self, event: dict[str, str]):
        """Notifies the event to the channels that belong to the same group.
        
        Args:
            event: Dictionary with two keys.
              type: Please refer to the documentation of Channels.
              message: Dictionary with three keys.
                category: Event type.
                content: Event content.
                occurred_at: Occurrence time in ISO 8601 format.
        """
        message = event['message']
        await self.send(text_data=message)
