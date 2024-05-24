from django.contrib import admin
from dispatcher.models import Pricing, DriverBalanceHistory


@admin.register(Pricing)
class PricingAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_fee', 'order_bonus',)


@admin.register(DriverBalanceHistory)
class PricingAdmin(admin.ModelAdmin):
    list_display = ('id', 'driver', 'transaction', 'created_at',)
