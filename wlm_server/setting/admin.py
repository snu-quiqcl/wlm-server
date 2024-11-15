from django.contrib import admin

from .models import Setting

@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            None,
            {
                'fields': ['channel', 'exposure', 'period', 'created_at'],
            },
        ),
    ]
    list_display = ['id', 'channel', 'exposure', 'period', 'created_at']
    list_filter = []
    search_fields = ['exposure', 'period']
    ordering = ['created_at']
    readonly_fields = ['created_at']
