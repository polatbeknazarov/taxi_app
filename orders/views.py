from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from orders.models import OrdersHistory
from orders.serializers import OrderSerializer


class OrderAPIView(APIView):
    def post(self, request):
        serializer = OrderSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()

            return Response(
                data={
                    'detail': 'Order successfully created.'
                }, status=status.HTTP_201_CREATED
            )


class OrdersHistoryList(APIView):
    def get(self, request, user_id):
        orders_history = OrdersHistory.objects.filter(driver_id=user_id)
        orders_data = []

        for order_history in orders_history:
            order_serializer = OrderSerializer(order_history.client)
            orders_data.append(order_serializer.data)

        return Response(orders_data, status=status.HTTP_200_OK)
