from rest_framework import serializers

from line.models import Line


class DriversFromLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Line
        fields = '__all__'
