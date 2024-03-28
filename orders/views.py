from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from orders.serializers import OrderSerizlizer
from orders.tasks import send_order


class OrderAPIView(APIView):
    def post(self, request):
        serializer = OrderSerizlizer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            send_order.delay()

            return Response(
                data={
                    'detail': 'Order successfully created.'
                }, status=status.HTTP_201_CREATED
            )
