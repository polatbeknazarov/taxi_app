from rest_framework import serializers

from line.models import Line


class LineSerializer(serializers.ModelSerializer):
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    car_number = serializers.SerializerMethodField()
    car_brand = serializers.SerializerMethodField()

    class Meta:
        model = Line
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'car_number',
            'car_brand',
            'passengers',
            'passengers_required',
            'joined_at',
        )

    def get_first_name(self, obj):
        return obj.driver.first_name

    def get_last_name(self, obj):
        return obj.driver.last_name

    def get_username(self, obj):
        return obj.driver.username

    def get_car_number(self, obj):
        return obj.driver.car_number

    def get_car_brand(self, obj):
        return obj.driver.car_brand
