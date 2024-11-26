from django.contrib import admin

from .models import Config

@admin.register(Config)
class ConfigAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            None,
            {
                'fields': ['wlm_version', 'wlm_dll_path', 'wlm_app_path',
                           'calib_ch', 'calib_exposure', 'calib_freq', 'lock_duration'],
            },
        ),
    ]
    list_display = ['id', 'wlm_version', 'wlm_dll_path', 'wlm_app_path',
                    'calib_ch', 'calib_exposure', 'calib_freq', 'lock_duration']
    list_filter = []
    search_fields = []
    ordering = []
