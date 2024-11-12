from django.db import models

from user.models import User

class Operation(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='operation_history',
    )
    on = models.BooleanField()
    occured_at = models.DateTimeField(auto_now_add=True)
