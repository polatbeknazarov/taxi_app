from rest_framework import serializers

from line.models import Line


class LineSerializer(serializers.ModelSerializer):
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    car_number = serializers.SerializerMethodField()

    class Meta:
        model = Line
        fields = (
            'id',
            'car_number',
            'first_name',
            'last_name',
            'passengers',
            'joined_at',
        )

    def get_first_name(self, obj):
        return obj.driver.first_name

    def get_last_name(self, obj):
        return obj.driver.last_name

    def get_car_number(self, obj):
        return obj.driver.username
