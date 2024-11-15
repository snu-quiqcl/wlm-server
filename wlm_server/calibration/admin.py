from django.contrib import admin

from .models import Calibration

@admin.register(Calibration)
class CalibrationAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            None,
            {
                'fields': ['user', 'occured_at'],
            },
        ),
    ]
    list_display = ['id', 'user', 'occured_at']
    list_filter = ['user']
    search_fields = ['user']
    ordering = ['occured_at']
    readonly_fields = ['occured_at']
