from django.contrib import admin

from .models import Calibration

@admin.register(Calibration)
class CalibrationAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            None,
            {
                'fields': ['user', 'occurred_at'],
            },
        ),
    ]
    list_display = ['id', 'user', 'occurred_at']
    list_filter = ['user']
    search_fields = ['user']
    ordering = ['occurred_at']
    readonly_fields = ['occurred_at']
