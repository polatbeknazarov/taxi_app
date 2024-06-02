from rest_framework import serializers
from djoser.serializers import UserSerializer as DjoserUserSerializer

from line.models import Line


class CustomUserSerializer(DjoserUserSerializer):
    status = serializers.SerializerMethodField()

    class Meta(DjoserUserSerializer.Meta):
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'phone_number',
            'balance',
            'car_number',
            'car_brand',
            'status',
        )

    def get_status(self, obj):
        driver = Line.objects.get(driver=obj)

        return driver.status
