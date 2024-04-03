from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from orders.models import Order
from orders.serializers import OrderSerizlizer


class OrderAPIView(APIView):
    def post(self, request):
        serializer = OrderSerizlizer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()

            return Response(
                data={
                    'detail': 'Order successfully created.'
                }, status=status.HTTP_201_CREATED
            )
