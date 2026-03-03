import json

from django.conf import settings
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from user.models import User
from channel.models import Channel
from operation.models import Operation
from lock.models import Lock
from pid_operation.models import PidOperation
from event.models import Event
from task import message as task_message
from task.handler import TaskHandler
from pid import message as pid_message
from pid.handler import PidHandler
from cache.channel import ChannelCache
from utils import util

def turn_on_operation(user: User, channel: Channel) -> int:
    """Turns on an operation for the given channel.
    
    Args:
        user: User requesting the operation.
        channel: Channel to turn on the operation for.
    
    Returns:
        HTTP status code.
    """
    ch = channel.channel
    task_message_queue: task_message.MessageQueue = settings.MESSAGE_QUEUE
    channel_cache: ChannelCache = settings.CHANNEL_CACHE
    util.record_event(
        Event.EventType.OPERATION,
        f'{user.username} requested to enable operation for channel {ch}.'
    )
    if not util.is_channel_running(ch):
        setting = channel_cache.get_setting(ch)
        message = task_message.MessageInfo(
            task_message.ActionType.SETTING,
            ch,
            {'setting': setting, 'update_exposure': True}
        )
        task_message_queue.push(message)
        if not util.is_wlm_running():
            message = task_message.MessageInfo(task_message.ActionType.START, ch, None)
            task_message_queue.push(message)
            task_handler = TaskHandler()
            task_handler.start()
            util.record_event(Event.EventType.OPERATION, 'WLM started.')
            pid_handler = PidHandler()
            pid_handler.start()
            util.record_event(Event.EventType.PID, 'PID handler started.')
        message = task_message.MessageInfo(task_message.ActionType.OPERATE, ch, {'on': True})
        task_message_queue.push(message)
        util.record_event(Event.EventType.OPERATION, f'Measurement of channel {ch} started.')
    operation = Operation(user=user, channel=channel, on=True)
    operation.save()
    requesters = [op.user.username for op in channel_cache.get_operations(ch).values() if op.on]
    notif = {'on': util.is_channel_running(ch), 'requesters': requesters}
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'channel_{ch}_operation', {'type': 'notify', 'message': json.dumps(notif)}
    )
    return 200


def turn_off_operation(user: User, channel: Channel) -> int:
    """Turns off an operation for the given channel.
    
    Args:
        user: User requesting the operation.
        channel: Channel to turn off the operation for.
    
    Returns:
        HTTP status code.
    """
    ch = channel.channel
    task_message_queue: task_message.MessageQueue = settings.MESSAGE_QUEUE
    pid_message_queue: pid_message.PidMessageQueue = settings.PID_MESSAGE_QUEUE
    channel_cache: ChannelCache = settings.CHANNEL_CACHE
    util.record_event(
        Event.EventType.OPERATION,
        f'{user.username} requested to stop the measurement of channel {ch}.'
    )
    pid_operation = channel_cache.get_pid_operation(ch)
    if pid_operation is not None and pid_operation.user == user:
        util.record_event(
            Event.EventType.WARNING,
            f'Cannot stop operation for channel {ch} because {user.username} is performing a '
            'PID operation. This request has been ignored.'
        )
        return 409
    operation = Operation(user=user, channel=channel, on=False)
    operation.save()
    if not util.is_channel_running(ch):
        message = task_message.MessageInfo(task_message.ActionType.OPERATE, ch, {'on': False})
        task_message_queue.push(message)
        util.record_event(Event.EventType.OPERATION, f'Measurement of channel {ch} stopped.')
        if not util.is_wlm_running():
            message = task_message.MessageInfo(task_message.ActionType.STOP, None, None)
            task_message_queue.push(message)
            message = task_message.MessageInfo(task_message.ActionType.CLOSE, None, None)
            task_message_queue.push(message)
            util.record_event(Event.EventType.OPERATION, 'WLM stopped.')
            message = pid_message.PidMessageInfo(pid_message.ActionType.CLOSE, None)
            pid_message_queue.push(message)
            util.record_event(Event.EventType.PID, 'PID handler stopped.')
    requesters = [op.user.username for op in channel_cache.get_operations(ch).values() if op.on]
    notif = {'on': util.is_channel_running(ch), 'requesters': requesters}
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'channel_{ch}_operation', {'type': 'notify', 'message': json.dumps(notif)}
    )
    return 200


def acquire_lock(user: User, channel: Channel) -> int:
    """Acquires a lock for the given channel.
    
    Args:
        user: User requesting the operation.
        channel: Channel to acquire the lock for.
    
    Returns:
        HTTP status code.
    """
    ch = channel.channel
    lock = Lock(user=user, channel=channel)
    lock.save()
    notif = {'locked': True, 'owner': user.username}
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'channel_{ch}_lock',
        {'type': 'notify', 'message': json.dumps(notif)}
    )
    util.record_event(Event.EventType.LOCK, f'{user.username} acquired the lock of channel {ch}.')
    return 200


def release_lock(user: User, channel: Channel) -> int:
    """Releases a lock for the given channel.
    
    Args:
        user: User requesting the operation.
        channel: Channel to release the lock for.
    
    Returns:
        HTTP status code.
    """
    ch = channel.channel
    pid_operation = settings.CHANNEL_CACHE.get_pid_operation(ch)
    if pid_operation is not None:
        util.record_event(
            Event.EventType.WARNING,
            f'Cannot release lock for channel {ch} because {user.username} is performing a '
            'PID operation. This request has been ignored.'
        )
        return 409
    lock = settings.CHANNEL_CACHE.get_lock(ch)
    lock.expires_at = timezone.now()
    lock.save()
    notif = {'locked': False, 'owner': None}
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'channel_{ch}_lock', {'type': 'notify', 'message': json.dumps(notif)}
    )
    util.record_event(Event.EventType.LOCK, f'{user.username} released the lock of channel {ch}.')
    return 200


def turn_on_pid(user: User, channel: Channel) -> int:
    """Turns on PID control for the given channel.
    
    Args:
        user: User requesting the operation.
        channel: Channel to turn on PID control for.
    
    Returns:
        HTTP status code.
    """
    ch = channel.channel
    pid_message_queue: pid_message.PidMessageQueue = settings.PID_MESSAGE_QUEUE
    channel_cache: ChannelCache = settings.CHANNEL_CACHE
    util.record_event(
        Event.EventType.PID,
        f'{user.username} requested to enable PID control for channel {ch}.'
    )
    operations = channel_cache.get_operations(ch)
    if not user.username in operations:
        util.record_event(
            Event.EventType.WARNING,
            f'Cannot enable PID control for channel {ch} because {user.username} is not '
            'performing an operation. This request has been ignored.'
        )
        return 409
    if util.is_channel_pid_enabled(ch):
        util.record_event(
            Event.EventType.WARNING,
            f'PID control for channel {ch} is already enabled. This request has been ignored.'
        )
        return 409
    pid_setting = channel_cache.get_pid_setting(ch)
    if pid_setting is None:
        util.record_event(
            Event.EventType.WARNING,
            f'Cannot enable PID control for channel {ch} because no PID setting is set. '
            'This request has been ignored.'
        )
        return 409
    pid_operation = PidOperation(user=user, channel=channel, on=True)
    pid_operation.save()
    message = pid_message.PidMessageInfo(
        pid_message.ActionType.SETTING,
        {'channel': ch, 'pid_setting': pid_setting}
    )
    pid_message_queue.push(message)
    message = pid_message.PidMessageInfo(pid_message.ActionType.ON, {'channel': ch})
    pid_message_queue.push(message)
    util.record_event(Event.EventType.PID, f'PID control for channel {ch} enabled.')
    return 200


def turn_off_pid(user: User, channel: Channel) -> int:
    """Turns off PID control for the given channel.
    
    Args:
        user: User requesting the operation.
        channel: Channel to turn off PID control for.
    
    Returns:
        HTTP status code.
    """
    ch = channel.channel
    pid_message_queue: pid_message.PidMessageQueue = settings.PID_MESSAGE_QUEUE
    util.record_event(
        Event.EventType.PID,
        f'{user.username} requested to disable PID control for channel {ch}.'
    )
    pid_operation = PidOperation(user=user, channel=channel, on=False)
    pid_operation.save()
    if not util.is_channel_pid_enabled(ch):
        message = pid_message.PidMessageInfo(pid_message.ActionType.OFF, {'channel': ch})
        pid_message_queue.push(message)
        util.record_event(Event.EventType.PID, f'PID control for channel {ch} disabled.')
    return 200
