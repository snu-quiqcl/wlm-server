from django.contrib import admin

from .models import Event

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            None,
            {
                'fields': ['category', 'content', 'occurred_at'],
            },
        ),
    ]
    list_display = ['id', 'category', 'content', 'occurred_at']
    list_filter = ['category']
    search_fields = ['category', 'content']
    ordering = ['occurred_at']
    readonly_fields = ['occurred_at']
