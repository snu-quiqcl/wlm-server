from django.contrib import admin

from .models import Lock

@admin.register(Lock)
class LockAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            None,
            {
                'fields': ['user', 'channel', 'started_at', 'expires_at'],
            },
        ),
    ]
    list_display = ['id', 'user', 'channel', 'started_at', 'expires_at']
    list_filter = ['user', 'channel']
    search_fields = ['user']
    ordering = ['expires_at']
    readonly_fields = ['started_at', 'expires_at']
