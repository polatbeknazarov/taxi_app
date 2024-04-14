from rest_framework import serializers

from orders.models import Order, OrdersHistory, Client


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = (
            'id',
            'phone_number',
            'balance',
        )


class OrderSerializer(serializers.ModelSerializer):
    client = ClientSerializer()

    class Meta:
        model = Order
        fields = (
            'id',
            'client',
            'from_city',
            'to_city',
            'address',
            'passengers',
            'created_at',
        )

    def create(self, validated_data):
        client_data = validated_data.pop('client')
        phone_number = client_data.get('phone_number')

        client, created = Client.objects.get_or_create(
            phone_number=phone_number, 
            defaults=client_data,
        )
        order = Order.objects.create(client=client, **validated_data)

        return order


class OrdersHistorySerializer(serializers.ModelSerializer):
    order = OrderSerializer()

    class Meta:
        model = OrdersHistory
        fields = (
            'id',
            'driver',
            'order',
        )
