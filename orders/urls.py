from django.urls import path

from orders.views import OrderAPIView

urlpatterns = [
    path('order/', OrderAPIView.as_view()),
]
