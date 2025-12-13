from django.db import models

from team.models import Team
from dac_device.models import DacDevice

class Channel(models.Model):
    channel = models.IntegerField(primary_key=True)
    teams = models.ManyToManyField(
        Team,
        related_name='channels',
    )
    name = models.CharField(max_length=30)
    dac_device = models.ForeignKey(
        DacDevice,
        on_delete=models.PROTECT,
        related_name='channels',
        blank=True,
        null=True,
        default=None,
    )
    dac_channel = models.PositiveSmallIntegerField(blank=True, null=True, default=None)

    def __str__(self):
        return str(self.channel)
