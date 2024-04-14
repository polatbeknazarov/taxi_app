from django.urls import path

from orders.views import OrderAPIView, OrdersHistoryList, CurrentPassengersAPIView

urlpatterns = [
    path('orders/', OrderAPIView.as_view()),
    path('orders/history/', OrdersHistoryList.as_view()),
    path('orders/current/', CurrentPassengersAPIView.as_view()),
]
