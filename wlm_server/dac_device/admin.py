from django.contrib import admin

from .models import DacDevice

@admin.register(DacDevice)
class DacDeviceAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            None,
            {
                'fields': ['name', 'backend', 'port'],
            },
        ),
    ]
    list_display = ['id', 'name', 'backend', 'port']
    list_filter = ['backend']
    search_fields = ['name', 'backend', 'port']
    ordering = ['id']
