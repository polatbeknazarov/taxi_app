from django.urls import path
from django.contrib.admin.views.decorators import staff_member_required

from dispatcher import views

urlpatterns = [
    path('', views.index, name='index'),

    path('drivers/', views.drivers, name='drivers'),
    path('drivers/<int:pk>/edit/', views.driver_details, name='driver_details'),
    path('drivers/<int:pk>/add_balance/', views.add_balance, name='add_balance'),
    path('drivers/<int:pk>/block/', views.block_driver, name='block_driver'),
    path('drivers/<int:pk>/unblock/', views.unblock_driver, name='unblock_driver'),

    path('orders/', views.orders, name='orders'),
    path('orders/<int:pk>/', views.order_details, name='order_details'),

    path('pricing/', views.pricing, name='pricing'),

    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
]
