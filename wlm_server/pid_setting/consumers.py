import json

from django.conf import settings
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from camel_converter import dict_to_camel

from channel.models import Channel
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
        if not user.is_authenticated:
            await self.close(code=401)
            return
        ch = self.scope['url_route']['kwargs']['ch']
        channel, error_code = await database_sync_to_async(
            util.verify_channel_access_with_dac)(user, ch)
        if channel is None:
            await self.close(code=error_code)
            return
        await self.accept()
        self.channel = channel

    @database_sync_to_async
    def _check_dac_info(self, channel: Channel):
        """Checks if channel has DAC device and channel information."""
        return channel.dac_device is not None and channel.dac_channel is not None

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


class DacOutputConsumer(AsyncWebsocketConsumer):
    """Consumer for notifying the DAC output of a specific channel.
    
    Attributes:
        group_name: Name of group it belongs to in the channel layer.
    """

    # pylint: disable=attribute-defined-outside-init
    async def connect(self):
        user = self.scope['user']
        if not user.is_authenticated:
            await self.close(code=401)
            return
        ch = self.scope['url_route']['kwargs']['ch']
        channel, error_code = await database_sync_to_async(
            util.verify_channel_access_with_dac)(user, ch)
        if channel is None:
            await self.close(code=error_code)
            return
<<<<<<< HEAD
=======
        has_dac_info = await self._check_dac_info(channel)
        if not has_dac_info:
            await self.close(code=400)
            return
>>>>>>> 0dba8a1 (Use `database_sync_to_async` decorator)
        self.group_name = f'channel_{ch}_dac_output'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        voltage = settings.CHANNEL_CACHE.get_dac_voltage(ch)
        await self.send(text_data=json.dumps({'voltage': voltage}))

    @database_sync_to_async
    def _check_dac_info(self, channel: Channel):
        """Checks if channel has DAC device and channel information."""
        return channel.dac_device is not None and channel.dac_channel is not None

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def notify(self, event: dict[str, str]):
        """Notifies the DAC output to the channels that belong to the same group.
        
        Args:
            event: Dictionary with two keys.
              type: Please refer to the documentation of Channels.
              message: Dictionary with one key.
                voltage: Updated DAC voltage in V.
        """
        message = event['message']
        await self.send(text_data=message)


class PidSettingConsumer(AsyncWebsocketConsumer):
    """Consumer for notifying the PID setting change of a specific channel.
    
    Attributes:
        group_name: Name of group it belongs to in the channel layer.
    """

    # pylint: disable=attribute-defined-outside-init
    async def connect(self):
        user = self.scope['user']
        if not user.is_authenticated:
            await self.close(code=401)
            return
        ch = self.scope['url_route']['kwargs']['ch']
        channel, error_code = await database_sync_to_async(
            util.verify_channel_access_with_dac)(user, ch)
        if channel is None:
            await self.close(code=error_code)
            return
<<<<<<< HEAD
=======
        has_dac_info = await self._check_dac_info(channel)
        if not has_dac_info:
            await self.close(code=400)
            return
>>>>>>> 0dba8a1 (Use `database_sync_to_async` decorator)
        self.group_name = f'channel_{ch}_pid_setting'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        pid_setting = settings.CHANNEL_CACHE.get_pid_setting(ch)
        await self.send(text_data=json.dumps(dict_to_camel({
            'target_frequency': pid_setting.target_frequency,
            'kp': pid_setting.kp,
            'ki': pid_setting.ki,
            'kd': pid_setting.kd
        })))

    @database_sync_to_async
    def _check_dac_info(self, channel: Channel):
        """Checks if channel has DAC device and channel information."""
        return channel.dac_device is not None and channel.dac_channel is not None

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def notify(self, event: dict[str, str]):
        """Notifies the PID setting change to the channels that belong to the same group.
        
        Args:
            event: Dictionary with two keys.
              type: Please refer to the documentation of Channels.
              message: Dictionary with up to four keys.
                target_frequency: Updated target frequency in Hz.
                kp: Updated proportional gain.
                ki: Updated integral gain.
                kd: Updated derivative gain.
        """
        message = event['message']
        await self.send(text_data=message)
