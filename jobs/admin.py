from django.contrib import admin
from .models import Job


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['event_id', 'status', 'created_at', 'updated_at']
    list_filter = ['status', 'created_at']
    search_fields = ['event_id']
    readonly_fields = ['event_id', 'created_at', 'updated_at']