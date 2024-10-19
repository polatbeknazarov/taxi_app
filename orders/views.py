from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model

from orders.models import Order
from orders.serializers import OrderSerializer
from line.models import Line


User = get_user_model()


class LastPassengersAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        driver = Line.objects.get(driver=user)
        orders = Order.objects.filter(
            driver=driver,
            updated_at__gt=driver.joined_at,
        ).order_by("-created_at", "id")
        serializer = OrderSerializer(orders, many=True)

        return Response(serializer.data)
