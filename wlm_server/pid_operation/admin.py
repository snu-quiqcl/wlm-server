from django.contrib import admin

from .models import PidOperation

@admin.register(PidOperation)
class PidOperationAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            None,
            {
                'fields': ['user', 'channel', 'on', 'occurred_at'],
            },
        ),
    ]
    list_display = ['id', 'user', 'channel', 'on', 'occurred_at']
    list_filter = ['user', 'channel', 'on']
    search_fields = ['user']
    ordering = ['occurred_at']
    readonly_fields = ['occurred_at']
