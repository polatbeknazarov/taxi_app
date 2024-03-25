from rest_framework_simplejwt.tokens import RefreshToken

from users.serializers import UserSerializer


def get_auth_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'user': UserSerializer(user).data,
        'tokens': {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }
    }
