import json

from django.conf import settings
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from camel_converter import dict_to_camel

from user.models import User
from channel.models import Channel
from event.models import Event
from event.serializers import EventSerializer

def verify_channel_access(
    user: User, ch: int, check_lock: bool = True
) -> tuple[Channel | None, int | None]:
    """Verifies if the user has permission to access the channel.
    
    Args:
        user: User requesting access.
        ch: Target channel.
        check_lock: If True, it verifies if the user has a valid lock on the channel or the channel
          is open. Otherwise, it skips the check.

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
    if check_lock:
        lock = settings.CHANNEL_CACHE.get_lock(ch)
        if lock is not None and lock.user != user:
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
