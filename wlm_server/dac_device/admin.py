from django.contrib import admin

from .models import DacDevice

@admin.register(DacDevice)
class DacDeviceAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            None,
            {
                'fields': ['name', 'backed', 'port'],
            },
        ),
    ]
    list_display = ['id', 'name', 'backed', 'port']
    list_filter = ['backed']
    search_fields = ['name', 'backed', 'port']
    ordering = ['id']
