from django.urls import path

from line.consumers import LineConsumer

websocket_urlpatterns = [
    path('', LineConsumer.as_asgi()),
]
