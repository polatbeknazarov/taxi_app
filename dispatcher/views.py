from django.db.models import Count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status, generics

from dispatcher.serializers import DriversFromLineSerializer
from orders.models import Order, Client
from line.models import Line


class GeneralStatisticsAPIView(APIView):
    permission_classes = [IsAuthenticated,]

    def get(self, request):
        orders_quantity = Order.objects.aggregate(
            count=Count('id'))['count'] or 0
        clients_quantity = Client.objects.aggregate(count=Count('id'))[
            'count'] or 0
        drivers_quantity = Line.objects.aggregate(
            count=Count('id'))['count'] or 0

        return Response({
            'orders_quantity': orders_quantity,
            'clients_quantity': clients_quantity,
            'drivers_quantity': drivers_quantity
        }, status=status.HTTP_200_OK)
    
class DriversFromLineListAPIView(generics.ListAPIView):
    queryset = Line.objects.filter(status=True)
    serializer_class = DriversFromLineSerializer
    permission_classes = [IsAuthenticated,]
