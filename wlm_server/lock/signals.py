from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from .models import Lock

@receiver(post_save, sender=Lock)
def handle_model_save(sender, **kwargs):  # pylint: disable=unused-argument
    """Updates the channel cache whenever a lock is acquired or released."""
    channel_cache = settings.CHANNEL_CACHE
    lock = kwargs['instance']
    if kwargs['created']:  # acquired
        channel_cache.set_lock(lock)
    else:  # released
        channel_cache.delete_lock(lock.channel.channel)
