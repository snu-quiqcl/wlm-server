import json
from datetime import timedelta

from django.utils import timezone
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from camel_converter import dict_to_camel

from measurement.models import Measurement
from measurement.serializers import MeasurementSerializer

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
        message = await self.get_recent_measurements()
        await self.send(text_data=json.dumps(message))

    @database_sync_to_async
    def get_recent_measurements(self):
        cutoff_time = timezone.now() - timedelta(minutes=10)
        recent_measurements = Measurement.objects.filter(
            setting__channel__channel=self.ch,
            measured_at__gte=cutoff_time
        ).order_by('measured_at')
        return [dict_to_camel(measurement)
                for measurement in MeasurementSerializer(recent_measurements, many=True).data]

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def notify(self, event: dict[str, str]):
        """Notifies the measurement to the channels that belong to the same group.
        
        Args:
            event: Dictionary with two keys.
              type: Please refer to the documentation of Channels.
              message: Dictionary with three keys.
                frequency: Measured frequency in Hz. If an error occurs, it is set to None.
                error: Occurred error code. Please refer to the documentation of pylablib. If no
                  error occurs, it is set to None.
                measured_at: Measured time in ISO 8601 format.
        """
        message = event['message']
        await self.send(text_data=message)
