from django.contrib import admin
from dispatcher.models import Pricing


@admin.register(Pricing)
class PricingAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_fee', 'order_bonus',)