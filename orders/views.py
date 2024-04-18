from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model

from orders.models import OrdersHistory, Order
from orders.serializers import OrderSerializer, OrdersHistorySerializer


User = get_user_model()


class OrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = OrderSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrdersHistoryList(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        orders_history = OrdersHistory.objects.filter(
            driver_id=user.id)
        
        orders_seriazlier = OrdersHistorySerializer(orders_history, many=True)

        return Response(orders_seriazlier.data, status=status.HTTP_200_OK)


class CurrentPassengersAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        orders = Order.objects.filter(driver=user.id)[:4]
        serializer = OrderSerializer(orders, many=True)

        return Response(serializer.data)
