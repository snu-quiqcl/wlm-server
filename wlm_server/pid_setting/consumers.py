import json

from django.conf import settings
from channels.generic.websocket import AsyncWebsocketConsumer

from pid.dac_control import DacControlInfo

class DacControlConsumer(AsyncWebsocketConsumer):
    """Consumer for receiving the DAC control commands and sending them to the DAC control queue.
    
    Attributes:
        ch: Target WLM channel.
    """

    # pylint: disable=attribute-defined-outside-init
    async def connect(self):
        self.ch = self.scope['url_route']['kwargs']['ch']
        await self.accept()

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
            settings.DAC_CONTROL_QUEUE.push(DacControlInfo(self.ch, voltage))
