from django.contrib import admin

from .models import Channel

@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            None,
            {
                'fields': ['channel', 'teams', 'name', 'max_exposure', 'dac_device', 'dac_channel'],
            },
        ),
    ]
    list_display = ['channel', 'name', 'max_exposure', 'dac_device__name', 'dac_channel']
    list_filter = ['teams', 'dac_device__name']
    search_fields = ['name', 'dac_device__name', 'dac_channel']
    ordering = ['channel']
