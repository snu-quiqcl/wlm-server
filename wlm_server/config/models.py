from django.db import models
from datetime import timedelta

class Config(models.Model):
    wlm_version = models.IntegerField(blank=True, null=True, default=None)
    wlm_dll_path = models.CharField(max_length=100, blank=True, null=True, default=None)
    wlm_app_path = models.CharField(max_length=100, blank=True, null=True, default=None)
    calib_ch = models.IntegerField()
    calib_freq = models.FloatField()
    lock_duration = models.DurationField(default=timedelta(minutes=5))

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['id'], name='unique_config'
            )
        ]
