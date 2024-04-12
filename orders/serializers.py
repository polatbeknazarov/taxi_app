from django.db.models.signals import post_save
from rest_framework import serializers

from orders.models import Order, OrdersHistory, Client


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ('id', 'phone_number', 'balance',)


class OrderSerializer(serializers.ModelSerializer):
    client = ClientSerializer()

    class Meta:
        model = Order
        fields = ('id', 'client', 'from_city', 'to_city', 'address', 'passengers', 'created_at',)

    def create(self, validated_data):
        client_data = validated_data.pop('client')
        phone_number = client_data.get('phone_number')

        client, created = Client.objects.get_or_create(
            phone_number=phone_number, defaults=client_data)
        order = Order.objects.create(client=client, **validated_data)

        return order


# class ClientSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Client
#         fields = ('phone_number',)


# class OrderSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Order
#         fields = ('client.phone_number', 'from_city', 'to_city', 'address',)

#     def create(self, validated_data):
#         phone_number = validated_data.pop('client')
#         client, created = Client.objects.get_or_create(
#             phone_number=phone_number)

#         return client


# class OrderSerializer(serializers.ModelSerializer):
#     phone_number = serializers.CharField(source='client.phone_number')

#     class Meta:
#         model = Order
#         fields = (
#             'client',
#             'phone_number',
#             'from_city',
#             'to_city',
#             'address',
#             'created_at',
        # )

    # def create(self, validated_data):
    #     client_data = validated_data.pop('client')
    #     phone_number = validated_data.pop('client.phone_number')
    #     client, created = Client.objects.get_or_create(phone_number=phone_number, defaults=client_data)
    #     order = Order.objects.create(client=client, **validated_data)

    #     return order


# class OrderSerializer(serializers.ModelSerializer):
#     from_city = serializers.CharField(required=True)
#     to_city = serializers.CharField(required=True)
#     address = serializers.CharField(required=True)

#     class Meta:
#         model = Order
#         fields = (
#             'id',
#             'from_city',
#             'to_city',
#             'address',
#             'phone_number',
#             'created_at',
#         )

#     def create(self, validated_data):
#         phone_number = validated_data['phone_number']

#         existing_order = Order.objects.filter(
#             phone_number=phone_number).first()
#         if existing_order:
#             order = Order.objects.update(**validated_data, in_search=True, driver=None)
#             post_save.send(sender=Order, instance=existing_order, created=False)

#             return order

#         order = Order.objects.create(**validated_data)
#         return order


class OrdersHistorySerializer(serializers.Serializer):
    class Meta:
        model = OrdersHistory
        fields = ('id', 'driver', 'client',)
