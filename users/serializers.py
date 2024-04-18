from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db.models import Sum
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from djoser.serializers import UserCreateSerializer as DjoserUserCreateSerializer
from djoser.serializers import UserSerializer as DjoserUserSerializer

from orders.models import OrdersHistory

CustomUser = get_user_model()


class CustomUserCreateSerializer(DjoserUserCreateSerializer):
    password2 = serializers.CharField(write_only=True)

    class Meta(DjoserUserCreateSerializer.Meta):
        model = CustomUser
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'phone_number',
            'password',
            'password2',
        )

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password2'):
            raise serializers.ValidationError("Passwords do not match")

        validate_password(attrs['password'], user=CustomUser)

        return attrs

    def validate_password(self, value):
        errors = dict()

        try:
            validate_password(value, user=self.instance)
        except ValidationError as e:
            errors['password'] = list(e.messages)

        if errors:
            raise serializers.ValidationError(errors)

        return value


class CustomUserSerializer(DjoserUserSerializer):
    passengers_count = serializers.SerializerMethodField()

    class Meta(DjoserUserSerializer.Meta):
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'phone_number',
            'balance',
            'passengers_count',
        )

    def get_passengers_count(self, obj):
        orders_history = OrdersHistory.objects.filter(driver=obj)
        total_passengers = orders_history.aaggregate(total_passengers=Sum('order__passengers'))['total_passengers']

        return total_passengers
