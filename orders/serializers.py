from rest_framework import serializers

from orders.models import Order


class OrderSerizlizer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = (
            'id',
            'from_city',
            'to_city',
            'address',
            'phone_number',
            'created_at',
        )
