from django.contrib import admin

from .models import Operation

@admin.register(Operation)
class OperationAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            None,
            {
                'fields': ['user', 'channel', 'on', 'occured_at'],
            },
        ),
    ]
    list_display = ['id', 'user', 'channel', 'on', 'occured_at']
    list_filter = ['user', 'channel', 'on']
    search_fields = ['user']
    ordering = ['occured_at']
    readonly_fields = ['occured_at']
