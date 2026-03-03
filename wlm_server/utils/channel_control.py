import json

from django.conf import settings
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from user.models import User
from channel.models import Channel
from pid_operation.models import PidOperation
from lock.models import Lock
from event.models import Event
from pid import message as pid_message
from cache.channel import ChannelCache
from utils import util

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
