from django.contrib import admin
from django.urls import path, include
from django.conf.urls import handler404
from django.conf.urls.static import static 
from django.conf import settings 

from dispatcher.views import page_not_found_view

handler404 = page_not_found_view

urlpatterns = [
    path('admin/', admin.site.urls),

    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),

    path('api/v1/', include('orders.urls')),
    path('', include('dispatcher.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
