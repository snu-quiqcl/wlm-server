from django.apps import AppConfig


class LockConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'lock'

    def ready(self):
        from . import signals  # pylint: disable=import-outside-toplevel, unused-import
