from django.db import models

class Event(models.Model):
    class EventType(models.TextChoices):
        GENERAL = 'GN', 'general'
        WARNING = 'WN', 'warning'
        ERROR = 'ER', 'error'
        USER = 'US', 'user'
        OPERATION = 'OP', 'operation'
        SETTING = 'ST', 'setting'
        PID = 'PD', 'pid'
        LOCK = 'LK', 'lock'
        CONFIG = 'CF', 'config'

    category = models.CharField(max_length=2, choices=EventType, default=EventType.GENERAL)
    content = models.CharField(max_length=200)
    occurred_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f'Category: {self.category}, '
            f'Content: {self.content}, '
            f'Occurred at: {self.occurred_at}'
        )
