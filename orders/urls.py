from django.urls import path

from orders.views import LastPassengersAPIView

urlpatterns = [
    path("orders/current/", LastPassengersAPIView.as_view()),
]
