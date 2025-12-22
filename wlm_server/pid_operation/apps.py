from django.apps import AppConfig

class PidOperationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pid_operation'

    def ready(self):
        from . import signals  # pylint: disable=import-outside-toplevel, unused-import
