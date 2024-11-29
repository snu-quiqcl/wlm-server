from django.db import models
from django.utils import timezone

from user.models import User
from channel.models import Channel
from config.models import Config

def get_default_expires_at():
    config = Config.objects.first()
    return timezone.now() + config.lock_duration


class Lock(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='locks',
    )
    channel = models.ForeignKey(
        Channel,
        on_delete=models.PROTECT,
        related_name='lock_history',
    )
    started_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=get_default_expires_at)

    def __str__(self):
        return (
            f'User: {self.user}, '
            f'Channel: {self.channel}, '
            f'Started at: {self.started_at}, '
            f'Expires at: {self.expires_at}'
        )
