from django.contrib import admin

from orders.models import Order, OrdersHistory

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'from_city', 'to_city', 'phone_number', 'address', 'created_at', 'balance', 'in_search',)
    list_editable = ('from_city', 'to_city', 'phone_number', 'in_search')
    search_fields = ('phone_number', 'address',)
    list_per_page = 30


@admin.register(OrdersHistory)
class OrdersHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'driver', 'client',)
    list_per_page = 30

