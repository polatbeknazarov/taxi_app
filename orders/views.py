from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from orders.models import OrdersHistory, Order, Client
from orders.serializers import ClientSerializer, OrderSerializer


class OrderAPIView(APIView):
    def post(self, request, format=None):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # serializer = OrderSerializer(data=request.data)

        # if serializer.is_valid():
        #     serializer.save()
        #     return Response(serializer.data, status=status.HTTP_201_CREATED)

        # else:
        #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # serializer = OrderSerializer(data=request.data)

        # if serializer.is_valid(raise_exception=True):
        #     serializer.save()

        #     return Response(
        #         data={
        #             'detail': 'Order successfully created.'
        #         }, status=status.HTTP_201_CREATED
        #     )

    # def get(self, request, user_id):
    #     driver_orders = Order.objects.filter(driver_id=user_id, in_search=True)
    #     orders = []

    #     for order in driver_orders:
    #         serialize_order = OrderSerializer()


class OrdersHistoryList(APIView):
    def get(self, request, user_id):
        orders_history = OrdersHistory.objects.filter(driver_id=user_id)
        orders_data = []

        for order_history in orders_history:
            order_serializer = OrderSerializer(order_history.client)
            orders_data.append(order_serializer.data)

        return Response(orders_data, status=status.HTTP_200_OK)
