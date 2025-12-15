from django.db import models

class DacDevice(models.Model):
    class BackendType(models.TextChoices):
        DAC8734 = 'DAC8734', 'DAC8734'

    name = models.CharField(max_length=30, unique=True)
    backend = models.CharField(max_length=30, choices=BackendType, default=BackendType.DAC8734)
    port = models.CharField(max_length=30, unique=True)
