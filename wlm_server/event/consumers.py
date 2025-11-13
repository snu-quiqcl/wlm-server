import json
from datetime import timedelta

from django.utils import timezone
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from camel_converter import dict_to_camel

from event.models import Event
from event.serializers import EventSerializer

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
        message = await self.get_recent_events()
        await self.send(text_data=json.dumps(message))

    @database_sync_to_async
    def get_recent_events(self):
        cutoff_time = timezone.now() - timedelta(minutes=10)
        recent_events = Event.objects.filter(occurred_at__gte=cutoff_time).order_by('occurred_at')
        return [dict_to_camel(event) for event in EventSerializer(recent_events, many=True).data]

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
