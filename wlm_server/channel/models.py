from django.db import models

from team.models import Team

class Channel(models.Model):
    channel = models.IntegerField(primary_key=True)
    teams = models.ManyToManyField(
        Team,
        related_name='channels',
    )
    name = models.CharField(max_length=30)
    dac_channel = models.PositiveSmallIntegerField(blank=True, null=True, default=None)

    def __str__(self):
        return str(self.channel)
