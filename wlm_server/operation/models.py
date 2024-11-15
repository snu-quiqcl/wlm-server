from django.db import models

from user.models import User
from channel.models import Channel

class Operation(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='operation_history',
    )
    channel = models.ForeignKey(
        Channel,
        on_delete=models.PROTECT,
        related_name='operation_history',
    )
    on = models.BooleanField()
    occured_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f'User: {self.user}, '
            f'Channel: {self.channel}, '
            f'On: {self.on}, '
            f'Occured at: {self.occured_at}'
        )
