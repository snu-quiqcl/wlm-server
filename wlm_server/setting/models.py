from django.db import models

from channel.models import Channel

class Setting(models.Model):
    channel = models.ForeignKey(
        Channel,
        on_delete=models.PROTECT,
        related_name='setting_history',
    )
    exposure = models.DurationField()
    period = models.DurationField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f'Channel: {self.channel}, '
            f'Exposure: {self.exposure}, '
            f'Period: {self.period}, '
            f'Created at: {self.created_at}'
        )
