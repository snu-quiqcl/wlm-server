from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from .models import PidOperation

@receiver(post_save, sender=PidOperation)
def handle_model_save(sender, **kwargs):  # pylint: disable=unused-argument
    """Updates the channel cache whenever a PID operation status is saved."""
    settings.CHANNEL_CACHE.set_pid_operation(kwargs['instance'])
