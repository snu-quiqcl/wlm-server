from django.db import models

from channel.models import Channel

class Setting(models.Model):
    channel = models.ForeignKey(
        Channel,
        on_delete=models.PROTECT,
        related_name='setting_history',
    )
    exposure = models.FloatField()
    period = models.DurationField()
    created_at = models.DateTimeField(auto_now_add=True)
