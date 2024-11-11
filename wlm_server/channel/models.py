from django.db import models

from team.models import Team

class Channel(models.Model):
    channel = models.IntegerField(primary_key=True)
    team = models.ManyToManyField(
        Team,
        related_name='channels',
    )
    name = models.CharField(max_length=30)
