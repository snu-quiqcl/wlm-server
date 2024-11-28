from django.apps import AppConfig


class SettingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'setting'

    def ready(self):
        from . import signals  # pylint: disable=import-outside-toplevel, unused-import
