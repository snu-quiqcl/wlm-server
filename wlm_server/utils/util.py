from django.conf import settings

from user.models import User
from channel.models import Channel

def verify_channel_access(user: User, ch: int) -> tuple[Channel | None, int | None]:
    """Verifies if the user has permission to access the channel.
    
    Args:
        user: User requesting access.
        ch: Target channel.

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
