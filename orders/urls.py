from django.urls import path

from orders.views import OrdersHistoryList, LastPassengersAPIView

urlpatterns = [
    path('orders/history/', OrdersHistoryList.as_view()),
    path('orders/current/', LastPassengersAPIView.as_view()),
]
