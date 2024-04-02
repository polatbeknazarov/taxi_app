from django.contrib import admin

from users.models import CustomUser


@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'phone_number',
        'first_name',
        'last_name',
        'date_joined',
        'is_active',
    )
    list_editable = ('is_active',)
    search_fields = (
        'username',
        'phone_number',
        'first_name',
        'last_name',
    )
    list_per_page = 30
