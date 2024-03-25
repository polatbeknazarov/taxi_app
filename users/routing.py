from django.urls import path

from users.consumers import UserConsumer

websocket_urlpatterns = [
    path('', UserConsumer.as_asgi()),
]
