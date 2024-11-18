from django.contrib import admin

from .models import Channel

@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            None,
            {
                'fields': ['channel', 'teams', 'name'],
            },
        ),
    ]
    list_display = ['channel', 'name']
    list_filter = []
    search_fields = ['name']
    ordering = ['channel']
