from django.db import models

class Event(models.Model):
    class EventType(models.TextChoices):
        GENERAL = 'GN', 'general'
        ERROR = 'ER', 'error'
        WARNING = 'WN', 'warning'
        LOCK = 'LK', 'lock'
        OPERATION = 'OP', 'operation'
        CONFIG = 'CF', 'config'

    category = models.CharField(max_length=2, choices=EventType, default=EventType.GENERAL)
    content = models.CharField(max_length=200)
    occured_at = models.DateTimeField(auto_now_add=True)
