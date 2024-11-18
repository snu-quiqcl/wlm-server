from django.db import models
from django.contrib.auth.models import AbstractUser

from team.models import Team

class User(AbstractUser):
    team = models.ForeignKey(
        Team,
        on_delete=models.PROTECT,
        related_name='members',
        null=True,
    )

    def __str__(self):
        return self.username
