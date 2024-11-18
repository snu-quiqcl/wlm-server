from django.contrib import admin

from .models import Team

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            None,
            {
                'fields': ['name'],
            },
        ),
    ]
    list_display = ['name', 'id']
    list_filter = []
    search_fields = ['name']
    ordering = ['id']
