import json

from django.conf import settings
from channels.generic.websocket import AsyncWebsocketConsumer

from pid.dac_control import DacControlInfo
from utils import util

class DacControlConsumer(AsyncWebsocketConsumer):
    """Consumer for receiving the DAC control commands and sending them to the DAC control queue.
    
    Attributes:
        channel: Target WLM channel.
    """

    # pylint: disable=attribute-defined-outside-init
    async def connect(self):
        user = self.scope['user']
        ch = self.scope['url_route']['kwargs']['ch']
        channel, error_code = util.verify_channel_access(user, ch)
        if channel is None:
            await self.close(code=error_code)
            return
        await self.accept()
        self.channel = channel

    async def receive(self, text_data=None, bytes_data=None):
        """Receives the DAC control commands and sends them to the DAC control queue.
        
        Args:
            text_data: JSON-encoded text data received from the client.
              It should have the action key.
              If the action is 'voltage', it should have the following keys:
                voltage: Target voltage in V.
            bytes_data: Not used.
        """
        payload = json.loads(text_data)
        action = payload['action']
        if action == 'voltage':
            voltage = payload['voltage']
            settings.DAC_CONTROL_QUEUE.push(DacControlInfo(self.channel.channel, voltage))
