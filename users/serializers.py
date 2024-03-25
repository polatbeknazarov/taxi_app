from rest_framework import serializers
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'full_name',)

    def get_full_name(self, obj):
        return obj.get_full_name()


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(max_length=128, write_only=True)


class UserRegisterSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'password',
            'password2',
        )

    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')

        if password != password2:
            raise serializers.ValidationError(
                {'detail': 'Passwords do not match.'},
            )
        if len(password) < 8:
            raise serializers.ValidationError(
                {'detail': 'Password should be at least 8 characters long.'},
            )

        return attrs

    def create(self, validated_data):
        username = validated_data['username'].lower()
        first_name = validated_data['first_name'].title()
        last_name = validated_data['last_name'].title()

        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=validated_data['password'],
        )

        return user
