from django.contrib import admin

from .models import Measurement

@admin.register(Measurement)
class MeasurementAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            None,
            {
                'fields': ['setting', 'frequency', 'measured_at'],
            },
        ),
    ]
    list_display = ['id', 'setting__channel', 'frequency', 'measured_at']
    list_filter = ['setting__channel']
    search_fields = ['measured_at']
    ordering = ['measured_at']
    readonly_fields = ['measured_at']
