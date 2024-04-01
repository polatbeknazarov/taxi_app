from django.contrib import admin
from line.models import Line


@admin.register(Line)
class LineAdmin(admin.ModelAdmin):
    list_display = ('id', 'driver', 'status', 'joined_at',)
    search_fields = ('driver',)
    list_per_page = 30
