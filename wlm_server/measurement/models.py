from django.db import models

from setting.models import Setting

class Measurement(models.Model):
    setting = models.ForeignKey(
        Setting,
        on_delete=models.PROTECT,
        related_name='measure_history',
    )
    frequency = models.FloatField()
    measured_at = models.DateTimeField(auto_now_add=True)
