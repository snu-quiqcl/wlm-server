from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from .models import Operation

@receiver(post_save, sender=Operation)
def handle_model_save(sender, **kwargs):  # pylint: disable=unused-argument
    """Updates the channel cache whenever an operation status is saved."""
    settings.CHANNEL_CACHE.set_operation(kwargs['instance'])
