from django.urls import path

from orders.views import OrderAPIView, OrdersHistoryList

urlpatterns = [
    path('order/', OrderAPIView.as_view()),
    path('order/<int:user_id>/', OrdersHistoryList.as_view()),
]
