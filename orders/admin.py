from django.contrib import admin

from orders.models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'from_city', 'to_city', 'phone_number', 'address', 'created_at', 'in_search',)
    list_editable = ('from_city', 'to_city', 'phone_number', 'in_search')
    search_fields = ('phone_number', 'address',)
    list_per_page = 30
