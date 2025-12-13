from datetime import timedelta

from django.db import models
from django.core.exceptions import ValidationError

class Config(models.Model):
    wlm_version = models.IntegerField(blank=True, null=True, default=None)
    wlm_dll_path = models.CharField(max_length=100, blank=True, null=True, default=None)
    wlm_app_path = models.CharField(max_length=100, blank=True, null=True, default=None)
    calib_ch = models.IntegerField()
    calib_exposure = models.DurationField()
    calib_freq = models.FloatField()
    lock_duration = models.DurationField(default=timedelta(minutes=5))

    def __str__(self):
        return (
            f'WLM version: {self.wlm_version}, '
            f'WLM DLL path: {self.wlm_dll_path}, '
            f'WLM app path: {self.wlm_app_path}, '
            f'Calibration channel: {self.calib_ch}, '
            f'Calibration exposure: {self.calib_exposure}, '
            f'Calibration frequency: {self.calib_freq}, '
            f'Lock duration: {self.lock_duration}'
        )

    def clean(self):
        if Config.objects.count() and self.id != Config.objects.get().id:
            raise ValidationError('A config can only exist once at most.')
