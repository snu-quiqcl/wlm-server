from django.contrib import admin

from .models import PidSetting

@admin.register(PidSetting)
class PidSettingAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            None,
            {
                'fields': ['channel', 'target_frequency', 'kp', 'ki', 'kd', 'created_at'],
            },
        ),
    ]
    list_display = ['id', 'channel', 'target_frequency', 'kp', 'ki', 'kd', 'created_at']
    list_filter = ['channel']
    search_fields = ['target_frequency', 'kp', 'ki', 'kd']
    ordering = ['created_at']
    readonly_fields = ['created_at']
