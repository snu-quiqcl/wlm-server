from django.db import models

from channel.models import Channel

class PidSetting(models.Model):
    channel = models.ForeignKey(
        Channel,
        on_delete=models.PROTECT,
        related_name='pid_setting_history',
    )
    target_frequency = models.FloatField()
    kp = models.FloatField()
    ki = models.FloatField()
    kd = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f'Channel: {self.channel}, '
            f'Target frequency: {self.target_frequency}, '
            f'KP: {self.kp}, '
            f'KI: {self.ki}, '
            f'KD: {self.kd}, '
            f'Created at: {self.created_at}'
        )
