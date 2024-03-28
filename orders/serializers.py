from rest_framework import serializers

from orders.models import Order


class OrderSerizlizer(serializers.ModelSerializer):
    in_search = serializers.BooleanField(read_only=True)

    class Meta:
        model = Order
        fields = (
            'id',
            'address',
            'in_search',
            'driver',
            'created_at',
        )
