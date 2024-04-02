from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.conf import settings
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from channels.auth import AuthMiddlewareStack
from jwt import decode as jwt_decode
from jwt.exceptions import ExpiredSignatureError


User = get_user_model()


@database_sync_to_async
def get_user(validated_token):
    try:
        user = User.objects.get(id=validated_token["user_id"])

        return user
    except User.DoesNotExist:
        return AnonymousUser()


class JwtAuthMiddleware(BaseMiddleware):
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        headers = dict(scope['headers'])

        if b'authorization' in headers:
            token_name, token_key = headers[b'authorization'].decode().split()

            if token_name == 'Bearer':
                try:
                    decoded_data = jwt_decode(
                        token_key, settings.SECRET_KEY, algorithms=['HS256'])
                    scope['user'] = await get_user(validated_token=decoded_data)
                except ExpiredSignatureError:
                    await send({'type': 'websocket.close', 'code': 403})
                except Exception as e:
                    print(e)

        return await super().__call__(scope, receive, send)


def JwtAuthMiddlewareStack(inner):
    return JwtAuthMiddleware(AuthMiddlewareStack(inner))
