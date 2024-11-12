from django.db import models

from user.models import User

class Calibration(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='calib_history',
    )
    occured_at = models.DateTimeField(auto_now_add=True)
