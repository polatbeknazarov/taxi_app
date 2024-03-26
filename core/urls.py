from django.contrib import admin
from django.urls import path, include

from line.views import TestAPIView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('users.urls')),
    path('api/v1/test/', TestAPIView.as_view()),
]
