from django.db.models.signals import post_save
from rest_framework import serializers

from orders.models import Order


class OrderSerizlizer(serializers.ModelSerializer):
    from_city = serializers.CharField(required=True)
    to_city = serializers.CharField(required=True)
    address = serializers.CharField(required=True)

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

    def create(self, validated_data):
        phone_number = validated_data['phone_number']

        existing_order = Order.objects.filter(
            phone_number=phone_number).first()
        if existing_order:
            order = Order.objects.update(**validated_data, in_search=True, driver=None)
            post_save.send(sender=Order, instance=existing_order, created=False)

            return order

        order = Order.objects.create(**validated_data)
        return order
