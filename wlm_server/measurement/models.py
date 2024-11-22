from django.db import models

from setting.models import Setting

class Measurement(models.Model):
    class ErrorType(models.TextChoices):
        UNDER = 'under', 'underexposed'
        OVER = 'over', 'overexposed'

    setting = models.ForeignKey(
        Setting,
        on_delete=models.PROTECT,
        related_name='measure_history',
    )
    frequency = models.FloatField(blank=True, null=True, default=None)
    error = models.CharField(max_length=10, choices=ErrorType, null=True, default=None)
    measured_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f'Setting: {self.setting}, '
            f'Frequency: {self.frequency}, '
            f'Error: {self.error}, '
            f'Measured at: {self.measured_at}'
        )
