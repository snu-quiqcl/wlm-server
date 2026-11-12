import functools
import json
import threading
from typing import Any, Callable

from django.conf import settings
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from camel_converter import dict_to_camel

from user.models import User
from channel.models import Channel
from event.models import Event
from event.serializers import EventSerializer

def verify_channel_access(  # pylint: disable=too-many-return-statements
    user: User, ch: int, check_lock: bool = False, check_open: bool = False,
) -> tuple[Channel | None, int | None]:
    """Verifies if the user has permission to access the channel.
    
    Args:
        user: User requesting access.
        ch: Target channel.
        check_lock: If True, it verifies if the user has a valid lock on the channel. Otherwise, it
          skips the check.
        check_open: If check_lock is False and check_open is True, it verifies if the channel is
          open. Otherwise, it skips the check.

    Returns:
        (channel, error_code):
          channel: Target channel object. If an error occurs, it is set to None.
          error_code: HTTP status code for the occured error. If there is no error, it is set to
            None.
    """
    try:
        channel = Channel.objects.get(channel=ch)
    except Channel.DoesNotExist:
        return None, 404
    if not channel.teams.contains(user.team):
        return None, 403
    lock = settings.CHANNEL_CACHE.get_lock(ch)
    if check_lock:
        if lock is not None and lock.user == user:
            return channel, None
        return None, 409
    if check_open:
        if lock is None:
            return channel, None
        return None, 409
    return channel, None


def is_channel_running(channel: int) -> bool:
    """Returns whether the given channel is currently running.
    
    Args:
        channel: Target channel.
    """
    operations = settings.CHANNEL_CACHE.get_operations(channel)
    return any(op.on for op in operations.values())


def is_wlm_running() -> bool:
    """Returns whether the WLM is currently running."""
    return any(is_channel_running(channel.channel) for channel in Channel.objects.all())


def is_channel_pid_enabled(channel: int) -> bool:
    """Returns whether PID control is enabled for the given channel.
    
    Args:
        channel: Target channel.
    
    Returns:
        True if PID control is enabled for the channel, False otherwise.
    """
    pid_operation = settings.CHANNEL_CACHE.get_pid_operation(channel)
    return pid_operation is not None


def record_event(category: Event.EventType, content: str):
    """Records an event.

    It notifies the event to the channels following the event consumer.
    
    Args:
        category: Event type.
        content: Event content.
    """
    event = Event(category=category.value, content=content)
    event.save()
    notif = EventSerializer(event).data
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'event',
        {'type': 'notify', 'message': json.dumps(dict_to_camel(notif))}
    )


def _synchronized(lock: threading.Lock) -> Callable:
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            with lock:
                return func(*args, **kwargs)
        return wrapper
    return decorator


def task_synchronized(func: Callable) -> Callable:
    """Makes the given function execute after acquiring the task-associated lock."""
    return _synchronized(settings.TASK_LOCK)(func)


def lock_synchronized(func: Callable) -> Callable:
    """Makes the given function execute after acquiring the lock-associated lock."""
    return _synchronized(settings.LOCK_LOCK)(func)
