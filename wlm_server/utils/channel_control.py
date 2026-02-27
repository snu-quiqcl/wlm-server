from django.conf import settings

from user.models import User
from channel.models import Channel
from pid_operation.models import PidOperation
from event.models import Event
from pid import message as pid_message
from cache.channel import ChannelCache
from utils import util

def turn_on_pid(user: User, channel: Channel) -> int:
    """Turns on PID control for the given channel.
    
    Args:
        user: User requesting the operation.
        channel: Channel to turn on PID control for.
    
    Returns:
        HTTP status code.
    """
    ch = ch
    pid_message_queue: pid_message.PidMessageQueue = settings.PID_MESSAGE_QUEUE
    channel_cache: ChannelCache = settings.CHANNEL_CACHE
    pid_operation = PidOperation(user=user, channel=channel, on=True)
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
    message = pid_message.PidMessageInfo(
        pid_message.ActionType.SETTING,
        {'channel': ch, 'pid_setting': pid_setting}
    )
    pid_message_queue.push(message)
    message = pid_message.PidMessageInfo(pid_message.ActionType.ON, {'channel': ch})
    pid_message_queue.push(message)
    util.record_event(Event.EventType.PID, f'PID control for channel {ch} enabled.')
    pid_operation.save()
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
    pid_operation = PidOperation(user=user, channel=channel, on=False)
    util.record_event(
        Event.EventType.PID,
        f'{user.username} requested to disable PID control for channel {ch}.'
    )
    pid_operation.save()
    if not util.is_channel_pid_enabled(ch):
        message = pid_message.PidMessageInfo(pid_message.ActionType.OFF, {'channel': ch})
        pid_message_queue.push(message)
        util.record_event(Event.EventType.PID, f'PID control for channel {ch} disabled.')
    return 200
