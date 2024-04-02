from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from djoser.serializers import UserCreateSerializer as DjoserUserCreateSerializer

CustomUser = get_user_model()


class CustomUserSerializer(DjoserUserCreateSerializer):
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
