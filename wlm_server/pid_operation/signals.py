from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from .models import PidOperation

@receiver(post_save, sender=PidOperation)
def handle_model_save(sender, **kwargs):  # pylint: disable=unused-argument
    """Updates the channel cache whenever a PID operation status is saved."""
    pid_operation = kwargs['instance']
    if pid_operation.on:
        settings.CHANNEL_CACHE.set_pid_operation(pid_operation)
    else:
        settings.CHANNEL_CACHE.delete_pid_operation(pid_operation.channel.channel)
