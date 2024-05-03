from django.urls import path

from dispatcher import views

urlpatterns = [
    path('', views.index, name='index'),

    path('drivers/', views.drivers, name='drivers'),
    path('drivers/<int:pk>/edit/', views.driver_details, name='driver_details'),
    path('drivers/<int:pk>/add_balance/', views.add_balance, name='add_balance'),

    path('orders/', views.orders, name='orders'),

    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
]
