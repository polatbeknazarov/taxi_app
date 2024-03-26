from rest_framework import serializers

from line.models import Line


class LineSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Line
        fields = ('id', 'full_name', 'joined_at',)

    def get_full_name(self, obj):
        return obj.driver.get_full_name()
