from django.contrib import admin

from .models import Channel

@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            None,
            {
                'fields': ['channel', 'teams', 'name', 'dac_device', 'dac_channel'],
            },
        ),
    ]
    list_display = ['channel', 'teams', 'name', 'dac_device', 'dac_channel']
    list_filter = ['teams', 'dac_device']
    search_fields = ['name', 'dac_device', 'dac_channel']
    ordering = ['channel']
