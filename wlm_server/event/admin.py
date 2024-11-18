from django.contrib import admin

from .models import Event

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            None,
            {
                'fields': ['category', 'content', 'occured_at'],
            },
        ),
    ]
    list_display = ['id', 'category', 'content', 'occured_at']
    list_filter = ['category']
    search_fields = ['category', 'content']
    ordering = ['occured_at']
    readonly_fields = ['occured_at']
