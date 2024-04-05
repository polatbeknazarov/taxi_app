from django.urls import path

from users.views import RegisterAPIView

urlpatterns = [
    path('register/', RegisterAPIView.as_view()),
]
