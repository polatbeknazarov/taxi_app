from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from users.serializers import CustomUserSerializer


class RegisterAPIView(APIView):
    permission_classes = [AllowAny,]

    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()

            return Response(
                data={'detail': 'User registered successfully.'},
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                data={'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
