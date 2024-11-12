from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = [
        (
            None,
            {
                'fields': ['username', 'password', 'team'],
            },
        ),
        (
            'Advanced options',
            {
                'classes': ['collapse'],
                'fields': ['is_superuser'],
            },
        ),
        (
            'Important dates',
            {
                'classes': ['collapse'],
                'fields': ['last_login'],
            },
        ),
    ]
    list_display = ('username', 'id', 'team__name', 'is_superuser')
    list_filter = ('team__name', 'is_superuser')
    search_fields = ('username', 'team__name')
    ordering = ('id',)
