from django.apps import AppConfig

class OperationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'operation'

    def ready(self):
        from . import signals  # pylint: disable=import-outside-toplevel, unused-import
