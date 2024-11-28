from django.conf import settings

from channel.models import Channel

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
