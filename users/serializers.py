from djoser.serializers import UserSerializer as DjoserUserSerializer


class CustomUserSerializer(DjoserUserSerializer):
    class Meta(DjoserUserSerializer.Meta):
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "phone_number",
            "balance",
            "car_number",
            "car_brand",
        )
