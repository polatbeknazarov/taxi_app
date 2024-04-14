from django.contrib import admin

from orders.models import Order, OrdersHistory, Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'phone_number',
        'balance',
    )
    list_per_page = 30


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'client',
        'driver',
        'from_city',
        'to_city',
        'address',
        'created_at',
    )
    list_editable = (
        'from_city',
        'to_city',
    )
    search_fields = (
        'client',
        'address',
    )
    list_per_page = 30


@admin.register(OrdersHistory)
class OrdersHistoryAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'driver',
    )
    list_per_page = 30
