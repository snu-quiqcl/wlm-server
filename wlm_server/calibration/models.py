from django.db import models

from user.models import User

class Calibration(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='calib_history',
    )
    occured_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f'User: {self.user}, '
            f'Occured at: {self.occured_at}'
        )
