from django.urls import path

from line.consumers import LineConsumer, MapConsumer

websocket_urlpatterns = [
    path("ws/", LineConsumer.as_asgi()),
    path("ws/map/", MapConsumer.as_asgi()),
]
