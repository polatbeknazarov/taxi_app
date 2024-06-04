from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.db.models import F

from orders.models import Order
from orders.serializers import OrderSerializer


User = get_user_model()


class LastPassengersAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        orders = Order.objects.filter(driver=user.id, created_at__gt=F(
            'driver__joined_at')).order_by('-created_at')
        serializer = OrderSerializer(orders, many=True)

        return Response(serializer.data)
