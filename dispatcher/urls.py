from django.urls import path

from dispatcher.views import GeneralStatisticsAPIView, DriversFromLineListAPIView

urlpatterns = [
    path('dispatcher/statistics/', GeneralStatisticsAPIView.as_view()),
    path('dispatcher/drivers/line/', DriversFromLineListAPIView.as_view()),
]
