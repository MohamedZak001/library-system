from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.gis.geos import Point
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import RegisterSerializer, UserSerializer, LoginSerializer, LogoutSerializer, PasswordRestSerializer, PasswordRestConfirmSerializer

User = get_user_model()


class RegisterAPIView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        payload = request.data
        serialized_data = self.get_serializer(payload).data
        password = serialized_data.pop("password")
        latitude = serialized_data.pop("latitude")
        longitude = serialized_data.pop("longitude")
        location = None
        if latitude and longitude:
            location = Point(longitude, latitude)
        user = User.objects.create_user(
            **serialized_data,
            password=password,
            location=location
        )
        return Response(UserSerializer(instance=user).data, status=status.HTTP_201_CREATED)


class LoginAPIView(TokenObtainPairView):
    serializer_class = LoginSerializer


class LogoutAPIView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LogoutSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh = serializer.validated_data.get("refresh")
        try:
            token = RefreshToken(refresh)
            token.blacklist()
            return Response({"details": "Logged out successfully."}, status=status.HTTP_205_RESET_CONTENT)
        except TokenError:
            return Response({"details": "Invalid refresh token."}, status=status.HTTP_400_BAD_REQUEST)


class PasswordRestAPIView(generics.CreateAPIView):

    serializer_class = PasswordRestSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get("email")
        user = User.objects.get(email=email)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        return Response({
            "uid": uid,
            "token": token,
        }, status=status.HTTP_200_OK)


class PasswordRestConfirmAPIView(generics.CreateAPIView):

    serializer_class = PasswordRestConfirmSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data.get("user")
        password = serializer.validated_data.get("password")
        user.set_password(password)
        user.save()
        return Response({"message": "Your password has been reset successfully."}, status=status.HTTP_200_OK)
