from django.db import models

from user.models import User
from channel.models import Channel

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
    expires_at = models.DateTimeField()
