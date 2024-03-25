from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from users.serializers import UserLoginSerializer, UserRegisterSerializer
from users.utils import get_auth_for_user


class LoginAPIView(APIView):
    permission_classes = [AllowAny,]

    @csrf_exempt
    def post(self, request):
        '''
        Authenticate user and generate token.
        '''
        serializer = UserLoginSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            username = request.data.get('username')
            password = request.data.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                user_data = get_auth_for_user(user)

                return Response(
                    data=user_data,
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    data={'detail': 'Invalid username or password.'},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
        else:
            return Response(
                data={'detail': 'Invalid data provided.'},
                status=status.HTTP_400_BAD_REQUEST,
            )


class RegisterAPIView(APIView):
    permission_classes = [AllowAny,]

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)

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
