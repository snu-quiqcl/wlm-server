from django.conf import settings

def is_channel_running(channel: int) -> bool:
    operations = settings.CHANNEL_CACHE.get_operations(channel)
    return any(op.on for op in operations.values())
