from django.db import models

class DacDevice(models.Model):
    class BackedType(models.TextChoices):
        DAC8734 = 'DAC8734', 'DAC8734'

    name = models.CharField(max_length=30, unique=True)
    backed = models.CharField(max_length=30, choices=BackedType, default=BackedType.DAC8734)
    port = models.CharField(max_length=30, unique=True)
