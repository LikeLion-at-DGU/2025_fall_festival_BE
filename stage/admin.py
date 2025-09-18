from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Stage

@admin.register(Stage)
class StageAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "location", "start_time", "end_time", "is_active","image_url")
    list_filter = ("location", "start_time")
    search_fields = ("name",)
    ordering = ("start_time",)
