from django.contrib import admin

from .models import Log


@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = 'created_at', 'username'
    list_display_links = list_display
    ordering = ['-created_at']
